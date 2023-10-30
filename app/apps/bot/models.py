from django.db import models
from django.db.models import CharField, DateTimeField, BooleanField


class UserInfo(models.Model):
    chat_id = CharField(max_length=64, primary_key=True)
    first_name = CharField(max_length=32)
    last_name = CharField(max_length=32, null=True)
    username = CharField(max_length=32, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.chat_id


class InfoForConfFile(models.Model):
    chat_id = CharField(max_length=64, primary_key=True)
    first_name = CharField(max_length=32)
    publickey = CharField(max_length=44)
    privatekey = CharField(max_length=44)
    created_at = DateTimeField(default='')
    expires_at = DateTimeField(default='')
    enable = BooleanField(default=False)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'

    def __str__(self):
        return self.chat_id
