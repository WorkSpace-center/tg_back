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

# Подключение к удаленной базе данных (на сервере Amvera.ru)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://admin:securepassword@db.amvera.ru:5432/mydatabase"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)
jwt = JWTManager(app)

name_2 = []
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Импорт моделей из отдельного файла
from models import User, Order

# Создание базы данных (если необходимо)
with app.app_context():
    db.create_all()


@app.route("/register", methods=["POST"])
def register():
    """Регистрация пользователя"""
    data = request.json
    if not all(
        key in data
        for key in ("name", "username", "first_name", "last_name", "password")
    ):
        return jsonify({"message": "Invalid data provided"}), 400

    hashed_password = generate_password_hash(data["password"])

    new_user = User(
        name=data["name"],
        username=data["username"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        password=hashed_password,
        hash=data["hash"],
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Username already exists"}), 409


@app.route("/login", methods=["POST"])
def login():
    """Авторизация пользователя"""
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()

    if user and check_password_hash(user.password, data.get("password")):
        access_token = create_access_token(identity=user.username)
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Bad username or password"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
