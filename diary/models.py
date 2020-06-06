from django.db import models

LIST_OF_ITEMS = [
    'Soap',
    'Branch',
    'Rock',
    'Rope',
    'Glasses',
    'Skin',
    'Head & Shoulders',
    'Bat',
]


LIST_OF_MONSTER = [
    'Dragon',
    'ButterFly',
    'Village Idiot',
    'Rabbit',
    'Wolf',
    'Big Bad Wolf',
    'Small Bad Wolf',
]


class Hero(models.Model):
    name = models.CharField(max_length=255)
    experience = models.IntegerField(default=0)
    strength = models.IntegerField()
    agility = models.IntegerField()
    vitality = models.IntegerField()
    wisdom = models.IntegerField()
    charisma = models.IntegerField()
    gold = models.IntegerField()


class Item(models.Model):
    QUALITY = (
        (1, 'normal'),
        (4, 'rare'),
        (16, 'unique'),
        (64, 'legendary'),
    )

    name = models.CharField(max_length=255)
    quality = models.IntegerField(choices=QUALITY)
    owner = models.ForeignKey(Hero, on_delete=models.CASCADE)


class Equipment(models.Model):
    PREFIXES = (
        (1, 'Awful'),
        (4, 'Poor'),
        (16, 'Normal'),
        (64, 'Good'),
        (256, 'Excellent'),
        (1024, 'Legendary'),
    )
    prefix = models.IntegerField(choices=PREFIXES)
    SUFFIX = (
        (1, 'of Child'),
        (4, 'of Mouse'),
        (16, 'of Minotaur'),
        (64, 'of Dragon'),
        (256, 'of God'),
        (1024, 'of Hamster'),
    )
    suffix = models.CharField(max_length=255)
    modifier = models.IntegerField()
    owner = models.ForeignKey(Hero, on_delete=models.CASCADE)
    SLOTS = (
        (1, 'Helmet'),
        (2, 'Shoulders'),
        (3, 'Armor'),
        (4, 'Gloves'),
        (5, 'Legs'),
        (6, 'Shoes'),
        (7, 'Sword'),
        (8, 'Shield'),
        (9, 'Cape'),
    )
    slot = models.IntegerField(choices=SLOTS)
