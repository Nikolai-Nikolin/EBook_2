from flask import Flask, jsonify
from sqlalchemy.orm import Session, sessionmaker
from routes import app as routes_app
from models import Base
from connection import engine
from flask_jwt_extended import JWTManager
from datetime import timedelta

# создаем таблицы
Base.metadata.create_all(bind=engine)

app = Flask(__name__)

# Настройки для JWT
app.config['JWT_SECRET_KEY'] = 'python-forever'
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=90)

jwt = JWTManager(app)

app.register_blueprint(routes_app)

if __name__ == '__main__':
    app.run(debug=False, port=7000)
