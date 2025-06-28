from typing import Optional, TYPE_CHECKING

from apps.core.domain.usecases.base import BaseUseCaseInputDTO

if TYPE_CHECKING:
    from apps.bot.models.user_info import UserInfo


class UserInfoInputDTO(BaseUseCaseInputDTO):
    chat_id: str
    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    @classmethod
    def from_model(cls, instance: 'UserInfo') -> 'UserInfoInputDTO':
        return cls(
            chat_id=instance.chat_id,
            first_name=instance.first_name,
            last_name=instance.last_name,
            username=instance.username
        )
