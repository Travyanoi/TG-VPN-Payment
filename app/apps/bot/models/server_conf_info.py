from django.db import models


class ServerConfInfo(models.Model):
    product = models.ForeignKey("shop.Product", related_name="server_configs", on_delete=models.CASCADE)
    address = models.CharField(max_length=20, null=True)
    end_point = models.CharField(max_length=20, null=True)
    publickey = models.CharField(max_length=44, null=True)
    privatekey = models.CharField(max_length=44, null=True)

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'

    def __str__(self):
        return f'ServerConfig {self.pk}'
