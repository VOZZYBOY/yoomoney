# Система оплаты с использованием ЮKassa (YooMoney)

## Описание

Данный проект представляет собой простую систему оплаты, реализованную на языке Python с использованием фреймворка Flask. Система позволяет:

*   Создавать платежи (разовые и рекуррентные) через платёжный шлюз ЮKassa (YooMoney).
*   Получать информацию о статусе платежа.
*   Обрабатывать Webhook-уведомления от ЮKassa об изменении статуса платежа.
*   Делать возвраты платежей.
*   Автоматически повторять рекуррентные платежи в случае неудачи (с задержкой).
*   Отправлять уведомления об изменении статуса платежа в Telegram.

## Технологии

*   **Python 3.11+**
*   **Flask:** Микрофреймворк для создания веб-приложений.
*   **Flask-RESTful:** Расширение Flask для удобного создания REST API.
*   **SQLAlchemy:** ORM (Object-Relational Mapper) для работы с базой данных.
*   **SQLite:** Простая, файловая СУБД (используется для разработки).
*   **YooKassa API:**  API платёжного шлюза ЮKassa.
*   **Celery:**  Менеджер асинхронных задач (используется для повторных попыток оплаты).
*   **Redis:**  Брокер сообщений для Celery.
*   **Marshmallow:**  Библиотека для валидации данных.
*   **Requests:**  Библиотека для отправки HTTP-запросов (используется для отправки уведомлений в Telegram).
*   **python-dotenv:**  Библиотека для загрузки переменных окружения из файла `.env`.
*   **ngrok:**  Инструмент для создания туннелей к локальному серверу (используется для тестирования Webhook).
*   **hmac:** Для создания подписи.
*   **uuid:** Для создания уникального ключа.

## Структура проекта
├── .env <-- Файл с переменными окружения 
├── .gitignore <-- Файл, указывающий Git, какие файлы игнорировать
├── app.py <-- Основной файл приложения (Flask, эндпоинты)
├── config.py <-- Файл конфигурации (загрузка переменных окружения)
├── models.py <-- Модели базы данных (SQLAlchemy)
├── schemas.py <-- Схемы Marshmallow (валидация данных)
├── services.py <-- Сервисный слой (взаимодействие с ЮKassa API)
├── tasks.py <-- Задачи Celery (повторные попытки оплаты)
├── requirements.txt <-- Список зависимостей
└── notification.py <-- Модуль для отправки уведомлений


## Установка и запуск

1.  **Клонировать репозиторий:**

    ```bash
    git clone <URL_репозитория>
    cd <название_папки_проекта>
    ```

2.  **Создать и активировать виртуальное окружение:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    .venv\Scripts\activate  # Windows
    ```

3.  **Установить зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Создать файл `.env`** в корневой папке проекта и добавить туда переменные окружения:

    ```
    YOOKASSA_SHOP_ID=<ваш_shopId_из_ЮKassa>
    YOOKASSA_SECRET_KEY=<секретный_ключ_из_ЮKassa>
    TELEGRAM_BOT_TOKEN=<токен_Telegram_бота>
    TELEGRAM_CHAT_ID=<ID_чата_Telegram>
    DATABASE_URL=sqlite:///payments.db
    CELERY_BROKER_URL=redis://localhost:6379/0
    CELERY_RESULT_BACKEND=redis://localhost:6379/0
    API_PORT=5000
    API_HOST=0.0.0.0
    MAX_RETRIES=5
    ```

    *   `YOOKASSA_SHOP_ID` и `YOOKASSA_SECRET_KEY`:  Получить в личном кабинете ЮKassa.
    *   `TELEGRAM_BOT_TOKEN`:  Получить у `@BotFather` в Telegram.
    *   `TELEGRAM_CHAT_ID`:  ID чата, куда бот будет отправлять уведомления (можно узнать с помощью ботов типа `@myidbot`).
    *   `DATABASE_URL`: строка подключения к базе данных.
    *   `CELERY_BROKER_URL` и `CELERY_RESULT_BACKEND`:  URL брокера сообщений и бэкенда для Celery (в данном случае используется Redis).
    *   `API_PORT`:  Порт, на котором будет работать Flask-приложение.
    *   `API_HOST`: Хост
    *   `MAX_RETRIES`:  Максимальное количество повторных попыток оплаты.

5.  **Установить и запустить Redis:**  Инструкции по установке зависят от операционной системы.

6.  **Запустить Celery worker:**

    ```bash
    celery -A tasks worker -l info
    ```

7.  **Запустить Flask (в другом окне терминала):**

    ```bash
    python app.py
    ```

8.  **Запустить ngrok:**

    ```bash
    ngrok http 5000
    ```

9.  **Настроить Webhook в ЮKassa:**  В личном кабинете ЮKassa, в настройках магазина, указать URL вида `https://<случайный_URL>.ngrok.io/webhook`.

## API

### Создание платежа

**Endpoint:**  `/payments`

**Метод:**  `POST`

**Тело запроса (JSON):**

```json
{
    "amount": {
        "value": "100.00",
        "currency": "RUB"
    },
    "user_id": "user123",
    "order_id": 1,
    "is_recurrent": false
}

