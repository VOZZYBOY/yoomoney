
import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def send_notification(message: str):
    """
    Отправляет уведомление в Телеграм.
    """
    log.debug(f"Отправляю сообщение в ТГ бота: {message}")
    url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}/sendMessage"
    data = {
        'chat_id': os.environ.get('TELEGRAM_CHAT_ID'),
        'text': message
    }
    requests.post(url, data=data)
