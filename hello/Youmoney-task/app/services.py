# services.py
import uuid
import logging

from yookassa import Configuration, Payment, Refund
from config import YKASSA_SHOP_ID, YKASSA_SECRET_KEY

logger = logging.getLogger(__name__)
Configuration.account_id = YKASSA_SHOP_ID 
Configuration.secret_key = YKASSA_SECRET_KEY

class YooKassaService:

    @staticmethod
    def create_payment(data):
        try:
            payment_id = str(uuid.uuid4())
            payment = Payment.create({
                "amount": data['amount'],
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://www.example.com/return_url"  # Замени на свой return_url!
                },
                "capture": True,
                "description": f"Заказ №{data['order_id']}",
                "payment_method_data": {"type": "bank_card"} if not data.get('is_recurrent') else None,
                "save_payment_method": data.get("save_payment_method", False) if data.get('is_recurrent') else False
            }, payment_id)

            return payment.confirmation.confirmation_url, payment.id, None

        except Exception as e:
            logger.exception("Ошибка при создании платежа в ЮKassa")
            return None, None, str(e)

    @staticmethod
    def refund_payment(data):
        try:
            refund = Refund.create({
                "amount": data['amount'],
                "payment_id": data['payment_id']
            })
            return refund.json(), None
        except Exception as e:
            logger.exception("Ошибка при создании возврата в ЮKassa")
            return None, str(e)
