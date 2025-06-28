from django.contrib import admin

from apps.shop.models import PaySystem


@admin.register(PaySystem)
class PaySystemAdmin(admin.ModelAdmin):
    pass
