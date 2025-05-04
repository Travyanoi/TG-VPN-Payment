from django.db import models


class Subscription(models.Model):
    user = models.ForeignKey("bot.UserInfo", related_name="subscriptions", on_delete=models.CASCADE, null=True)
    product = models.ForeignKey("shop.Product", related_name="subscriptions", on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True)
    expired_date = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Активная подписка"
        verbose_name_plural = "Активные подписки"
        unique_together = ["user", "product"]
        indexes = [
            models.Index(fields=['id', 'expired_date']),
            models.Index(fields=['user', 'product']),
        ]
