from random import randint

from django.shortcuts import render, redirect

from django.views import View

from diary.models import Hero
from faker import Faker
fake = Faker(['pl_PL', 'sv_SE', 'hi_IN'])

class StartView(View):
    def get(self, request):
        heroes = Hero.objects.all()
        return render(request, 'index.html', context={'heroes': heroes})


class CreateHero(View):
    def get(self, request):
        heroes = Hero.objects.create(
            name=fake.name(),
            strength=randint(3, 18),
            agility=randint(3, 18),
            vitality=randint(3, 18),
            wisdom=randint(3, 18),
            charisma=randint(3, 18),
            gold=0,
        )
        return redirect('index')
