from apps.core.domain.usecases.base import BaseUseCase, BaseUseCaseOutputDTO, BaseUseCaseInputDTO
from apps.shop.domain.usecases.calculate_price import CalculateProductPriceUseCase, PriceDurationInputDTO
from apps.shop.repositories.price_duration import PriceDurationRepository
from apps.shop.repositories.product import ProductRepository
from apps.shop.repositories.purchase import PurchaseRepository


class CreatePurchaseInputDTO(BaseUseCaseInputDTO):
    user_id: str
    price_duration_id: int
    product_id: int


class CreatePurchaseOutputDTO(BaseUseCaseOutputDTO):
    purchase_id: int


class CreatePurchaseUseCase(BaseUseCase[CreatePurchaseInputDTO, CreatePurchaseOutputDTO]):
    def __init__(self):
        super().__init__()
        self.price_duration = PriceDurationRepository()
        self.purchase = PurchaseRepository()
        self.product = ProductRepository()

    def _execute(self, input_dto: CreatePurchaseInputDTO) -> CreatePurchaseOutputDTO:
        price_duration = self.price_duration.get_by_id(input_dto.price_duration_id)

        price_duration_dto = PriceDurationInputDTO.from_entity(price_duration)
        amount = CalculateProductPriceUseCase().execute(price_duration_dto)
        product = self.product.get_by_id(input_dto.product_id)

        discount = f"скидка {amount.discount_percent}" if amount.discount_percent else "без скидки"

        description = f"Покупка для {input_dto.user_id}, сервер {product.name}, сумма {amount.total_price}, {discount}"

        purchase = self.purchase.create(
            user_id=input_dto.user_id,
            price_duration_id=price_duration.pk,
            product_id=input_dto.product_id,
            currency=price_duration.currency,
            amount=amount.total_price,
            buy_descr=description
        )

        return CreatePurchaseOutputDTO(
            purchase_id=purchase.pk
        )
