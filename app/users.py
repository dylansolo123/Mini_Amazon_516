from flask import render_template, redirect, url_for, flash, request, Blueprint
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from .models.user import User
import csv
from datetime import datetime
import os

bp = Blueprint('users', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        print(form.email.data, form.password.data)
        user = User.get_by_auth(form.email.data, form.password.data)
        print(user)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

class RegistrationForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                         EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                           form.password.data,
                           form.fullname.data,
                           form.address.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/sales')
@login_required
def sales():
    if not current_user.is_seller:
        return redirect(url_for('index.index'))  # Redirect to the homepage or another page as needed
    inventory_items = current_user.get_seller_inventory()
    return render_template('seller_products.html', inventory_items=inventory_items)

def get_recent_reviews_by_user_id_from_csv(user_id):
    reviews = []
    csv_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db', 'generated', 'product_reviews.csv')
    try:
        with open(csv_filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == user_id:
                    reviews.append({
                        'product_id': row['product_id'],
                        'rating': int(row['rating']),
                        'review_text': row['review_text'],
                        # We'll add a placeholder date for now since the CSV doesn't have a date
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
    except FileNotFoundError:
        return []
    return reviews[:5]

class UserReviewSearchForm(FlaskForm):
    user_id = StringField('User ID', validators=[DataRequired()])
    submit = SubmitField('Search Reviews')

@bp.route('/my-account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = UserReviewSearchForm()
    user_reviews = None
    searched_user_id = None
    
    if form.validate_on_submit():
        searched_user_id = form.user_id.data
        user_reviews = get_recent_reviews_by_user_id_from_csv(searched_user_id)
    else:
        # Show current user's reviews by default
        user_reviews = get_recent_reviews_by_user_id_from_csv(current_user.id)
        searched_user_id = current_user.id
    
    return render_template('myaccount.html', 
                         user=current_user, 
                         user_reviews=user_reviews,
                         searched_user_id=searched_user_id,
                         form=form)