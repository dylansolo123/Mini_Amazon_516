from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from .purchase import Purchase

from .. import login


class User(UserMixin):
    def __init__(self, user_id, email, full_name, address, balance, is_seller):
        self.id = user_id
        self.user_id = user_id
        self.email = email
        self.full_name = full_name
        self.address = address
        self.balance = balance
        self.is_seller = is_seller

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT user_id, email, full_name, address, balance, is_seller, password
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:
            return None
        elif not check_password_hash(rows[0][6], password):
            return None
        else:
            return User(*(rows[0][:-1]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, full_name, address, is_seller=True):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, full_name, address, balance, is_seller)
VALUES(:email, :password, :full_name, :address, 0.00, :is_seller)
RETURNING user_id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  full_name=full_name,
                                  address=address,
                                  is_seller=is_seller)
            user_id = rows[0][0]
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(user_id):
        rows = app.db.execute("""
SELECT user_id, email, full_name, address, balance, is_seller
FROM Users
WHERE user_id = :user_id
""",
                              user_id=user_id)
        return User(*(rows[0])) if rows else None

    def update_balance(self, amount, action='add'):
        try:
            amount = float(amount)
            if action == 'add':
                new_balance = float(self.balance) + amount
            elif action == 'withdraw':
                if float(self.balance) < amount:
                    raise Exception("Insufficient funds")
                new_balance = float(self.balance) - amount
            else:
                raise Exception("Invalid action")

            app.db.execute("""
UPDATE Users
SET balance = :new_balance
WHERE user_id = :user_id
""",
                              new_balance=new_balance,
                              user_id=self.user_id)
            
            self.balance = new_balance
            
            rows = app.db.execute("""
SELECT balance
FROM Users
WHERE user_id = :user_id
""",
                              user_id=self.user_id)
            
            if rows and float(rows[0][0]) == new_balance:
                return True
            else:
                raise Exception("Balance update verification failed")
                
        except Exception as e:
            raise Exception("Failed to update balance: " + str(e))

    @staticmethod
    def update_info(user_id, email, full_name, address, password=None):
        try:
            if email != User.get(user_id).email:
                if User.email_exists(email):
                    raise Exception("Email already in use")

            if password:
                app.db.execute("""
UPDATE Users
SET email = :email,
    full_name = :full_name,
    address = :address,
    password = :password
WHERE user_id = :user_id
""",
                    email=email,
                    full_name=full_name,
                    address=address,
                    password=generate_password_hash(password),
                    user_id=user_id)
            else:
                app.db.execute("""
UPDATE Users
SET email = :email,
    full_name = :full_name,
    address = :address
WHERE user_id = :user_id
""",
                    email=email,
                    full_name=full_name,
                    address=address,
                    user_id=user_id)
            return True
        except Exception as e:
            raise Exception("Failed to update user information: " + str(e))

    def get_purchase_history(self):
        """
        Retrieves the user's purchase history
        """
        since_date = datetime.now() - timedelta(days=365)
        return Purchase.get_all_by_buyer_since(self.user_id, since_date)

    def get_order_details(self, order_id):
        """
        Retrieves detailed information about a specific order
        """
        order = Purchase.get(order_id)
        if not order or order.buyer_id != self.user_id:
            return None

        items = Purchase.get_items(order_id)

        return {
            'order': order,
            'items': items
        }

    @staticmethod
    def get_seller_reviews(seller_id):
        rows = app.db.execute("""
SELECT review_id, seller_id, user_id, rating, review_text, review_date
FROM Seller_Reviews
WHERE seller_id = :seller_id
ORDER BY review_date DESC
""",
                              seller_id=seller_id)
        return rows

    def get_seller_inventory(self):
        """
        Retrieves all products in the seller's inventory.
        """
        if not self.is_seller:
            return []
        
        rows = app.db.execute("""
        SELECT p.product_id, p.name AS product_name, si.price, si.quantity
        FROM Seller_Inventory si
        JOIN Products p ON si.product_id = p.product_id
        WHERE si.seller_id = :seller_id
        """, seller_id=self.user_id)
        
        return [
            {
                'product_id': row[0],
                'product_name': row[1],
                'price': row[2],
                'quantity': row[3]
            } for row in rows
        ]