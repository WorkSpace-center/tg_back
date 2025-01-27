# from flask import Flask

# app = Flask("MyFlaskApp")

# @app.route("/", methods=["GET"])
# def welcome():
#    return "<h1>Hello motherfacker !!!</h1>"

from flask import Flask, request
from flask_cors import CORS

app = Flask("MyFlaskApp")
CORS(app)  # Разрешаем CORS для всех источников


@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        # Получите данные из POST-запроса
        data = request.json  # Если данные отправляются в формате JSON
        # Извлекаем нужные данные (например, значение по ключу 'message')
        message = data.get("message", "No message provided")
        return {"message": "Data received", "data": data}, 200
    return "<h1>Hello motherfacker !!!</h1>"


if __name__ == "__main__":
    app.run()
