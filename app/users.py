from flask import render_template, redirect, url_for, flash, request, Blueprint,session
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from .models.user import User
from .models.purchase import Purchase
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
    # Clear any flash messages before logging out
    session.pop('_flashes', None)
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/sales')
@login_required
def sales():
    if not current_user.is_seller:
        return redirect(url_for('index.index')) 
    
    search_term = request.args.get('search', '')
    inventory_items = current_user.get_seller_inventory()
    seller_orders = User.get_seller_orders(current_user.user_id)
    
    if search_term:
        filtered_orders = []
        for order in seller_orders:
            if (search_term.lower() in str(order['order_id']).lower() or
                search_term.lower() in order['buyer_name'].lower() or
                search_term.lower() in order['buyer_address'].lower()):
                filtered_orders.append(order)
        seller_orders = filtered_orders
    
    return render_template('seller_products.html', 
                          inventory_items=inventory_items,
                          orders=seller_orders)

@bp.route('/fulfill-order-item', methods=['POST'])
@login_required
def fulfill_order_item():
    if not current_user.is_seller:
        return redirect(url_for('index.index'))
    
    order_item_id = request.form.get('order_item_id')
    
    try:
        order_item_id = int(order_item_id)
        User.fulfill_order_item(current_user.user_id, order_item_id)
        flash('Order item marked as fulfilled!')
    except ValueError:
        flash('Invalid order item ID')
    except Exception as e:
        flash(str(e))
    
    return redirect(url_for('users.sales'))

@bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_seller:
        return redirect(url_for('index.index'))
    
    categories = User.get_categories() #dropdown
    
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        name = request.form.get('name')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        
        try:
            category_id = int(category_id)
            price = float(price)
            quantity = int(quantity)
            
            product_id = User.add_product(
                category_id,
                name,
                description,
                image_url or "http://example.com/images/default.jpg",
                current_user.user_id,
                price,
                quantity
            )
            
            flash('Product added successfully!')
            return redirect(url_for('users.sales'))
            
        except ValueError:
            flash('Invalid input. Please check your entries.')
            return redirect(url_for('users.add_product'))
    
    return render_template('add_product.html', categories=categories)

@bp.route('/update_inventory_quantity', methods=['POST'])
@login_required
def update_inventory_quantity():
    if not current_user.is_seller:
        return redirect(url_for('index.index'))
    
    product_id = request.form.get('product_id')
    action = request.form.get('action')
    
    try:
        product_id = int(product_id)        
        current_quantity = User.get_inventory_item(current_user.user_id, product_id)
        if current_quantity is None:
            flash('Product not found in your inventory')
            return redirect(url_for('users.sales'))
            
        if action == 'increase':
            new_quantity = current_quantity + 1
        elif action == 'decrease':
            new_quantity = max(0, current_quantity - 1)
        else:
            flash('Invalid action')
            return redirect(url_for('users.sales'))
        
        User.update_inventory_quantity(current_user.user_id, product_id, new_quantity)
        
        flash('Inventory updated successfully')
    except ValueError:
        flash('Invalid product ID')
    
    return redirect(url_for('users.sales'))

@bp.route('/remove_from_inventory', methods=['POST'])
@login_required
def remove_from_inventory():
    if not current_user.is_seller:
        return redirect(url_for('index.index'))
    
    product_id = request.form.get('product_id')
    delete_product = request.form.get('delete_product') == 'true'
    
    try:
        product_id = int(product_id)
        User.remove_from_inventory(current_user.user_id, product_id, delete_product)
    
        if delete_product:
            flash('Product permanently removed')
        else:
            flash('Product removed from inventory')
    except ValueError:
        flash('Invalid product ID')
    
    return redirect(url_for('users.sales'))

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
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
    except FileNotFoundError:
        return []
    return reviews[:5]

class UserReviewSearchForm(FlaskForm):
    user_id = StringField('User ID', validators=[DataRequired()])
    submit = SubmitField('Search Reviews')

class AccountUpdateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[Optional()])
    submit = SubmitField('Update Profile')

    def validate_email(self, email):
        if email.data != current_user.email and User.email_exists(email.data):
            raise ValidationError('Email already in use by another account.')

@bp.route('/my-account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = AccountUpdateForm()
    user_reviews = get_recent_reviews_by_user_id_from_csv(current_user.id)
    purchases = current_user.get_purchase_history()
    
    if form.validate_on_submit():
        try:
            User.update_info(
                current_user.id,
                form.email.data,
                form.full_name.data,
                form.address.data,
                form.password.data if form.password.data else None
            )
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('users.my_account'))
        except Exception as e:
            flash(str(e), 'error')
    
    if request.method == 'GET':
        form.email.data = current_user.email
        form.full_name.data = current_user.full_name
        form.address.data = current_user.address
    
    return render_template('myaccount.html', 
                         user=current_user, 
                         user_reviews=user_reviews,
                         purchases=purchases,
                         searched_user_id=current_user.id,
                         form=form)

@bp.route('/update-balance', methods=['POST'])
@login_required
def update_balance():
    try:
        amount = float(request.form.get('amount', 0))
        action = request.form.get('action', 'add')
        
        if amount <= 0:
            flash('Amount must be greater than 0', 'error')
            return redirect(url_for('users.my_account'))
            
        if action == 'withdraw' and current_user.balance < amount:
            flash('Insufficient funds', 'error')
            return redirect(url_for('users.my_account'))
            
        if current_user.update_balance(amount, action):
            updated_user = User.get(current_user.id)
            if updated_user:
                current_user.balance = updated_user.balance
            flash(f'Balance updated successfully! New balance: ${current_user.balance:.2f}', 'success')
        else:
            flash('Failed to update balance', 'error')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('users.my_account'))

@bp.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    order = Purchase.get(order_id)
    if not order or order.buyer_id != current_user.id:
        flash('Order not found', 'error')
        return redirect(url_for('users.my_account'))
    items = Purchase.get_items(order_id)
    return render_template('order_details.html', order=order, items=items)