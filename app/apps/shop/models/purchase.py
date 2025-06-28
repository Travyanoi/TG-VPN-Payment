from django.db import models

from apps.core.utils import generate_md5_token


class Purchase(models.Model):
    user = models.ForeignKey("bot.UserInfo", related_name="purchases", on_delete=models.CASCADE)
    price_duration = models.ForeignKey(
        verbose_name="Цена/Длительность продукта",
        to="shop.PriceDuration",
        related_name="purchases",
        on_delete=models.SET_NULL,
        null=True
    )
    server = models.ForeignKey("bot.ServerConfInfo", related_name="purchases", on_delete=models.CASCADE, null=True)

    currency = models.CharField("Валюта", max_length=3, default='RUB')

    amount = models.DecimalField(
        "Итоговая сумма для оплаты картой",
        decimal_places=2,
        max_digits=8,
        default=0
    )

    created_date = models.DateTimeField("Дата создания", auto_now_add=True)

    buy_descr = models.CharField("Описание покупки", max_length=100)

    token = models.CharField("Внутренний ID", max_length=64, default=generate_md5_token, unique=True)

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
