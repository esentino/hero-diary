from django.contrib import admin
from django.urls import path

from diary.views import StartView, CreateHero, CheckHero

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_hero', CreateHero.as_view(), name='create-hero'),
    path('view_hero/<int:hero_id>', CheckHero.as_view, name='hero'),
    path('', StartView.as_view(), name='index'),
]
