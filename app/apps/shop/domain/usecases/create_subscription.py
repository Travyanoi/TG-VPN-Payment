import datetime

from apps.core.domain.usecases.base import BaseUseCase, BaseUseCaseOutputDTO, BaseUseCaseInputDTO
from apps.shop.repositories.subscription import SubscriptionRepository


class CreateSubscriptionInputDTO(BaseUseCaseInputDTO):
    user_id: str
    server_id: int
    duration_days: datetime


class CreateSubscriptionOutputDTO(BaseUseCaseOutputDTO):
    subscription_id: int


class CreateSubscriptionUseCase(BaseUseCase[CreateSubscriptionInputDTO, CreateSubscriptionOutputDTO]):
    def __init__(self):
        super().__init__()
        self.subscription = SubscriptionRepository()

    def _execute(self, input_dto: CreateSubscriptionInputDTO) -> CreateSubscriptionOutputDTO:

        start_date = datetime.datetime.now(tz=datetime.UTC)
        expired_date = start_date + datetime.timedelta(days=input_dto.duration_days)

        sub = self.subscription.create(
            user_id=input_dto.user_id,
            server_id=input_dto.server_id,
            start_date=start_date,
            expired_date=expired_date,
        )

        return CreateSubscriptionOutputDTO(
            subscription_id=sub.pk
        )
