from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)  # Додаємо поле is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    response = db.Column(db.String(1000), nullable=True)
    is_closed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='support_messages')

User.support_messages = db.relationship('SupportMessage', back_populates='user', cascade="all, delete-orphan")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    def __repr__(self):
        return f'<MenuItem {self.name}>'

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    reservation_date = db.Column(db.DateTime, nullable=False)
    number_of_people = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Reservation {self.name}>'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # Оцінка (1-5)
    comment = db.Column(db.String(500), nullable=True)  # Коментар
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)  # Зв'язок з меню
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Зв'язок з користувачем

    menu_item = db.relationship('MenuItem', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f'<Review for {self.menu_item.name} by {self.user.username}>'

MenuItem.reviews = db.relationship('Review', back_populates='menu_item', cascade="all, delete-orphan")

User.reviews = db.relationship('Review', back_populates='user', cascade="all, delete-orphan")


