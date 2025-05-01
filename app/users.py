from flask import render_template, redirect, url_for, flash, request, Blueprint, session, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from .models.user import User
from .models.purchase import Purchase
from .models.product import Product
from .models.review import Review
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
    session.pop('_flashes', None)
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/sales')
@login_required
def sales():
    if not current_user.is_seller:
        return redirect(url_for('index.index')) 
    
    active_tab = request.args.get('tab', 'products')
    
    search_term = request.args.get('search', '')
    inventory_items = current_user.get_seller_inventory()
    
    seller_id = current_user.user_id
    
    seller_orders = User.get_seller_orders(seller_id)
    product_stats = User.get_product_sales_stats(seller_id)
    
    if search_term and active_tab == 'orders':
        filtered_orders = []
        for order in seller_orders:
            if (search_term.lower() in str(order['order_id']).lower() or
                search_term.lower() in order['buyer_name'].lower() or
                search_term.lower() in order['buyer_address'].lower()):
                filtered_orders.append(order)
        seller_orders = filtered_orders
    
    ratings_data = None
    top_buyers = None
    buyer_data = None
    
    if active_tab == 'analytics':
        try:
                        
            ratings_data = User.get_seller_ratings_distribution(seller_id)
            
            top_buyers = User.get_top_buyers(seller_id, limit=5)
            
            buyer_data = User.get_buyer_engagement_data(seller_id)
            
        except Exception as e:
            print(f"Error in analytics tab: {str(e)}")
            ratings_data = {'one_star': 0, 'two_star': 0, 'three_star': 0, 'four_star': 0, 'five_star': 0}
            top_buyers = []
            buyer_data = []
    
    return render_template('seller_dashboard.html', 
                          active_tab=active_tab,
                          inventory_items=inventory_items,
                          orders=seller_orders,
                          product_stats=product_stats,
                          ratings_data=ratings_data,
                          top_buyers=top_buyers,
                          buyer_data=buyer_data)

@bp.route('/my-products')
@login_required
def my_products():
    if not current_user.is_seller:
        flash('You must be a seller to view this page')
        return redirect(url_for('index.index'))
    
    products = Product.get_user_products(current_user.id)
    return render_template('my_products.html', products=products)

@bp.route('/create-product', methods=['GET', 'POST'])
@login_required
def create_product():
    if not current_user.is_seller:
        flash('You must be a seller to create products')
        return redirect(url_for('index.index'))
    
    categories = User.get_categories()
    
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
            
            # Create the product
            product_id = User.add_product(
                category_id=category_id,
                name=name,
                description=description,
                image_url=image_url or "https://via.placeholder.com/200",
                created_by=current_user.id,
                price=price,
                quantity=quantity
            )
            
            if product_id:
                flash('Product created successfully!')
                return redirect(url_for('users.sales'))
            else:
                flash('Failed to create product')
        except ValueError:
            flash('Invalid input. Please check your entries.')
        except Exception as e:
            flash(str(e))
    
    return render_template('create_product.html', categories=categories)

@bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_seller:
        flash('You must be a seller to edit products')
        return redirect(url_for('index.index'))
    
    product = Product.get(product_id)
    if not product or product.created_by != current_user.id:
        flash('Product not found or you do not have permission to edit it')
        return redirect(url_for('users.my_products'))
    
    categories = User.get_categories()
    inventory = User.get_inventory_item(current_user.id, product_id)
    
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
            
            # Update the product
            success = User.update_product_info(
                seller_id=current_user.id,
                product_id=product_id,
                name=name,
                price=price
            )
            
            if success:
                # Update inventory quantity
                User.update_inventory_quantity(
                    current_user.id,
                    product_id,
                    quantity
                )
                flash('Product updated successfully!')
                return redirect(url_for('users.sales'))
            else:
                flash('Failed to update product')
        except ValueError:
            flash('Invalid input. Please check your entries.')
        except Exception as e:
            flash(str(e))
    
    return render_template('edit_product.html', 
                         product=product,
                         categories=categories,
                         inventory=inventory)

