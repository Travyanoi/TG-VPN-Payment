from apps.bot.models import UserInfo
from apps.core.models import LogEntry


class UserInfoRepository:
    def get_by_chat_id(self, chat_id: str) -> UserInfo:
        return UserInfo.objects.get(chat_id=chat_id)

    def exists(self, chat_id: str) -> bool:
        return UserInfo.objects.filter(chat_id=chat_id).exists()

    def create(self, chat_id: str, first_name: str, last_name: str = None, username: str = None) -> UserInfo:
        return UserInfo.objects.create(
            chat_id=chat_id,
            first_name=first_name,
            last_name=last_name,
            username=username
        )

    def log(self, user: UserInfo, text: str, detail=None, level=0):
        LogEntry.objects.create(
            user=user.chat_id,
            text=text,
            detail=detail,
            level=level
        )
