from io import BytesIO
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from apps.core.domain.usecases.base import BaseUseCaseInputDTO, BaseUseCase

if TYPE_CHECKING:
    from apps.bot.models.info_for_conf_file import InfoForConfFile


class InfoForConfFileInputDTO(BaseUseCaseInputDTO):
    chat_id: str
    address: Optional[str]
    first_name: str
    publickey: str
    privatekey: str
    created_at: datetime
    start_at: Optional[datetime]
    expires_at: Optional[datetime]
    enable: bool

    @classmethod
    def from_model(cls, instance: 'InfoForConfFile') -> 'InfoForConfFileInputDTO':
        return cls(
            chat_id=instance.chat_id_id,
            address=instance.address,
            first_name=instance.first_name,
            publickey=instance.publickey,
            privatekey=instance.privatekey,
            created_at=instance.created_at,
            start_at=instance.start_at,
            expires_at=instance.expires_at,
            enable=instance.enable
        )


class CreateConfigFileForUserUseCase(BaseUseCase):
    def _execute(self, input_dto: InfoForConfFileInputDTO):
        chat_id = self._user.chat_id
        db_conf_info = InfoForConfFile.objects.get(chat_id_id=chat_id)
        db_server_info: ServerConfInfo = ServerConfInfo.objects.first()

        file = BytesIO()
        file.write(
            "[Interface]\n"
            f"Privatekey = {db_conf_info.privatekey}\n"
            f"Address = {db_conf_info.address}\n"
            "DNS = 8.8.8.8\n\n"
            "[Peer]\n"
            f"PublicKey = {db_server_info.publickey}\n"
            "AllowedIPs = 0.0.0.0/0\n"
            f"Endpoint = {db_server_info.end_point}\n"
            "PersistentKeepalive = 20".encode('utf-8')
        )

        return file
