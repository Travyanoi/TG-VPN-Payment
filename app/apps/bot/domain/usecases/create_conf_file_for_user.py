from io import BytesIO
from typing import Optional, TYPE_CHECKING

from apps.bot.repositories.server_conf_info import ServerConfInfoRepository
from apps.core.domain.usecases.base import BaseUseCaseInputDTO, BaseUseCase

if TYPE_CHECKING:
    from apps.bot.models.info_for_conf_file import InfoForConfFile


class InfoForConfFileInputDTO(BaseUseCaseInputDTO):
    user_id: str
    server_id: int
    address: Optional[str]
    publickey: str
    privatekey: str
    enable: bool


# TODO OutputDTO with BytesIO
class CreateConfigFileForUserUseCase(BaseUseCase[InfoForConfFileInputDTO, None]):
    def _execute(self, input_dto: InfoForConfFileInputDTO):
        server = ServerConfInfoRepository().get_by_id(pk=input_dto.server_id)

        file = BytesIO()
        file.write(
            "[Interface]\n"
            f"Privatekey = {input_dto.privatekey}\n"
            f"Address = {input_dto.address}\n"
            "DNS = 8.8.8.8\n\n"
            "[Peer]\n"
            f"PublicKey = {server.publickey}\n"
            "AllowedIPs = 0.0.0.0/0\n"
            f"Endpoint = {server.end_point}\n"
            "PersistentKeepalive = 20".encode('utf-8')
        )
        file.close()

        return file
