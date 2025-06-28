from typing import Optional, TYPE_CHECKING, Dict

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from apps.bot.models import ServerConfInfo


class ServerConfInfoEntity(BaseModel):
    pk: int
    product_id: int
    name: Optional[str]
    address: Optional[str]
    end_point: Optional[str]
    publickey: Optional[str]
    privatekey: Optional[str]
    is_active: bool
    is_test: bool
    queue_name: Optional[str]
    extra_conf: Dict[str, int] = Field(default_factory=dict)

    @classmethod
    def from_model(cls, instance: 'ServerConfInfo') -> 'ServerConfInfoEntity':
        return cls(
            pk=instance.pk,
            product_id=instance.product_id,
            name=instance.name,
            address=instance.address,
            end_point=instance.end_point,
            publickey=instance.publickey,
            privatekey=instance.privatekey,
            is_active=instance.is_active,
            is_test=instance.is_test,
            queue_name=instance.queue_name,
            extra_conf=instance.extra_conf,
        )
