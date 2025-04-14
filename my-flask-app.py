import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Загрузка переменных окружения
TOKEN = os.getenv("TG_BOT_TOKEN")

# Telegram Web App URL
WEB_APP_URL = os.getenv("WEB_APP_URL")

# Flask App Init
app = Flask("MyFlaskApp")
CORS(app)

# Настройки подключения к БД
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "pass")
MYSQL_HOST = os.getenv("MYSQL_HOST", "amvera-evst-run-database-tg")
MYSQL_DB = os.getenv("MYSQL_DB", "database tg")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)


# Модель заказа
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    order_number = db.Column(db.String(100), nullable=False)
    order_date = db.Column(db.String(20), nullable=False)
    order_time = db.Column(db.String(20), nullable=False)
    article = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)


# Создание таблиц
with app.app_context():
    db.create_all()


# Обработка Telegram сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return
    chat_id = message.chat.id
    text = message.text

    if text == "/start":
        keyboard = ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton(
                        "Заполнить форму, мудак!!!", web_app={"url": f"{WEB_APP_URL}/form"}
                    )
                ]
            ],
            resize_keyboard=True,
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text="Ниже появится кнопка, заполни форму!!!",
            reply_markup=keyboard,
        )

        inline_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Сделать заказ", web_app={"url": WEB_APP_URL})]]
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text="Заходи в наш интернет магазин по кнопке ниже",
            reply_markup=inline_keyboard,
        )

    elif message.web_app_data and message.web_app_data.data:
        try:
            data = json.loads(message.web_app_data.data)
            await context.bot.send_message(
                chat_id=chat_id, text="Спасибо за обратную связь!"
            )
            await context.bot.send_message(
                chat_id=chat_id, text=f"Ваша страна: {data.get('country')}"
            )
            await context.bot.send_message(
                chat_id=chat_id, text=f"Ваша улица: {data.get('street')}"
            )
            time.sleep(3)
            await context.bot.send_message(
                chat_id=chat_id, text="Всю информацию вы получите в этом чате"
            )
        except Exception as e:
            print(e)


# Роуты Flask
@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        data = request.json
        existing_user = User.query.filter_by(username=data.get("username")).first()
        if existing_user:
            return jsonify({"message": "User already exists"}), 409

        new_user = User(
            name=data.get("name", ""),
            username=data.get("username", ""),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created"}), 201

    users = User.query.all()
    users_data = [
        {
            "name": u.name,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
        }
        for u in users
    ]
    return jsonify(users_data), 200


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    try:
        quantity = int(data.get("quantity", 0))
        price = float(data.get("price", 0))
        amount = quantity * price

        new_order = Order(
            username=data.get("username", ""),
            order_number=data.get("order_number", ""),
            order_date=data.get("order_date", ""),
            order_time=data.get("order_time", ""),
            article=data.get("article", ""),
            description=data.get("description", ""),
            quantity=quantity,
            price=price,
            amount=amount,
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"message": "Order created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    orders_data = [
        {
            "username": o.username,
            "order_number": o.order_number,
            "order_date": o.order_date,
            "order_time": o.order_time,
            "article": o.article,
            "description": o.description,
            "quantity": o.quantity,
            "price": float(o.price),
            "amount": float(o.amount),
        }
        for o in orders
    ]
    return jsonify(orders_data), 200


@app.route("/web-data", methods=["POST"])
def web_data():
    data = request.json
    query_id = data.get("queryId")
    products = data.get("products", [])
    total_price = data.get("totalPrice", 0)

    try:
        product_titles = ", ".join([item["title"] for item in products])
        bot = application.bot
        bot.answer_web_app_query(
            query_id=query_id,
            result={
                "type": "article",
                "id": query_id,
                "title": "Успешная покупка",
                "input_message_content": {
                    "message_text": f"Поздравляю с покупкой, вы приобрели товар на сумму {total_price}, {product_titles}"
                },
            },
        )
        return jsonify({}), 200
    except Exception as e:
        print(e)
        return jsonify({}), 500


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(
        MessageHandler(filters.TEXT | filters.WEB_APP_DATA, handle_message)
    )
    application.run_polling()
    app.run(debug=True, port=8001)
