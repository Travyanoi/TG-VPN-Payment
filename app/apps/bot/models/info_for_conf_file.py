from django.db import models


class InfoForConfFile(models.Model):
    user = models.ForeignKey("bot.UserInfo", on_delete=models.CASCADE)
    server = models.ForeignKey("bot.ServerConfInfo", on_delete=models.CASCADE)
    address = models.CharField(max_length=15, null=True)
    first_name = models.CharField(max_length=32)
    publickey = models.CharField(max_length=44)
    privatekey = models.CharField(max_length=44)
    created_at = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField(null=True)
    expires_at = models.DateTimeField(null=True)
    enable = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'

    def __str__(self):
        return self.user_id
