from django.core.management.base import BaseCommand

from apps.bot.repositories.user_info import UserInfoRepository


class Command(BaseCommand):
    help = 'Start the bot'

    def handle(self, *args, **options):
        test_entity = UserInfoRepository().get_by_chat_id(chat_id="608862111")
        print(f"{test_entity.chat_id}\n{test_entity.username}\n")

