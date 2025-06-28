from django.db import models

from apps.core.models import LogEntry


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

    def log(self, text, detail=None, level=0):
        LogEntry.objects.create(
            user=self.chat_id,
            text=text,
            detail=detail,
            level=level
        )
