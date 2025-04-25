from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from .models.cart import Cart
from .models.purchase import Purchase
from .models.user import User

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def cart_page():
    """
    Display the user's cart
    """
    if current_user.is_authenticated:
        cart_items = Cart.get_cart_items(current_user.id)
        total = sum(item['total_price'] for item in cart_items)
        item_count = Cart.get_cart_count(current_user.id)
    else:
        # For non-logged in users, we display an empty cart
        cart_items = []
        total = 0
        item_count = 0
        
    return render_template('cart.html',
                           cart_items=cart_items,
                           total=total,
                           item_count=item_count)

@cart_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """
    Add a product to the cart
    """
    product_id = int(request.form.get('product_id'))
    seller_id = int(request.form.get('seller_id'))
    quantity = int(request.form.get('quantity', 1))
    
    # Validate quantity
    if quantity <= 0:
        flash('Quantity must be at least 1', 'danger')
        return redirect(request.referrer)
    
    # Add to cart
    success = Cart.add_to_cart(current_user.id, product_id, seller_id, quantity)
    
    if success:
        flash('Item added to cart successfully', 'success')
    else:
        flash('Failed to add item to cart', 'danger')
    
    # Redirect back to the referring page
    return redirect(request.referrer or url_for('index.index'))

@cart_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    """
    Update the quantity of an item in the cart
    """
    cart_item_id = int(request.form.get('cart_item_id'))
    quantity = int(request.form.get('quantity'))
    
    success = Cart.update_quantity(current_user.id, cart_item_id, quantity)
    
    if success:
        if quantity <= 0:
            flash('Item removed from cart', 'success')
        else:
            flash('Cart updated successfully', 'success')
    else:
        flash('Failed to update cart', 'danger')
    
    return redirect(url_for('cart.cart_page'))

@cart_bp.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    """
    Remove an item from the cart
    """
    cart_item_id = int(request.form.get('cart_item_id'))
    
    success = Cart.remove_item(current_user.id, cart_item_id)
    
    if success:
        flash('Item removed from cart', 'success')
    else:
        flash('Failed to remove item from cart', 'danger')
    
    return redirect(url_for('cart.cart_page'))

@cart_bp.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    """
    Clear all items from the cart
    """
    success = Cart.clear_cart(current_user.id)

    if success:
        flash('Cart cleared', 'success')
    else:
        flash('Failed to clear cart', 'danger')

    return redirect(url_for('cart.cart_page')) 


@cart_bp.route("/checkout/page", methods=["GET"])
@login_required
def checkout_page():
    """Checkout page confirmation"""
    cart_items = Cart.get_cart_items(current_user.id)
    total = sum(item["total_price"] for item in cart_items)
    item_count = Cart.get_cart_count(current_user.id)
    current_balance = current_user.balance

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total,
        item_count=item_count,
        current_balance=current_balance,
    )


@cart_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """Checkout items from cart"""
    cart_items = Cart.get_cart_items(current_user.id)
    total = sum(item["total_price"] for item in cart_items)
    current_balance = current_user.balance

    if current_balance > total:
        try:
            # create order
            order_id = Purchase.add_purchase(current_user.id, total)

            # add cart items as order items
            for item in cart_items:
                Purchase.add_order_item(
                    order_id=order_id,
                    seller_id=item["seller_id"],
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                )

            # clear cart
            Cart.clear_cart(current_user.id)

            # subtract total from user balance
            current_user.update_balance(total, "withdraw")

            # redirect to newly created order page
            return redirect(url_for("users.order_details", order_id=order_id))

        except Exception as e:
            flash(f"Error processing order: {str(e)}")
            return redirect(url_for("cart.checkout_page"))

    else:
        return render_template(
            "purchase_failed.html",
        )
