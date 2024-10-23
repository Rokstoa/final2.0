from wtforms import DecimalField, FileField, StringField, DateTimeField, IntegerField, SubmitField
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from wtforms.fields import DateField

class SupportForm(FlaskForm):
    message = StringField('Ваше повідомлення', validators=[DataRequired()])
    submit = SubmitField('Надіслати')

class MenuItemForm(FlaskForm):
    name = StringField('Назва', validators=[DataRequired()])
    description = StringField('Опис', validators=[DataRequired()])
    price = DecimalField('Ціна', validators=[DataRequired()])
    image_file = FileField('Зображення', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Додати пункт меню')

class ReservationForm(FlaskForm):
    name = StringField("Ім'я", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    date = DateField('Дата бронювання', format='%Y-%m-%d', validators=[DataRequired()])
    people_count = IntegerField('Кількість людей', validators=[DataRequired()])

class ReviewForm(FlaskForm):
    rating = IntegerField('Оцінка (1-5)', validators=[DataRequired()])
    comment = StringField('Коментар')
    submit = SubmitField('Надіслати відгук')
