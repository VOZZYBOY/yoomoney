import dotenv
import os

dotenv.load_dotenv()

API_HOST = os.getenv('API_HOST')
API_PORT = int(os.getenv('API_PORT'))

YMONEY_CLIENT_ID = os.getenv('YMONEY_CLIENT_ID')
YKASSA_SECRET_KEY = os.getenv('YKASSA_SECRET_KEY')
YKASSA_SHOP_ID = os.getenv('YKASSA_SHOP_ID')
RETURN_URL = os.getenv('RETURN_URL')
CHECK_PAYMENT_STATUS_PERIOD = int(os.getenv('CHECK_PAYMENT_STATUS_PERIOD'))
DATABASE_PATH = os.path.join(current_dir, 'app', DATABASE_NAME)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
