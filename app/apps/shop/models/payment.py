from django.db import models

from apps.shop.models.purchase import Purchase


class Payment(models.Model):
    class StatusCode(models.IntegerChoices):
        refund = -1, 'Возвращён'
        init = 1, 'Создан'
        success = 2, 'Оплачен'
        error = 6, 'Ошибка'

    user = models.ForeignKey("bot.UserInfo", related_name="payments", on_delete=models.CASCADE, null=True)

    purchase = models.ForeignKey(Purchase, verbose_name="Покупка", related_name="payments", on_delete=models.CASCADE)
    pay_system = models.ForeignKey(
        "shop.PaySystem",
        verbose_name="Платежные системы",
        related_name="payments",
        on_delete=models.DO_NOTHING,
        null=True
    )

    status_code = models.IntegerField(
        "Код статуса",
        choices=StatusCode.choices,
        default=StatusCode.init,
        db_index=True
    )
    error_detail = models.JSONField("Детали ошибки", null=True, max_length=2048)
    ip = models.GenericIPAddressField(null=True)
    internal_id = models.CharField(
        "Внутренний ID платежа платежной системы",
        max_length=60,
        null=True,
        db_index=True
    )

    create_date = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'status_code']),
        ]
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
