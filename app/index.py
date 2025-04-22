from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
import datetime
from decimal import Decimal

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    try:
        # Get categories
        categories = Product.get_categories()
        
        # Get featured products (latest 4 products)
        featured_result = Product.get_all(
            page=1, 
            per_page=4
        )
        featured_products = []
        if featured_result and 'products' in featured_result:
            featured_products = [p for p in featured_result['products'] if p is not None]
        
        # Get top deals (k most expensive products with calculated discount)
        k = 4  # Number of top deals to show
        top_deals = []
        expensive_products = Product.get_top_k_expensive(k)
        for product in expensive_products:
            if product is not None and product.price is not None:
                try:
                    product.original_price = product.price + (product.price * Decimal('0.2'))
                    top_deals.append(product)
                except (TypeError, ValueError, AttributeError) as e:
                    print(f"Error calculating original price: {str(e)}")
                    continue
        
        # Initialize variables for authenticated users
        recommended_products = []
        purchases = None
        
        if current_user.is_authenticated:
            # Get recommended products (can be customized based on user preferences)
            recommended_result = Product.get_all(
                page=1,
                per_page=5
            )
            if recommended_result and 'products' in recommended_result:
                recommended_products = [p for p in recommended_result['products'] if p is not None]
            
            # Get recent purchases (last 30 days)
            try:
                purchases = Purchase.get_all_by_uid_since(
                    current_user.id,
                    datetime.datetime.now() - datetime.timedelta(days=30)
                )
            except Exception as e:
                print(f"Error getting recent purchases: {str(e)}")
                purchases = None
        
        return render_template('index.html',
                             categories=categories or [],
                             featured_products=featured_products,
                             top_deals=top_deals[:k],
                             recommended_products=recommended_products,
                             purchase_history=purchases)
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        flash('An error occurred while loading the page. Please try again later.', 'error')
        return render_template('index.html',
                             categories=[],
                             featured_products=[],
                             top_deals=[],
                             recommended_products=[],
                             purchase_history=None)

@bp.route('/products')
def products():
    try:
        # Get and validate parameters
        category_id = request.args.get('category_id', type=int)
        search_query = request.args.get('search', type=str)
        sort_price = request.args.get('sort_price')
        top_k = request.args.get('top_k', type=int)

        # Validate page number
        try:
            page = max(1, int(request.args.get('page', 1)))
        except (TypeError, ValueError):
            page = 1

        # Validate and process top_k parameter
        if top_k is not None:
            try:
                top_k = max(1, min(100, int(top_k)))  # Limit between 1 and 100
                page = 1  # Reset to first page when using top_k
            except (TypeError, ValueError):
                top_k = None
                flash('Invalid number for top products. Showing all products instead.', 'warning')

        # Set items per page
        per_page = 20 if not top_k else top_k

        # Validate sort_price parameter
        if sort_price not in ['ASC', 'DESC', None]:
            sort_price = None

        # Force DESC sort for top_k
        if top_k:
            sort_price = 'DESC'

        # Get products with all filters applied
        result = Product.get_all(
            category_id=category_id,
            search_query=search_query,
            sort_by_price=sort_price,
            page=page,
            per_page=per_page,
            top_k=top_k
        )

        # Get categories for filter dropdown
        try:
            categories = Product.get_categories()
        except Exception as e:
            print(f"Error getting categories: {str(e)}")
            categories = []
            flash('Error loading categories. Please try again later.', 'warning')

        # Handle case where no products are found
        if not result:
            result = {
                'products': [],
                'total_pages': 1,
                'current_page': 1,
                'total_count': 0
            }

        # Calculate pagination parameters
        current_page = result.get('current_page', 1)
        total_pages = result.get('total_pages', 1)
        
        # Show 5 pages before and after current page
        start_page = max(1, current_page - 5)
        end_page = min(total_pages, current_page + 5)

        return render_template('products.html',
                             avail_products=result.get('products', []),
                             categories=categories or [],
                             current_category=category_id,
                             search_query=search_query,
                             sort_price=sort_price,
                             top_k=top_k,
                             pagination={
                                 'current_page': current_page,
                                 'total_pages': total_pages,
                                 'total_count': result.get('total_count', 0),
                                 'start_page': start_page,
                                 'end_page': end_page
                             })
    except Exception as e:
        print(f"Error in products route: {str(e)}")
        flash('An error occurred while loading the products. Please try again later.', 'error')
        return redirect(url_for('index.index'))

@bp.route('/product/<int:product_id>')
def product_details(product_id):
    try:
        # Get detailed product information
        product = Product.get_product_details(product_id)
        if not product:
            flash('Product not found', 'error')
            return redirect(url_for('index.products'))

        # Get similar products from the same category
        similar_products = []
        if product.category_id:
            similar_result = Product.get_all(
                category_id=product.category_id,
                page=1,
                per_page=4
            )
            if similar_result and 'products' in similar_result:
                similar_products = [p for p in similar_result['products'] 
                                  if p is not None and p.id != product_id]

        return render_template('product_details.html',
                             product=product,
                             similar_products=similar_products[:4])
    except Exception as e:
        print(f"Error in product_details route: {str(e)}")
        flash('An error occurred while loading the product details. Please try again later.', 'error')
        return redirect(url_for('index.products'))

@bp.route('/orders')
@login_required
def orders():
    try:
        # Get all user's purchases
        purchases = Purchase.get_all_by_uid_since(
            current_user.id,
            datetime.datetime.min
        )

        # Group purchases by fulfillment status
        grouped_purchases = {
            'Pending': [],
            'Partially Fulfilled': [],
            'Fulfilled': [],
            'Cancelled': []
        }

        if purchases:
            for purchase in purchases:
                status = purchase.fulfillment_status
                if status in grouped_purchases:
                    grouped_purchases[status].append(purchase)

        return render_template('orders.html',
                             purchases=purchases or [],
                             grouped_purchases=grouped_purchases)
    except Exception as e:
        print(f"Error in orders route: {str(e)}")
        flash('An error occurred while loading your orders. Please try again later.', 'error')
        return redirect(url_for('index.index'))

@bp.route('/api/products/search')
def search_products():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([])

        # Get matching products
        result = Product.get_all(
            search_query=query,
            page=1,
            per_page=10
        )

        if not result or 'products' not in result:
            return jsonify([])

        # Format products for response
        products = []
        for product in result['products']:
            if product:
                products.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price) if product.price else None,
                    'image_url': product.image_url
                })

        return jsonify(products)
    except Exception as e:
        print(f"Error in search_products: {str(e)}")
        return jsonify([])

@bp.route('/api/categories')
def get_categories():
    try:
        categories = Product.get_categories()
        return jsonify([{
            'id': cat[0],
            'name': cat[1]
        } for cat in categories])
    except Exception as e:
        print(f"Error in get_categories: {str(e)}")
        return jsonify([])