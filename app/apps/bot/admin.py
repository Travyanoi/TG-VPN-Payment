from django.contrib import admin

from apps.bot.models import UserInfo, ServerConfInfo


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    pass

@admin.register(ServerConfInfo)
class ServerConfAdmin(admin.ModelAdmin):
    pass

# Register your models here.
