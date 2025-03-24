from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, User  # Импортируем БД и модель

app = Flask("MyFlaskApp")
CORS(app)  # Разрешаем CORS для всех источников

# Подключаем SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Привязываем БД к Flask-приложению
db.init_app(app)

# Создание таблиц при запуске
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        data = request.json  # Получаем JSON

        # Создаем пользователя
        new_user = User(
            name=data.get("name", ""),
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
        )

        # Сохраняем в БД
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created"}), 201

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
