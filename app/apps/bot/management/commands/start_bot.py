from django.core.management.base import BaseCommand
from apps.bot.bot import BotPolling
import asyncio


class Command(BaseCommand):
    help = 'Start the bot'

    def handle(self, *args, **options):
        try:
            BotPolling()
        finally:
            print("Webhook editing has done!\n")
