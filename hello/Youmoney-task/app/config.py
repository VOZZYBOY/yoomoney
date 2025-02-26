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
DATABASE_NAME = os.getenv('DATABASE_NAME')

current_dir = os.getcwd()
DATABASE_PATH = os.path.join(current_dir, 'app', DATABASE_NAME)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Just .env Sample:
#
# YMONEY_CLIENT_ID=0012ABBAA12AB456AB8BA8A9EF9E89C44A0BC28GF7D9B014B99F6BBB78BBA9123
# YKASSA_SECRET_KEY=test_AbCdE12CDe4e5U8Mki123y123d498WAnlolkekxsC04
# YKASSA_SHOP_ID=1234567
# RETURN_URL=http://localhost:5000/api/payment
# CHECK_PAYMENT_STATUS_PERIOD=5
# DATABASE_NAME=payments_status.db
