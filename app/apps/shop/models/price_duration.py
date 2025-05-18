from django.db import models


class PriceDuration(models.Model):
    product = models.ForeignKey("shop.Product", related_name="prices", on_delete=models.CASCADE)
    duration = models.PositiveIntegerField("Длительность в днях", default=30)
    currency = models.CharField("Валюта", max_length=3, default='RUB', db_index=True)
    discount = models.ForeignKey("shop.Discount", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Цена/длительность"
        verbose_name_plural = "Цены/длительности"
