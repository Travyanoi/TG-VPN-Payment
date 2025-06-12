from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from apps.bot.models import InfoForConfFile


class InfoForConfFileEntity(BaseModel):
    pk: int
    user_id: str
    server_id: int
    address: Optional[str]
    publickey: str
    privatekey: str
    enable: bool

    @classmethod
    def from_model(cls, instance: 'InfoForConfFile') -> 'InfoForConfFileEntity':
        return cls(
            pk=instance.pk,
            user_id=instance.user.chat_id,
            server_id=instance.server.pk,
            address=instance.address,
            publickey=instance.publickey,
            privatekey=instance.privatekey,
            enable=instance.enable
        )
