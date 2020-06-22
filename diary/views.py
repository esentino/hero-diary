from datetime import datetime, timedelta, timezone
from random import choice, randint
from types import FunctionType
from typing import Dict

from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from faker import Faker

from diary import consts, models

fake = Faker(["pl_PL", "sv_SE", "hi_IN"])


class StartView(View):
    def get(self, request):
        heroes = models.Hero.objects.all()
        return render(request, "index.html", context={"heroes": heroes})


class CreateHero(View):
    def get(self, request):
        models.Hero.objects.create(
            name=fake.name(),
            strength=randint(3, 18),
            agility=randint(3, 18),
            vitality=randint(3, 18),
            wisdom=randint(3, 18),
            charisma=randint(3, 18),
            gold=0,
            last_action=datetime.now(),
        )
        return redirect("index")


class Action:
    def __init__(self, action_type: consts.ActionType):
        self.action_type = action_type

    @property
    def time(self):
        return consts.ACTION_SPEED.get(self.action_type, 0)


class Diary:
    MAX_ACTION_COUNT = 100

    def __init__(self, hero: models.Hero):
        self._hero = hero
        self.messages = []

    def process_story(self):
        counter = 0
        while self.can_do_next_action() and counter < self.MAX_ACTION_COUNT:
            action = self.predict_action()
            self.make_action(action)
            counter += 1
        self._hero.save()  # Save hero only one

    def can_do_next_action(self):
        action = self.predict_action()
        timedelta_from_last_action = datetime.now(timezone.utc) - self._hero.last_action
        return timedelta(seconds=action.time) < timedelta_from_last_action

    def predict_action(self) -> Action:
        if self._hero.location == consts.LOCATION_TOWN:
            return self.predict_action_in_town()
        if self._hero.location == consts.LOCATION_ROAD_KILLING_FIELDS:
            return Action(consts.ActionType.KILLING_FIELD)
        if self._hero.location == consts.LOCATION_KILLING_FIELDS:
            return self.predict_action_in_killing_fields()
        return Action(consts.ActionType.TOWN)

    def predict_action_in_killing_fields(self) -> Action:
        if self._hero.items.count() < self._hero.capacity:
            return Action(consts.ActionType.KILL_MONSTER)
        return Action(consts.ActionType.TRAVEL_TO_TOWN)

    def predict_action_in_town(self) -> Action:
        if self._hero.items.count() > 0:
            return Action(consts.ActionType.SELL_ITEM)
        if self.can_buy_equipment():
            return Action(consts.ActionType.BUY_EQUIPMENT)
        return Action(consts.ActionType.TRAVEL_TO_KILLING_FIELD)

    def can_buy_equipment(self) -> bool:
        price_for_slot_upgrade = self.get_price_for_upgrade()
        for key, value in price_for_slot_upgrade.items():
            if value <= self._hero.gold:
                return True
        return False

    def get_price_for_upgrade(self):
        equipments = self._hero.equipments.all()
        price_for_slot_upgrade = {k: 1 for k, _ in models.Equipment.SLOTS}
        for equipment in equipments:
            price_for_slot_upgrade[equipment.slot] = equipment.price_next
        return price_for_slot_upgrade

    def make_action(self, action: Action):
        actions: Dict[consts.ActionType, FunctionType] = {
            consts.ActionType.SELL_ITEM: self.sell_item,
            consts.ActionType.BUY_EQUIPMENT: self.buy_equipments,
            consts.ActionType.TRAVEL_TO_KILLING_FIELD: self.travel_to_killing_field,
            consts.ActionType.KILLING_FIELD: self.killing_field,
            consts.ActionType.KILL_MONSTER: self.action_kill_monster,
            consts.ActionType.TRAVEL_TO_TOWN: self.action_travel_to_town,
            consts.ActionType.TOWN: self.action_in_town,
        }

        action_method = actions.get(action.action_type)
        if action_method:
            action_method(action)

    def buy_equipments(self, action: Action):
        for slot, value in self.get_price_for_upgrade().items():
            if value <= self._hero.gold:
                equipment = self.buy_equipment(slot, value)
                self._hero.last_action += timedelta(seconds=action.time)
                self.messages.append(f"{self._hero.last_action} - buy equipment {equipment}")

    def action_in_town(self, action: Action):
        self._hero.location = consts.LOCATION_TOWN
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(f"{self._hero.last_action} - in  Town")

    def action_travel_to_town(self, action: Action):
        self._hero.location = consts.LOCATION_ROAD_TOWN
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(f"{self._hero.last_action} - travel to  Town")

    def action_kill_monster(self, action: Action):
        self._hero.experience += +randint(3, 5)
        self._hero.last_action += timedelta(seconds=action.time)
        monster = choice(consts.LIST_OF_MONSTER)
        self.messages.append(f"{self._hero.last_action} - kill {monster}")
        if randint(1, 100) > 99:
            attribute = self._hero.add_random_attribute()
            self.messages.append(f"{self._hero.last_action} - get attribute {attribute}")
        item = self.generate_item()
        self.messages.append(f"{self._hero.last_action} - get {item}")

    def killing_field(self, action: Action):
        self._hero.location = consts.LOCATION_KILLING_FIELDS
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(f"{self._hero.last_action} - in  KILLING_FIEL")

    def travel_to_killing_field(self, action: Action):
        self._hero.location = consts.LOCATION_ROAD_KILLING_FIELDS
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(f"{self._hero.last_action} - travel to  KILLING_FIEL")

    def sell_item(self, action: Action):
        item = self._hero.items.first()
        self._hero.gold += item.price
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(
            f"{self._hero.last_action} - sell item {item} - price: {item.price} - gold {self._hero.gold}"
        )
        item.delete()

    def buy_equipment(self, slot: int, value: int) -> models.Item:
        self._hero.gold -= value
        equipment = self._hero.equipments.filter(slot=slot).first()
        if equipment:
            if equipment.prefix > equipment.suffix:
                equipment.suffix *= 4
            else:
                equipment.prefix *= 4
            equipment.save()
        else:
            equipment = models.Equipment.objects.create(prefix=1, suffix=1, slot=slot, owner=self._hero, modifier=0)
        return equipment

    def generate_item(self) -> models.Item:
        roll = randint(1, 64)
        if roll == 64:
            quality = 64
        elif roll >= 64 - 4:
            quality = 16
        elif roll >= 64 - 16:
            quality = 4
        else:
            quality = 1
        name = choice(consts.LIST_OF_ITEMS)
        return models.Item.objects.create(quality=quality, name=name, owner=self._hero)


class CheckHero(View):
    def get(self, request, hero_id):
        hero = get_object_or_404(models.Hero, pk=hero_id)
        diary = Diary(hero)
        diary.process_story()
        return render(request, "hero_page.html", context={"hero": hero, "diary": diary})
