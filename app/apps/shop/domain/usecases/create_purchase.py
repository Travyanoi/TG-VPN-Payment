from apps.bot.repositories.server_conf_info import ServerConfInfoRepository
from apps.core.domain.usecases.base import BaseUseCase, BaseUseCaseOutputDTO, BaseUseCaseInputDTO
from apps.shop.domain.usecases.calculate_price import CalculateProductPriceUseCase, PriceDurationInputDTO
from apps.shop.repositories.price_duration import PriceDurationRepository
from apps.shop.repositories.purchase import PurchaseRepository


class CreatePurchaseInputDTO(BaseUseCaseInputDTO):
    user_id: str
    price_duration_id: int
    server_id: int


class CreatePurchaseOutputDTO(BaseUseCaseOutputDTO):
    purchase_id: int


class CreatePurchaseUseCase(BaseUseCase[CreatePurchaseInputDTO, CreatePurchaseOutputDTO]):
    def __init__(self):
        super().__init__()
        self.price_duration = PriceDurationRepository()
        self.purchase = PurchaseRepository()
        self.server = ServerConfInfoRepository()

    def _execute(self, input_dto: CreatePurchaseInputDTO) -> CreatePurchaseOutputDTO:
        price_duration = self.price_duration.get_by_id(input_dto.price_duration_id)

        price_duration_dto = PriceDurationInputDTO.from_entity(price_duration)
        amount = CalculateProductPriceUseCase().execute(price_duration_dto)
        server = self.server.get_by_id(input_dto.product_id)

        discount = f"скидка {amount.discount_percent}" if amount.discount_percent else "без скидки"

        description = f"Покупка для {input_dto.user_id}, сервер {server.name}, сумма {amount.total_price}, {discount}"

        purchase = self.purchase.create(
            user_id=input_dto.user_id,
            price_duration_id=price_duration.pk,
            server_id=input_dto.server_id,
            currency=price_duration.currency,
            amount=amount.total_price,
            buy_descr=description
        )

        return CreatePurchaseOutputDTO(
            purchase_id=purchase.pk
        )
