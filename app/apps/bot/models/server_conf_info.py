from django.db import models


class ServerConfInfo(models.Model):
    name = models.CharField(max_length=20, null=True)
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE)
    address = models.CharField(max_length=20, null=True, blank=True)
    end_point = models.CharField(max_length=20, null=True, blank=True)
    publickey = models.CharField(max_length=44, null=True, blank=True)
    privatekey = models.CharField(max_length=44, null=True, blank=True)
    is_active = models.BooleanField("Активна?", default=True)
    is_test = models.BooleanField("Является тестовой?", default=False)

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'

    def __str__(self):
        return f'Server {self.address or self.pk}'
