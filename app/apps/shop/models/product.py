from django.db import models


class Product(models.Model):
    name = models.CharField("Название", max_length=100, null=True, blank=True)
    description = models.CharField("Описание", max_length=200, null=True, blank=True)
    is_active = models.BooleanField("Доступен для покупки", default=True)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
