from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask("MyFlaskApp")
CORS(app)  # Разрешаем CORS для всех источников

# Подключаем MySQL
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
    amount = db.Column(db.Float, nullable=False)  # quantity * price


# Создание таблиц
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        data = request.json

        # Проверяем, есть ли уже пользователь с таким username
        existing_user = User.query.filter_by(username=data.get("username")).first()
        if existing_user:
            return (
                jsonify(
                    {"message": "User already exists (такой пользователь уже есть)"}
                ),
                409,
            )

        new_user = User(
            name=data.get("name", ""),
            username=data.get("username", ""),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created (Добавлен новый пользователь)"}), 201

    # GET-запрос — отдаем всех пользователей
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

        return jsonify({"message": "Order created (Заказ добавлен)"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    orders_data = [
        {
            "username": o.username,
            "order_number": o.order_number,
            "order_date": o.order_date.strftime("%Y-%m-%d") if o.order_date else None,
            "order_time": o.order_time.strftime("%H:%M:%S") if o.order_time else None,
            "article": o.article,
            "description": o.description,
            "quantity": o.quantity,
            "price": float(o.price),
            "amount": float(o.amount),
        }
        for o in orders
    ]
    return jsonify(orders_data), 200


if __name__ == "__main__":
    app.run(debug=True)
