from django.core.management.base import BaseCommand
from apps.bot.bot import BotPolling
import asyncio


class Command(BaseCommand):
    help = 'Start the bot'

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(BotPolling())
        finally:
            loop.close()
