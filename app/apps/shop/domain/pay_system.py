from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from apps.shop.models import PaySystem


class PaySystemEntity(BaseModel):
    pk: int
    name: str
    description: Optional[str]
    is_active: bool
    is_test: bool
    class_name: str
    ordering: int

    @classmethod
    def from_model(cls, instance: 'PaySystem') -> 'PaySystemEntity':
        return cls(
            pk=instance.pk,
            name=instance.name,
            description=instance.description,
            is_active=instance.is_active,
            is_test=instance.is_test,
            class_name=instance.class_name,
            ordering=instance.ordering,
        )
