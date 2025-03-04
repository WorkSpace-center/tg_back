# версия для отправки возврата данных на офронтенд
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask("MyFlaskApp")
CORS(app)  # Разрешаем CORS для всех источников


@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        # Получаем данные из POST-запроса
        data = request.json  # Если данные отправляются в формате JSON

        # Достаём только нужные поля, если их нет — ставим пустую строку
        response_data = {
            # "name": data.get("name", ""),
            "username": data.get("username", ""),
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
        }

        return jsonify(response_data), 200  # Отправляем JSON-ответ

    return "<h1>Hello motherfacker !!!</h1>"


if __name__ == "__main__":
    app.run(debug=True)