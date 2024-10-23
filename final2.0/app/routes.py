from flask import render_template, redirect, url_for, flash, request, abort, current_app
from app.models import User, MenuItem, Review, Reservation
from flask import current_app as app
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps
import os
import secrets
from PIL import Image
from werkzeug.utils import secure_filename
from app.forms import ReservationForm, ReviewForm, MenuItemForm
from app import db
from app.forms import SupportForm
from app.models import SupportMessage

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Реєстрація успішна!')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Увійшли успішно!')
            return redirect(url_for('menu'))
        else:
            flash('Невірний email або пароль', 'danger')
    return render_template('login.html')


@app.route('/menu')
def menu():
    items = MenuItem.query.all()
    return render_template('menu.html', items=items)


@app.route('/admin/menu', methods=['GET', 'POST'])
@login_required
def admin_menu():
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))

    form = MenuItemForm()
    if form.validate_on_submit():
        if form.image_file.data:
            image_file = save_image(form.image_file.data)
        else:
            image_file = 'default.jpg'

        new_item = MenuItem(name=form.name.data, description=form.description.data, price=form.price.data,
                            image_file=image_file)
        db.session.add(new_item)
        db.session.commit()
        flash('Пункт меню успішно додано!', 'success')
        return redirect(url_for('menu'))

    return render_template('admin_menu.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('index'))


@app.route('/menu/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f'Пункт меню {item.name} успішно видалено.', 'success')
    return redirect(url_for('menu'))

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    form = ReservationForm()
    if form.validate_on_submit():
        try:
            name = form.name.data
            email = form.email.data
            date = form.date.data
            people_count = form.people_count.data

            reservation = Reservation(name=name, email=email, reservation_date=date, number_of_people=people_count)

            db.session.add(reservation)

            db.session.commit()

            flash('Бронювання успішно створено!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Помилка створення бронювання: {str(e)}", 'danger')
    return render_template('reserve.html', form=form)



@app.route('/menu/item/<int:item_id>/review', methods=['GET', 'POST'])
@login_required
def review_menu_item(item_id):
    menu_item = MenuItem.query.get_or_404(item_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(rating=form.rating.data, comment=form.comment.data, menu_item_id=menu_item.id, user_id=current_user.id)
        db.session.add(review)
        db.session.commit()
        flash('Ваш відгук було додано!', 'success')
        return redirect(url_for('menu'))
    return render_template('review_menu_item.html', form=form, menu_item=menu_item)

@app.route('/profile')
@login_required
def profile():
    reservations = Reservation.query.filter_by(email=current_user.email).all()
    return render_template('profile.html', reservations=reservations)


@app.route('/admin/reservations')
@login_required
@admin_required
def admin_reservations():
    reservations = Reservation.query.all()
    return render_template('admin_reservations.html', reservations=reservations)


@app.route('/admin/reservation/delete/<int:reservation_id>', methods=['POST'])
@login_required
@admin_required
def delete_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    db.session.delete(reservation)
    db.session.commit()
    flash(f'Бронювання {reservation.name} успішно видалено.', 'success')
    return redirect(url_for('admin_reservations'))


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/user/<int:user_id>/make_admin', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'Користувач {user.username} отримав права адміністратора.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/review/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Перевірка: тільки автор відгуку або адміністратор може видалити відгук
    if current_user.id != review.user_id and not current_user.is_admin:
        abort(403)

    db.session.delete(review)
    db.session.commit()
    flash('Відгук було успішно видалено.', 'success')
    return redirect(url_for('menu'))

@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    form = SupportForm()
    if form.validate_on_submit():
        support_message = SupportMessage(user_id=current_user.id, message=form.message.data)
        db.session.add(support_message)
        db.session.commit()
        flash('Ваш запит надіслано!', 'success')
        return redirect(url_for('index'))
    return render_template('support.html', form=form)

@app.route('/admin/support')
@login_required
@admin_required
def admin_support():
    messages = SupportMessage.query.filter_by(is_closed=False).all()
    return render_template('admin_support.html', messages=messages)

@app.route('/admin/support/<int:message_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reply_support(message_id):
    message = SupportMessage.query.get_or_404(message_id)
    if request.method == 'POST':
        response = request.form['response']
        message.response = response
        message.is_closed = True
        db.session.commit()
        flash('Відповідь надіслано, запит закрито!', 'success')
        return redirect(url_for('admin_support'))
    return render_template('admin_reply_support.html', message=message)

@app.route('/my_support_messages', methods=['GET'])
@login_required
def my_support_messages():
    messages = SupportMessage.query.filter_by(user_id=current_user.id).all()
    return render_template('my_support_messages.html', messages=messages)


@app.route('/delete-support-message/<int:message_id>', methods=['POST'])
@login_required  # Переконайтеся, що тільки авторизовані користувачі можуть видаляти повідомлення
def delete_support_message(message_id):
    message = SupportMessage.query.get_or_404(message_id)
    if message.user_id != current_user.id:
        abort(403)  # Якщо користувач не є автором повідомлення, відхилити запит

    db.session.delete(message)
    db.session.commit()
    flash('Запит підтримки успішно видалено!', 'success')
    return redirect(url_for('my_support_messages'))



def save_image(form_image):
    filename = secure_filename(form_image.filename)
    image_path = os.path.join(
        current_app.root_path, 'static', 'menu_pics', filename
    )

    directory = os.path.dirname(image_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    image = Image.open(form_image)
    image.save(image_path)

    return filename