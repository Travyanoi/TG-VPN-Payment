from django.db import models
from decimal import Decimal


class Discount(models.Model):
    name = models.CharField("Название акции", max_length=100)
    percent = models.PositiveIntegerField("Скидка в процентах", help_text="Например, 20 для 20%")
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField("Начало действия", null=True, blank=True)
    ends_at = models.DateTimeField("Конец действия", null=True, blank=True)

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"
