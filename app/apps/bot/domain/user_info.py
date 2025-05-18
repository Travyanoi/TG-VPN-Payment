from pydantic import BaseModel

from apps.bot.models import UserInfo


class UserInfoEntity(BaseModel):
    chat_id: str
    first_name: str
    last_name: str
    username: str

    @classmethod
    def from_model(cls, instance: 'UserInfo') -> 'UserInfoEntity':
        return cls(
            chat_id=instance.chat_id,
            first_name=instance.first_name,
            last_name=instance.last_name,
            username=instance.username
        )
