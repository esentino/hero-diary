from django.contrib import admin
from django.urls import path

from diary.views import StartView, CreateHero

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_hero', CreateHero.as_view(), name='create-hero'),
    path('', StartView.as_view(), name='index'),
]
