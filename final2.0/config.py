import os

class Config:
    PORT = int(os.environ.get("PORT", 5000))
    HOST = '0.0.0.0'  # Слушаем на всех интерфейсах
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'TGVYj17xDAi4CFqAaMtSSZsZc4RuB18q'
