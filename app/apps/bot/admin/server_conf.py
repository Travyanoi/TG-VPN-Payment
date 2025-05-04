from django.contrib import admin

from apps.bot.models import ServerConfInfo


@admin.register(ServerConfInfo)
class ServerConfAdmin(admin.ModelAdmin):
    pass
