from django.db import models


class ProductServerTariff(models.Model):
    product = models.ForeignKey("shop.Product", on_delete=models.CASCADE)
    server = models.ForeignKey("bot.ServerConfInfo", on_delete=models.CASCADE)
    price_duration = models.ForeignKey("shop.PriceDuration", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("product", "server", "price_duration")
        verbose_name = "Связь продукта, сервера и тарифа"
        verbose_name_plural = "Связи продукта, сервера и тарифа"

    def __str__(self):
        return f"{self.product} ↔ {self.server} @ {self.price_duration.duration}d"
