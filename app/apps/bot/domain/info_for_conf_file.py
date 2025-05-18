from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from apps.bot.models import InfoForConfFile


class InfoForConfFileEntity(BaseModel):
    pk: int
    user: str
    server: int
    address: Optional[str]
    publickey: str
    privatekey: str
    enable: bool

    @classmethod
    def from_model(cls, instance: 'InfoForConfFile') -> 'InfoForConfFileEntity':
        return cls(
            pk=instance.pk,
            user=instance.user,
            server=instance.server,
            address=instance.address,
            publickey=instance.publickey,
            privatekey=instance.privatekey,
            enable=instance.enable
        )
