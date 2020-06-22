from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from random import randint, choice
from types import FunctionType
from typing import Dict

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from faker import Faker

from diary.models import (
    Hero,
    LOCATION_TOWN,
    LOCATION_ROAD_KILLING_FIELDS,
    LOCATION_KILLING_FIELDS,
    LOCATION_ROAD_TOWN,
    Equipment,
    LIST_OF_MONSTER,
    Item,
    LIST_OF_ITEMS,
)

fake = Faker(["pl_PL", "sv_SE", "hi_IN"])


class StartView(View):
    def get(self, request):
        heroes = Hero.objects.all()
        return render(request, "index.html", context={"heroes": heroes})


class CreateHero(View):
    def get(self, request):
        Hero.objects.create(
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


class ActionType(Enum):
    SELL_ITEM = auto()
    BUY_EQUIPMENT = auto()
    TRAVEL_TO_KILLING_FIELD = auto()
    KILLING_FIELD = auto()
    KILL_MONSTER = auto()
    TRAVEL_TO_TOWN = auto()
    TOWN = auto()


ACTION_SPEED = {
    ActionType.SELL_ITEM: 1,
    ActionType.BUY_EQUIPMENT: 1,
    ActionType.TRAVEL_TO_KILLING_FIELD: 1,
    ActionType.KILLING_FIELD: 60,
    ActionType.KILL_MONSTER: 5,
    ActionType.TRAVEL_TO_TOWN: 1,
    ActionType.TOWN: 60,
}


class Action:
    def __init__(self, action_type: ActionType):
        self.action_type = action_type

    @property
    def time(self):
        return ACTION_SPEED.get(self.action_type, 0)


class Diary:
    MAX_ACTION_COUNT = 100

    def __init__(self, hero: Hero):
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
        return timedelta(seconds=action.time) < datetime.now(timezone.utc) - self._hero.last_action

    def predict_action(self):
        if self._hero.location == LOCATION_TOWN:
            return self.predict_action_in_town()
        if self._hero.location == LOCATION_ROAD_KILLING_FIELDS:
            return Action(ActionType.KILLING_FIELD)
        if self._hero.location == LOCATION_KILLING_FIELDS:
            return self.predict_action_in_killing_fields()
        return Action(ActionType.TOWN)

    def predict_action_in_killing_fields(self):
        if self._hero.items.count() < self._hero.capacity:
            return Action(ActionType.KILL_MONSTER)
        return Action(ActionType.TRAVEL_TO_TOWN)

    def predict_action_in_town(self):
        if self._hero.items.count() > 0:
            return Action(ActionType.SELL_ITEM)
        if self.can_buy_equipment():
            return Action(ActionType.BUY_EQUIPMENT)
        return Action(ActionType.TRAVEL_TO_KILLING_FIELD)

    def can_buy_equipment(self):
        price_for_slot_upgrade = self.get_price_for_upgrade()
        for key, value in price_for_slot_upgrade.items():
            if value <= self._hero.gold:
                return True
        return False

    def get_price_for_upgrade(self):
        equipments = self._hero.equipments.all()
        price_for_slot_upgrade = {k: 1 for k, _ in Equipment.SLOTS}
        for equipment in equipments:
            price_for_slot_upgrade[equipment.slot] = equipment.price_next
        return price_for_slot_upgrade

    def make_action(self, action: Action):
        actions: Dict[ActionType, FunctionType] = {
            ActionType.SELL_ITEM: self.sell_item,
            ActionType.BUY_EQUIPMENT: self.buy_equipments,
            ActionType.TRAVEL_TO_KILLING_FIELD: self.travel_to_killing_field,
            ActionType.KILLING_FIELD: self.killing_field,
            ActionType.KILL_MONSTER: self.action_kill_monster,
            ActionType.TRAVEL_TO_TOWN: self.action_travel_to_town,
            ActionType.TOWN: self.action_in_town,
        }

        action_method = actions.get(action.action_type)
        if action_method:
            action_method(action)

    def buy_equipments(self, action):
        for slot, value in self.get_price_for_upgrade().items():
            if value <= self._hero.gold:
                equipment = self.buy_equipment(slot, value)
                self._hero.last_action += timedelta(seconds=action.time)
                self.messages.append(f"{self._hero.last_action} - buy equipment {equipment}")

    def action_in_town(self, action):
        self._hero.location = LOCATION_TOWN
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(f"{self._hero.last_action} - in  Town")

    def action_travel_to_town(self, action):
        self._hero.location = LOCATION_ROAD_TOWN
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(f"{self._hero.last_action} - travel to  Town")

    def action_kill_monster(self, action):
        self._hero.experience += +randint(3, 5)
        self._hero.last_action += timedelta(seconds=action.time)
        monster = choice(LIST_OF_MONSTER)
        self.messages.append(f"{self._hero.last_action} - kill {monster}")
        if randint(1, 100) > 99:
            attribute = self._hero.add_random_attribute()
            self.messages.append(f"{self._hero.last_action} - get attribute {attribute}")
        item = self.generate_item()
        self.messages.append(f"{self._hero.last_action} - get {item}")

    def killing_field(self, action):
        self._hero.location = LOCATION_KILLING_FIELDS
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(f"{self._hero.last_action} - in  KILLING_FIEL")

    def travel_to_killing_field(self, action):
        self._hero.location = LOCATION_ROAD_KILLING_FIELDS
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(f"{self._hero.last_action} - travel to  KILLING_FIEL")

    def sell_item(self, action):
        item = self._hero.items.first()
        self._hero.gold += item.price
        self._hero.last_action += timedelta(seconds=action.time)
        self.messages.append(
            f"{self._hero.last_action} - sell item {item} - price: {item.price} - gold {self._hero.gold}"
        )
        item.delete()

    def buy_equipment(self, slot, value):
        self._hero.gold -= value
        equipment = self._hero.equipments.filter(slot=slot).first()
        if equipment:
            if equipment.prefix > equipment.suffix:
                equipment.suffix *= 4
            else:
                equipment.prefix *= 4
            equipment.save()
        else:
            equipment = Equipment.objects.create(prefix=1, suffix=1, slot=slot, owner=self._hero, modifier=0)
        return equipment

    def generate_item(self):
        roll = randint(1, 64)
        if roll == 64:
            quality = 64
        elif roll >= 64 - 4:
            quality = 16
        elif roll >= 64 - 16:
            quality = 4
        else:
            quality = 1
        name = choice(LIST_OF_ITEMS)
        return Item.objects.create(quality=quality, name=name, owner=self._hero)


class CheckHero(View):
    def get(self, request, hero_id):
        hero = get_object_or_404(Hero, pk=hero_id)
        diary = Diary(hero)
        diary.process_story()
        return render(request, "hero_page.html", context={"hero": hero, "diary": diary})