@bp.route('/update-product-info', methods=['POST'])
@login_required
def update_product_info():
    if not current_user.is_seller:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        product_id = int(request.form.get('product_id'))
        name = request.form.get('name')
        price = request.form.get('price')
        
        if price:
            try:
                price = float(price)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid price format'}), 400
        
        success = User.update_product_info(
            seller_id=current_user.id,
            product_id=product_id,
            name=name if name else None,
            price=price if price else None
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to update product'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

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
    
    return redirect(url_for('users.sales', tab='orders'))

@bp.route('/update_inventory_quantity', methods=['POST'])
@login_required
def update_inventory_quantity():
    if not current_user.is_seller:
        return redirect(url_for('index.index'))
    
    product_id = request.form.get('product_id')
    new_quantity = request.form.get('quantity')
    
    try:
        product_id = int(product_id)
        new_quantity = int(new_quantity)
        
        if new_quantity < 0:
            flash('Quantity cannot be negative')
            return redirect(url_for('users.sales'))
            
        if User.update_inventory_quantity(current_user.user_id, product_id, new_quantity):
            flash('Inventory quantity updated successfully!')
        else:
            flash('Failed to update inventory quantity')
            
    except ValueError:
        flash('Invalid input values')
    except Exception as e:
        flash(str(e))
    
    return redirect(url_for('users.sales', tab='products'))

@bp.route('/remove_from_inventory', methods=['POST'])
@login_required
def remove_from_inventory():
    if not current_user.is_seller:
        return redirect(url_for('index.index'))
    
    product_id = request.form.get('product_id')
    delete_product = request.form.get('delete_product', 'false').lower() == 'true'
    
    try:
        product_id = int(product_id)
        if User.remove_from_inventory(current_user.user_id, product_id, delete_product):
            flash('Product removed from inventory successfully!')
        else:
            flash('Failed to remove product from inventory')
    except ValueError:
        flash('Invalid product ID')
    except Exception as e:
        flash(str(e))
    
    return redirect(url_for('users.sales', tab='products'))

@bp.route('/get-buyer-details/<int:buyer_id>')
@login_required
def get_buyer_details(buyer_id):
    if not current_user.is_seller:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        
        user = User.get(buyer_id)
        if not user:
            return jsonify({'error': 'Buyer not found in the system'}), 404
            
        print(f"Found buyer in database: {user.full_name}")
        
        buyer = User.get_buyer_info(current_user.user_id, buyer_id)
        if not buyer:
            buyer = {
                'user_id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'order_count': 0,
                'total_spent': 0.0,
                'last_order_date': None,
                'avg_rating': None
            }
        
        orders = User.get_buyer_orders(current_user.user_id, buyer_id) or []
        
        reviews = User.get_buyer_reviews(current_user.user_id, buyer_id) or []
        
        messages = User.get_buyer_messages(current_user.user_id, buyer_id) or []
        
        return jsonify({
            'buyer': buyer,
            'orders': orders,
            'reviews': reviews,
            'messages': messages
        })
        
    except Exception as e:
        print(f"Error getting buyer details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch buyer details: {str(e)}'}), 500

def get_recent_reviews_by_user_id_from_csv(user_id):
        reviews = []
        try:
            with open('reviews.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['user_id'] == str(user_id):
                        reviews.append(row)
        except FileNotFoundError:
            pass
        return reviews

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
                raise ValidationError('Email already in use.')

@bp.route('/my-account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = AccountUpdateForm()
    search_form = UserReviewSearchForm()
    searched_reviews = None
    searched_user_name = None

    if search_form.validate_on_submit():
        try:
            search_user_id = int(search_form.user_id.data)
            # Get user's name first
            user = User.get(search_user_id)
            if user:
                searched_reviews = Review.get_recent_reviews_by_user(search_user_id)
                searched_user_name = user.full_name
            else:
                flash('User not found', 'error')
        except ValueError:
            flash('Please enter a valid user ID', 'error')

    if form.validate_on_submit():
        if User.update_profile(
            current_user.id,
            form.email.data,
            form.full_name.data,
            form.address.data,
            form.password.data if form.password.data else None
        ):
            flash('Profile updated successfully!')
            return redirect(url_for('users.my_account'))
        else:
            flash('Failed to update profile')

    # Get user's purchases
    purchases = Purchase.get_all_by_uid_since(
        current_user.id,
        datetime.min
    )
    
    # Get user's reviews
    reviews = Review.get_user_reviews(current_user.id)

    return render_template(
        'myaccount.html',
        title='My Account',
        user=current_user,
        form=form,
        search_form=search_form,
        purchases=purchases,
        reviews=reviews,
        searched_reviews=searched_reviews,
        searched_user_name=searched_user_name
    )

@bp.route('/update-balance', methods=['POST'])
@login_required
def update_balance():
    amount = request.form.get('amount', type=float)
    action = request.form.get('action', 'add')
    
    if not amount or amount <= 0:
        flash('Please enter a valid amount')
        return redirect(url_for('users.my_account'))
    
    try:
        current_user.update_balance(amount, action)
        flash(f'Balance {"added" if action == "add" else "withdrawn"} successfully!')
    except Exception as e:
        flash(str(e))
    
    return redirect(url_for('users.my_account'))

@bp.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    order_info = current_user.get_order_details(order_id)
    if not order_info:
        flash('Order not found')
        return redirect(url_for('users.my_account'))
    
    return render_template('order_details.html',
                         order=order_info['order'],
                         items=order_info['items'])

@bp.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    try:
        # Get the review first to verify ownership
        review = Review.get(review_id)
        
        if not review:
            flash('Review not found', 'error')
            return redirect(url_for('users.my_account'))
            
        # Check if the review belongs to the current user
        if review.user_id != current_user.id:
            flash('You do not have permission to delete this review', 'error')
            return redirect(url_for('users.my_account'))
            
        # Delete the review
        if Review.delete(review_id):
            flash('Review deleted successfully', 'success')
        else:
            flash('Failed to delete review', 'error')
            
    except Exception as e:
        print(f"Error deleting review: {str(e)}")
        flash('An error occurred while deleting the review', 'error')
        
    return redirect(url_for('users.my_account'))

@bp.route('/review/<int:review_id>/edit', methods=['POST'])
@login_required
def edit_review(review_id):
    try:
        # Get the review first to verify ownership
        review = Review.get(review_id)
        
        if not review:
            flash('Review not found', 'error')
            return redirect(url_for('users.my_account'))
            
        # Check if the review belongs to the current user
        if review.user_id != current_user.id:
            flash('You do not have permission to edit this review', 'error')
            return redirect(url_for('users.my_account'))
            
        # Get the updated review data
        rating = int(request.form.get('rating'))
        review_text = request.form.get('review_text')
        
        # Validate the rating
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5', 'error')
            return redirect(url_for('users.my_account'))
            
        # Update the review
        if Review.update(review_id, rating, review_text):
            flash('Review updated successfully', 'success')
        else:
            flash('Failed to update review', 'error')
            
    except Exception as e:
        print(f"Error updating review: {str(e)}")
        flash('An error occurred while updating the review', 'error')
        
    return redirect(url_for('users.my_account'))