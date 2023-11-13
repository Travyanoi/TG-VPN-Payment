from django.contrib import admin
from django.urls import path

from apps.bot.views import webhook

urlpatterns = [
    path('webhook/', webhook),
]