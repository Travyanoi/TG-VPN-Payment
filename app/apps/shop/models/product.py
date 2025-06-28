from django.db import models


class Product(models.Model):
    name = models.CharField("Название", max_length=100, null=True, blank=True)
    description = models.CharField("Описание", max_length=200, null=True, blank=True)
    base_price = models.DecimalField("Базовая цена", max_digits=8, decimal_places=2)
    is_active = models.BooleanField("Доступен для покупки", default=True)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name or f"Product {self.pk}"
