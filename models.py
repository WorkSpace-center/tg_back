from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Модель пользователя
class User(db.Model):
    __tablename__ = "users"
    name = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(15))
    hash = db.Column(db.String(150))


# Модель заказа
class Order(db.Model):
    __tablename__ = "orders"
    name = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date)
    time = db.Column(db.Time)
    article = db.Column(db.String(100))
    description = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
