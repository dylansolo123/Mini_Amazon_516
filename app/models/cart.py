from flask import current_app as app
from flask_login import current_user


class Cart:
    def __init__(self, cart_id, user_id, updated_at):
        self.cart_id = cart_id
        self.user_id = user_id
        self.updated_at = updated_at

    @staticmethod
    def get_by_user_id(user_id):
        """
        Get cart by user_id or create one if it doesn't exist
        """
        rows = app.db.execute('''
        SELECT cart_id, user_id, updated_at
        FROM Carts
        WHERE user_id = :user_id
        ''', user_id=user_id)

        if rows:
            return Cart(*(rows[0]))
        else:
            # Create a new cart for this user
            rows = app.db.execute('''
            INSERT INTO Carts(user_id)
            VALUES(:user_id)
            RETURNING cart_id, user_id, updated_at
            ''', user_id=user_id)
            return Cart(*(rows[0]))

    @staticmethod
    def get_cart_items(user_id):
        """
        Get all items in a user's cart
        Returns a list of dictionaries containing information about the items in the cart
        """

        # Get cart object for this user
        cart = Cart.get_by_user_id(user_id)

        # Get all items in this cart with product and seller information
        rows = app.db.execute('''
        SELECT ci.cart_item_id, ci.product_id, p.name AS product_name, p.image_url,
               ci.seller_id, u.full_name AS seller_name, 
               ci.quantity, ci.unit_price, 
               (ci.quantity * ci.unit_price) AS total_price
        FROM Cart_Items ci
        JOIN Products p ON ci.product_id = p.product_id
        JOIN Users u ON ci.seller_id = u.user_id
        WHERE ci.cart_id = :cart_id
        ORDER BY ci.added_at DESC
        ''', cart_id=cart.cart_id)

        return [
            {
                'cart_item_id': row[0],
                'product_id': row[1],
                'product_name': row[2],
                'image_url': row[3],
                'seller_id': row[4],
                'seller_name': row[5],
                'quantity': row[6],
                'unit_price': row[7],
                'total_price': row[8]
            } for row in rows
        ]

    @staticmethod
    def get_cart_count(user_id):
        """
        Get number of items in a user's cart
        """
        cart = Cart.get_by_user_id(user_id)
        rows = app.db.execute('''
        SELECT SUM(quantity)
        FROM Cart_Items
        WHERE cart_id = :cart_id
        ''', cart_id=cart.cart_id)

        return rows[0][0] if rows and rows[0][0] else 0

    @staticmethod
    def add_to_cart(user_id, product_id, seller_id, quantity):
        """
        Add an item to the cart or update quantity if it already exists
        
        Returns true if successful and false otherwise
        """
        cart = Cart.get_by_user_id(user_id)

        # Check if product already exists in the cart from the same seller
        rows = app.db.execute('''
        SELECT cart_item_id, quantity
        FROM Cart_Items
        WHERE cart_id = :cart_id AND product_id = :product_id AND seller_id = :seller_id
        ''', cart_id=cart.cart_id, product_id=product_id, seller_id=seller_id)

        # Get the current price of the product from the seller's inventory
        price_rows = app.db.execute('''
        SELECT price
        FROM Seller_Inventory
        WHERE seller_id = :seller_id AND product_id = :product_id
        ''', seller_id=seller_id, product_id=product_id)

        if not price_rows:
            return False  # Product not found in seller's inventory

        unit_price = price_rows[0][0]

        if rows:
            # Update the quantity if the item already exists
            cart_item_id = rows[0][0]
            current_quantity = rows[0][1]
            new_quantity = current_quantity + quantity

            app.db.execute('''
            UPDATE Cart_Items
            SET quantity = :quantity, unit_price = :unit_price, added_at = CURRENT_TIMESTAMP
            WHERE cart_item_id = :cart_item_id
            ''', quantity=new_quantity, unit_price=unit_price, cart_item_id=cart_item_id)
        else:
            # Add the new item to the cart
            app.db.execute('''
            INSERT INTO Cart_Items(cart_id, seller_id, product_id, quantity, unit_price)
            VALUES(:cart_id, :seller_id, :product_id, :quantity, :unit_price)
            ''', cart_id=cart.cart_id, seller_id=seller_id, product_id=product_id, 
                 quantity=quantity, unit_price=unit_price)

        # Update the cart's updated_at timestamp
        app.db.execute('''
        UPDATE Carts
        SET updated_at = CURRENT_TIMESTAMP
        WHERE cart_id = :cart_id
        ''', cart_id=cart.cart_id)

        return True

    @staticmethod
    def update_quantity(user_id, cart_item_id, quantity):
        """
        Update the quantity of an item in the cart
        
        Returns:
        True if successful, False otherwise
        """
        cart = Cart.get_by_user_id(user_id)

        if quantity <= 0:
            return Cart.remove_item(user_id, cart_item_id)

        # Check if the cart item belongs to the user's cart
        rows = app.db.execute('''
        SELECT ci.cart_item_id
        FROM Cart_Items ci
        JOIN Carts c ON ci.cart_id = c.cart_id
        WHERE ci.cart_item_id = :cart_item_id AND c.user_id = :user_id
        ''', cart_item_id=cart_item_id, user_id=user_id)

        if not rows:
            return False  # Cart item not found or doesn't belong to user

        # Update the quantity
        app.db.execute('''
        UPDATE Cart_Items
        SET quantity = :quantity, added_at = CURRENT_TIMESTAMP
        WHERE cart_item_id = :cart_item_id
        ''', quantity=quantity, cart_item_id=cart_item_id)

        # Update the cart's updated_at timestamp
        app.db.execute('''
        UPDATE Carts
        SET updated_at = CURRENT_TIMESTAMP
        WHERE cart_id = :cart_id
        ''', cart_id=cart.cart_id)

        return True

    @staticmethod
    def remove_item(user_id, cart_item_id):
        """
        Remove an item from the cart
        
        Returns:
        True if successful, False otherwise
        """
        cart = Cart.get_by_user_id(user_id)

        # Check if the cart item belongs to the user's cart
        rows = app.db.execute('''
        SELECT ci.cart_item_id
        FROM Cart_Items ci
        JOIN Carts c ON ci.cart_id = c.cart_id
        WHERE ci.cart_item_id = :cart_item_id AND c.user_id = :user_id
        ''', cart_item_id=cart_item_id, user_id=user_id)

        if not rows:
            return False  # Cart item not found or doesn't belong to user

        # Remove the item
        app.db.execute('''
        DELETE FROM Cart_Items
        WHERE cart_item_id = :cart_item_id
        ''', cart_item_id=cart_item_id)

        # Update the cart's updated_at timestamp
        app.db.execute('''
        UPDATE Carts
        SET updated_at = CURRENT_TIMESTAMP
        WHERE cart_id = :cart_id
        ''', cart_id=cart.cart_id)

        return True

    @staticmethod
    def clear_cart(user_id):
        """
        Remove all items from the cart
        
        Returns:
        True if successful, False otherwise
        """
        cart = Cart.get_by_user_id(user_id)

        # Remove all items
        app.db.execute('''
        DELETE FROM Cart_Items
        WHERE cart_id = :cart_id
        ''', cart_id=cart.cart_id)

        # Update the cart's updated_at timestamp
        app.db.execute('''
        UPDATE Carts
        SET updated_at = CURRENT_TIMESTAMP
        WHERE cart_id = :cart_id
        ''', cart_id=cart.cart_id)

        return True 

    @staticmethod
    def checkout_cart(user_id, cart_items):
        return True
