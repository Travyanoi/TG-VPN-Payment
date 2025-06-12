from apps.core.domain.usecases.base import BaseUseCase, BaseUseCaseOutputDTO, BaseUseCaseInputDTO
from apps.shop.repositories.payment import PaymentRepository
from apps.shop.repositories.purchase import PurchaseRepository


class CreatePaymentInputDTO(BaseUseCaseInputDTO):
    purchase_id: int
    pay_system_id: int


class CreatePaymentOutputDTO(BaseUseCaseOutputDTO):
    payment_id: int


class CreatePaymentUseCase(BaseUseCase[CreatePaymentInputDTO, CreatePaymentOutputDTO]):
    def __init__(self):
        super().__init__()
        self.purchase = PurchaseRepository()
        self.payment = PaymentRepository()

    def _execute(self, input_dto: CreatePaymentInputDTO) -> CreatePaymentOutputDTO:
        purchase = self.purchase.get_by_id(input_dto.purchase_id)

        payment_entity = self.payment.create(
            user_id=purchase.user_id,
            purchase_id=purchase.pk,
            pay_system_id=input_dto.pay_system_id,
            status_code=1,
            internal_id=purchase.token,
        )

        return CreatePaymentOutputDTO(
            payment_id=payment_entity.pk
        )
