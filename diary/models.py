import math
from random import choice

from django.db import models

from diary import consts


class Hero(models.Model):
    name = models.CharField(max_length=255)
    experience = models.IntegerField(default=0)
    strength = models.IntegerField()
    agility = models.IntegerField()
    vitality = models.IntegerField()
    wisdom = models.IntegerField()
    charisma = models.IntegerField()
    gold = models.IntegerField()
    last_action = models.DateTimeField(auto_created=True)
    LOCATION = (
        (consts.LOCATION_TOWN, "Town"),
        (consts.LOCATION_ROAD_KILLING_FIELDS, "In road to Killing fields"),
        (consts.LOCATION_KILLING_FIELDS, "Killing fields"),
        (consts.LOCATION_ROAD_TOWN, "In road to Town"),
    )
    location = models.IntegerField(choices=LOCATION, default=1)

    @property
    def capacity(self):
        return self.strength + consts.BASE_CAPACITY

    @property
    def speed_of_travel(self):
        return consts.BASE_SPEED_OF_TRAVEL + self.agility * consts.SPEED_OF_TRAVEL_MULTIPLIER

    @property
    def luck(self):
        return self.wisdom * consts.LUCK_MULTIPLIER

    @property
    def merchant_discount(self):
        return math.log2(self.charisma)

    @property
    def level(self):
        current_exp = max(self.experience, 1)
        logaritmic_level = math.log(current_exp, 8)
        return math.ceil(logaritmic_level)

    def add_random_attribute(self):
        option = choice(["strength", "agility", "vitality", "wisdom", "charisma"])
        if option == "strength":
            self.strength += +1
        if option == "agility":
            self.agility += +1
        if option == "vitality":
            self.vitality += +1
        if option == "wisdom":
            self.wisdom += +1
        if option == "charisma":
            self.charisma += +1
        return option


class Item(models.Model):
    QUALITY = (
        (1, "normal"),
        (4, "rare"),
        (16, "unique"),
        (64, "legendary"),
    )

    name = models.CharField(max_length=255)
    quality = models.IntegerField(choices=QUALITY)
    owner = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="items")

    @property
    def price(self):
        return self.owner.level * self.quality

    def __str__(self):
        return f"<{self.get_quality_display()}> {self.name}"


class Equipment(models.Model):
    PREFIXES = (
        (1, "Awful"),
        (4, "Poor"),
        (16, "Normal"),
        (64, "Good"),
        (256, "Excellent"),
        (1024, "Legendary"),
    )
    prefix = models.IntegerField(choices=PREFIXES)
    SUFFIX = (
        (1, "of Child"),
        (4, "of Mouse"),
        (16, "of Minotaur"),
        (64, "of Dragon"),
        (256, "of God"),
        (1024, "of Hamster"),
    )
    suffix = models.IntegerField(choices=SUFFIX, default=1)
    modifier = models.IntegerField()
    owner = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="equipments")
    SLOTS = (
        (1, "Helmet"),
        (2, "Shoulders"),
        (3, "Armor"),
        (4, "Gloves"),
        (5, "Legs"),
        (6, "Shoes"),
        (7, "Sword"),
        (8, "Shield"),
        (9, "Cape"),
    )
    slot = models.IntegerField(choices=SLOTS)

    @property
    def price(self):
        return self.prefix * self.suffix * self.slot

    @property
    def price_next(self):
        return self.prefix * self.suffix * self.slot * 4

    def __str__(self):
        return f"{self.get_prefix_display()} {self.get_slot_display()} {self.get_suffix_display()} {self.modifier}"
