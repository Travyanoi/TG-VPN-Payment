from typing import Optional, TYPE_CHECKING

from apps.core.domain.usecases.base import BaseUseCaseInputDTO

if TYPE_CHECKING:
    from apps.bot.models.server_conf_info import ServerConfInfo


class ServerConfInfoInputDTO(BaseUseCaseInputDTO):
    address: Optional[str]
    end_point: Optional[str]
    publickey: Optional[str]
    privatekey: Optional[str]

    @classmethod
    def from_model(cls, instance: 'ServerConfInfo') -> 'ServerConfInfoInputDTO':
        return cls(
            address=instance.address,
            end_point=instance.end_point,
            publickey=instance.publickey,
            privatekey=instance.privatekey
        )
