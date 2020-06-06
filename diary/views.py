from django.shortcuts import render, redirect

from django.views import View

from diary.models import Hero


class StartView(View):
    def get(self, request):
        heroes = Hero.objects.All()
        return render('index.html', context={'heroes': heroes})


class CreateHero(View):
    def get(self, request):
        return redirect('index')
