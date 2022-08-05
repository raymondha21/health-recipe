from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, RadioField, FloatField
from wtforms.validators import InputRequired,Length,DataRequired


class UserRegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    first_name = StringField("First name", validators=[InputRequired(),Length(max=30)])
    last_name = StringField("Last name", validators=[InputRequired(),Length(max=30)])
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editting current user"""

    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    height = FloatField('Height (in inches)',validators=[DataRequired()])
    weight = FloatField('Weight (in pounds)',validators=[DataRequired()])
    age = IntegerField('Age',validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('M','Male'),('F','Female')],validators=[DataRequired()])
    activity = SelectField('Activity Level',
        choices=[(1.2,"Sedentary (little to no exercise + work a desk job)"),
            (1.375,"Lightly Active (light exercise 1-3 days / week)"),
            (1.55,"Moderately Active (moderate exercise 3-5 days / week)"),
            (1.75,"Very Active (heavy exercise 6-7 days / week)"),
            (1.9,"Extremely Active (very heavy exercise, hard labor job, training 2x / day)")],
        coerce=float,
        validators=[DataRequired()])

class UserBioForm(FlaskForm):
    """Form for adding/editting """

    height = FloatField('Height (in inches)',validators=[DataRequired()])
    weight = FloatField('Weight (in pounds)',validators=[DataRequired()])
    age = IntegerField('Age',validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('M','Male'),('F','Female')],validators=[DataRequired()])
    activity = SelectField('Activity Level',
        choices=[(1.2,"Sedentary (little to no exercise + work a desk job)"),
            (1.375,"Lightly Active (light exercise 1-3 days / week)"),
            (1.55,"Moderately Active (moderate exercise 3-5 days / week)"),
            (1.75,"Very Active (heavy exercise 6-7 days / week)"),
            (1.9,"Extremely Active (very heavy exercise, hard labor job, training 2x / day)")],
        coerce=float,
        validators=[DataRequired()])

