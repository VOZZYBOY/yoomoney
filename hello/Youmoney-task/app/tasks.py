import logging
from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from marshmallow import ValidationError
from http import HTTPStatus
from services import YooKassaService
from schemas import PaymentSchema, RefundSchema
from models import session, Payment
from config import API_HOST, API_PORT
import hmac
from yookassa import Webhook, Configuration
from tasks import retry_payment_task
from notification import send_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

payment_parser = reqparse.RequestParser()
payment_parser.add_argument('amount', type=dict, required=True, help='Payment amount details')
payment_parser.add_argument('user_id', type=str, required=True, help='User ID')
payment_parser.add_argument('order_id', type=int, required=True, help='Order ID')
payment_parser.add_argument('is_recurrent', type=bool, default=False)

refund_parser = reqparse.RequestParser()
refund_parser.add_argument('amount', type=dict, required=True, help='Refund amount details')
refund_parser.add_argument('payment_id', type=str, required=True, help='Payment ID to refund')

class PaymentInfo(Resource):

    def get(self, payment_id):
        logger.info(f"Запрос информации о платеже: {payment_id}")
        try:
            payment = session.query(Payment).filter_by(payment_id=payment_id).first()
            if not payment:
                return {'message': 'Платёж не найден'}, HTTPStatus.NOT_FOUND
            return jsonify(payment.to_dict())
        except Exception as e:
            logger.exception(f"Ошибка при получении информации о платеже: {payment_id}")
            return {'message': 'Внутренняя ошибка сервера'}, HTTPStatus.INTERNAL_SERVER_ERROR

class CreatePayment(Resource):

    def post(self):
        logger.info(f"Запрос на создание платежа: {request.get_json()}")
        try:
            args = payment_parser.parse_args()
            schema = PaymentSchema()
            data = schema.load(args)

            payment_url, yookassa_payment_id, error = YooKassaService.create_payment(data)
            if error:
                return {'message': error}, HTTPStatus.BAD_REQUEST

            payment = Payment(
                amount=float(data['amount']['value']),
                description=f"Заказ №{data['order_id']}",
                payment_id=yookassa_payment_id,
                user_id=data['user_id'],
                is_recurrent=data.get('is_recurrent', False)
            )

            session.add(payment)
            session.commit()
            return {'payment_url': payment_url, 'payment_id': yookassa_payment_id}, HTTPStatus.CREATED

        except ValidationError as e:
            logger.error(f"Ошибка валидации данных платежа: {e.messages}")
            return {'message': 'Ошибка валидации данных', 'errors': e.messages}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            logger.exception("Ошибка при создании платежа")
            return {'message': 'Внутренняя ошибка сервера'}, HTTPStatus.INTERNAL_SERVER_ERROR

class RefundPayment(Resource):

    def post(self):
        logger.info(f"Запрос на возврат средств: {request.get_json()}")
        try:
            args = refund_parser.parse_args()
            schema = RefundSchema()
            data = schema.load(args)

            refund_data, error = YooKassaService.refund_payment(data)
            if error:
                return {'message': error}, HTTPStatus.BAD_REQUEST
            return refund_data, HTTPStatus.CREATED

        except ValidationError as e:
            logger.error(f"Ошибка валидации данных для возврата: {e.messages}")
            return {'message': 'Ошибка валидации данных', 'errors': e.messages}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            logger.exception("Ошибка при создании возврата")
            return {'message': 'Внутренняя ошибка сервера'}, HTTPStatus.INTERNAL_SERVER_ERROR


class WebhookResource(Resource):

    def post(self):
        logger.info(f"Получен Webhook от ЮKassa: {request.data}")
        try:
            signature = request.headers.get('X-Yookassa-Signature')
            if not signature:
                logger.warning("Отсутствует подпись Webhook")
                return 'Missing signature', HTTPStatus.BAD_REQUEST

            expected_signature = Webhook.get_signature(
                request.data,
                Configuration.secret_key
            )

            if not hmac.compare_digest(signature, expected_signature):
                logger.error("Неверная подпись Webhook")
                return 'Invalid signature', HTTPStatus.UNAUTHORIZED

            event_json = request.get_json()
            notification_object = Webhook.construct_event(event_json)
            payment_id = notification_object.object.id
            payment_status = notification_object.object.status

            payment = session.query(Payment).filter_by(payment_id=payment_id).first()
            if not payment:
                logger.warning(f"Webhook: Платёж не найден: {payment_id}")
                return "Payment not found", HTTPStatus.NOT_FOUND

            payment.status = payment_status

            if payment_status == 'succeeded':
                send_notification( f"Платеж {payment_id} успешно оплачен!")
            elif payment_status == 'canceled':
                reason = notification_object.object.cancellation_details.reason if notification_object.object.cancellation_details else 'Unknown reason'
                send_notification( f"Платеж {payment_id} отменен. Причина: {reason}")
                if payment.is_recurrent and payment.retries < int(os.environ.get("MAX_RETRIES", 5)):
                    retry_payment_task.apply_async((payment.id,), countdown=10)

            elif payment_status == 'waiting_for_capture':
                send_notification( f"Платеж {payment_id} ожидает подтверждения.")

            session.commit()
            logger.info(f"Webhook обработан успешно. Платеж: {payment_id}, статус: {payment_status}")
            return 'OK', HTTPStatus.OK

        except Exception as e:
            logger.exception("Ошибка при обработке Webhook")
            session.rollback()
            return 'Internal Server Error', HTTPStatus.INTERNAL_SERVER_ERROR

api.add_resource(CreatePayment, '/payments')
api.add_resource(PaymentInfo, '/payments/<string:payment_id>')
api.add_resource(RefundPayment, '/refunds')
api.add_resource(WebhookResource, '/webhook')

if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT, debug=True)
