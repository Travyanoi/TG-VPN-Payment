from django.db import models


class PaySystem(models.Model):
    name = models.CharField("Название", max_length=128, db_index=True)
    description = models.TextField("Описание", max_length=1000, null=True, blank=True)
    is_active = models.BooleanField("Активна?", default=True, db_index=True)
    is_test = models.BooleanField("Является тестовой?", default=False, db_index=True)
    class_name = models.CharField("Название класса-обработчика", max_length=128, db_index=True)
    ordering = models.PositiveIntegerField("Порядок", default=0, blank=True, null=False, db_index=True)

    def __str__(self):
        return f"[{self.id}] {self.name}"

    class Meta:
        verbose_name = "Платежная система"
        verbose_name_plural = "Платежные системы"
        ordering = ['ordering']

    def get_class(self):
        from apps.shop.pay_system import classes
        return getattr(classes, self.class_name)
