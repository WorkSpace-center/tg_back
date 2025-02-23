from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask("MyFlaskApp")
CORS(app)

# Настройка базы данных PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://username:password@host:port/database"  # Измените на ваши данные
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_secret_key"  # Замените на свой секретный ключ
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Модель пользователя
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(15))


# Модель заказа
class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date)
    time = db.Column(db.Time)
    article = db.Column(db.String(100))
    description = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)


# Создание базы данных и таблиц
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        data = request.json

        # Валидация данных
        if not all(
            key in data
            for key in (
                "login",
                "firstName",
                "lastName",
                "email",
                "password",
                "phone_number",
            )
        ):
            return jsonify({"message": "Invalid data provided"}), 400

        hashed_password = generate_password_hash(data["password"])  # Хешируем пароль

        new_user = User(
            login=data["login"],
            first_name=data["firstName"],
            last_name=data["lastName"],
            email=data["email"],
            password=hashed_password,
            phone_number=data["phone_number"],
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "Data received and saved", "data": data}), 201
        except IntegrityError:
            db.session.rollback()
            return (
                jsonify({"message": "User with this login or email already exists"}),
                409,
            )

    return "<h1>Hello motherfacker !!!</h1>"


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(login=data.get("login")).first()

    if user and check_password_hash(user.password, data.get("password")):
        access_token = create_access_token(identity=user.login)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Bad username or password"}), 401


@app.route("/users", methods=["PUT", "DELETE"])
@jwt_required()  # Защита маршрута с помощью JWT
def manage_users():
    current_user = get_jwt_identity()  # Получаем текущего пользователя

    if request.method == "PUT":
        data = request.json
        user_id = data.get("id")

        if str(user_id) != str(
            current_user
        ):  # Проверяем, что пользователь пытается изменить только свои данные
            return jsonify({"message": "Permission denied"}), 403
        user = User.query.get(user_id)
        if user:
            user.login = data.get("login", user.login)
            user.first_name = data.get("firstName", user.first_name)
            user.last_name = data.get("lastName", user.last_name)
            user.email = data.get("email", user.email)
            user.password = generate_password_hash(
                data.get("password", user.password)
            )  # Хешируем новый пароль
            user.phone_number = data.get("phone_number", user.phone_number)
            db.session.commit()
            return jsonify({"message": "User updated successfully"}), 200
        return jsonify({"message": "User not found"}), 404

    elif request.method == "DELETE":
        data = request.json
        user_id = data.get("id")

        if str(user_id) != str(
            current_user
        ):  # Проверяем, что пользователь пытается удалить только свои данные
            return jsonify({"message": "Permission denied"}), 403

        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted successfully"}), 200
        return jsonify({"message": "User not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
