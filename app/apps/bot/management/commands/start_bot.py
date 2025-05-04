from django.core.management.base import BaseCommand
from apps.bot.bot import bot_polling

import structlog

logger = structlog.getLogger('telebot')


class Command(BaseCommand):
    help = 'Start the bot'

    def handle(self, *args, **options):
        try:
            logger.info("trying configure webhook")
            bot_polling()
        except Exception as e:
            logger.error("Webhook doesn't configured")
        finally:
            logger.info("Webhook editing has done!")
