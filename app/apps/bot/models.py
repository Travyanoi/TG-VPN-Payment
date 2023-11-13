from django.db import models


class UserInfo(models.Model):
    chat_id = models.CharField(max_length=64, primary_key=True)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32, null=True)
    username = models.CharField(max_length=32, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.chat_id


class InfoForConfFile(models.Model):
    chat_id = models.OneToOneField(UserInfo, on_delete=models.CASCADE, primary_key=True)
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
        return self.chat_id_id


class ServerConfInfo(models.Model):
    address = models.CharField(max_length=20, null=True)
    end_point = models.CharField(max_length=20, null=True)
    publickey = models.CharField(max_length=44, null=True)
    privatekey = models.CharField(max_length=44, null=True)

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'

    def __str__(self):
        return f'ServerConfig {self.pk}'

