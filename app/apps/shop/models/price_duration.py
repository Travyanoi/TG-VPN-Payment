from django.db import models


class PriceDuration(models.Model):
    currency = models.CharField("Валюта", max_length=3, default='RUB', db_index=True)
    product = models.ForeignKey("shop.Product", related_name="prices", on_delete=models.CASCADE)
    # TODO цена должна быть у продукта, а тут должен быть подсчет суммы за конкретное количество месяцев подписки
    amount = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    name = models.CharField("Название для клавиатуры", max_length=20, null=False, default='-')
    duration = models.IntegerField(
        "Длительность",
        help_text="Длительность в днях. В формате 1,3,6,12 (месяцев)",
        default='1'
    )

    class Meta:
        verbose_name = "Цена/длительность"
        verbose_name_plural = "Цены/длительности"
