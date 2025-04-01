from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask("MyFlaskApp")
CORS(app)  # Разрешаем CORS для всех источников

# Подключаем SQLite, указывая путь к базе данных на сервере
DB_PATH = "/data/my_database.db"  # Указываем путь к файлу БД на сервере
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))


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
            )  # 409 - конфликт данных

        # Создаем нового пользователя
        new_user = User(
            name=data.get("name", ""),
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
        )

        # Сохраняем в БД
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created (Добавлен новый пользователь)"}), 201

    # Если GET-запрос — отдаем всех пользователей
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


if __name__ == "__main__":
    app.run(debug=True)
