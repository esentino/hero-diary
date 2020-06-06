from django.shortcuts import render, redirect

from django.views import View

from diary.models import Hero


class StartView(View):
    def get(self):
        heroes = Hero.objects.All()
        return render('index.html', context={'heroes': heroes})


class CreateHero(View):
    def get(self):
        return redirect('index')
