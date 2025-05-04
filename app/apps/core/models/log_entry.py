from django.db import models


class LogEntry(models.Model):
    class LogLevel(models.IntegerChoices):
        DEBUG = -1, 'DEBUG'
        INFO = 0, 'INFO'
        WARNING = 1, 'WARNING'
        ERROR = 2, 'ERROR'
        CRITICAL = 3, 'CRITICAL'

    user = models.ForeignKey("bot.UserInfo", related_name="logs", on_delete=models.CASCADE, null=True)
    date = models.DateTimeField("Дата", auto_now_add=True, db_index=True)
    text = models.TextField("Текст", null=True, blank=True)
    detail = models.TextField("Текст", null=True, blank=True)
    level = models.IntegerField("Уровень", choices=LogLevel.choices, default=0, db_index=True)

    class Meta:
        verbose_name = "Лог"
        verbose_name_plural = "Логи"
        indexes = [
            models.Index(fields=['id', 'date']),
        ]
