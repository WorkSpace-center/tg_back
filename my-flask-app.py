#from flask import Flask

#app = Flask("MyFlaskApp")

#@app.route("/", methods=["GET"])
#def welcome():
#    return "<h1>Hello motherfacker !!!</h1>"

from flask import Flask, request

app = Flask("MyFlaskApp")

@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        # Получите данные из POST-запроса
        data = request.json  # Если данные отправляются в формате JSON
        # Извлекаем нужные данные (например, значение по ключу 'message')
        message = data.get("message", "No message provided")
        return f"<h1>Hello motherfacker !!! {message}</h1>"
    return "<h1>Hello motherfacker !!!</h1>"

if __name__ == "__main__":
    app.run()