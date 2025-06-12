from datetime import datetime
from typing import Optional

from wireguard_tools import WireguardKey

from apps.bot.domain.info_for_conf_file import InfoForConfFileEntity
from apps.bot.repositories.info_for_conf_file import InfoForConfFileRepository
from apps.bot.repositories.user_info import UserInfoRepository
from apps.core.domain.usecases.base import BaseUseCaseInputDTO, BaseUseCase, BaseUseCaseOutputDTO
from apps.shop.domain.subscription import SubscriptionEntity


class SubscriptionInputDTO(BaseUseCaseInputDTO):
    pk: int
    user_id: str
    product_tariff_id: int
    created_date: datetime
    start_date: datetime
    expired_date: datetime

    @classmethod
    def from_entity(cls, entity: 'SubscriptionEntity'):
        return SubscriptionInputDTO(
            pk=entity.pk,
            user_id=entity.user_id,
            product_tariff_id=entity.product_tariff_id,
            created_date=entity.created_date,
            start_date=entity.start_date,
            expired_date=entity.expired_date,
        )


class InfoForConfFileOutputDTO(BaseUseCaseOutputDTO):
    pk: int
    user_id: str
    server_id: int
    address: Optional[str]
    publickey: str
    privatekey: str
    enable: bool

    @classmethod
    def from_entity(cls, entity: 'InfoForConfFileEntity'):
        return InfoForConfFileOutputDTO(
            pk=entity.pk,
            user_id=entity.user_id,
            server_id=entity.server_id,
            address=entity.address,
            publickey=entity.publickey,
            privatekey=entity.privatekey,
            enable=entity.enable,
        )


class GetOrCreateConfFileUseCase(BaseUseCase[SubscriptionInputDTO, InfoForConfFileOutputDTO]):
    def __init__(self):
        super().__init__()
        self.product_tariff_repo = ProductServerTariffRepository()
        self.conf_file_repo = InfoForConfFileRepository()
        self.user_repo = UserInfoRepository()

    def _execute(self, input_dto: SubscriptionInputDTO) -> InfoForConfFileOutputDTO:
        product_tariff = self.product_tariff_repo.get_by_id(input_dto.product_tariff_id)
        conf_file = self.conf_file_repo.get_by_user_server_id(input_dto.user_id, product_tariff.server_id)

        if conf_file:
            return InfoForConfFileOutputDTO.from_entity(conf_file)

        private_key = WireguardKey.generate()
        public_key = private_key.public_key()

        private_key = f"{private_key.urlsafe}="
        public_key = f"{public_key.urlsafe}="

        last_octet = self.conf_file_repo.get_by_server_id(product_tariff.server_id)
        address_for_user = f"10.0.0.{len(last_octet) + 2}/32"

        entity = self.conf_file_repo.create(
            user_id=input_dto.user_id,
            server_id=product_tariff.server_id,
            address=address_for_user,
            publickey=public_key,
            privatekey=private_key,
            enable=True,
        )

        return InfoForConfFileOutputDTO.from_entity(entity)
