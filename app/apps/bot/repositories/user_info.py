from typing import Optional

from apps.bot.domain.user_info import UserInfoEntity
from apps.bot.models import UserInfo
from apps.bot.repositories.base import BaseRepository
from apps.core.models import LogEntry


class UserInfoRepository(BaseRepository[UserInfoEntity]):
    def get_by_chat_id(self, chat_id: str) -> Optional[UserInfoEntity]:
        try:
            instance = UserInfoEntity.objects.get(user=chat_id)
            return UserInfoEntity.from_model(instance)
        except UserInfoEntity.DoesNotExist:
            return None

    def exists(self, chat_id: str) -> Optional[bool]:
        return UserInfo.objects.filter(chat_id=chat_id).exists()

    def create(self, **kwargs) -> UserInfoEntity:
        instance = UserInfo.objects.create(**kwargs)
        return UserInfoEntity.from_model(instance)

    # TODO тут нужно сделать ретерн и обработку ексепшн, если запись не сохранилась
    def save(self, entity: 'UserInfoEntity') -> None:
        instance, _ = UserInfo.objects.update_or_create(
            chat_id=entity.chat_id,
            defaults={
                'first_name': entity.first_name,
                'last_name': entity.last_name,
                'username': entity.username,
            }
        )
        return UserInfoEntity.from_model(instance)

    def delete(self, entity: 'UserInfoEntity') -> None:
        UserInfo.objects.filter(chat_id=entity.chat_id).delete()

    # TODO тут скорее всего нужно передать просто chat_id юзера, зач модель целую
    def log(self, instance: UserInfo, text: str, detail=None, level=0):
        LogEntry.objects.create(
            user=instance.chat_id,
            text=text,
            detail=detail,
            level=level
        )
