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
FROM users
WHERE email = :email
""",
                              email=email)
        print(rows)
        if not rows:  # email not found
            return None
        elif rows[0][6] != password:
            # incorrect password
            return None
        else:
            return User(*(rows[0][:-1]))  # Exclude password from User object

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
                                  password=password,
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
                    password=password,
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

    @staticmethod
    def get_categories():
        """
        Get all product categories for dropdown menu
        """
        rows = app.db.execute("""
        SELECT category_id, category_name 
        FROM Product_Categories 
        ORDER BY category_name
        """)
        
        return rows

    @staticmethod
    def add_product(category_id, name, description, image_url, created_by, price, quantity):
        """
        Add a new product and add it to seller's inventory
        """
        product_id = app.db.execute("""
        INSERT INTO Products(category_id, name, description, image_url, created_by)
        VALUES(:category_id, :name, :description, :image_url, :created_by)
        RETURNING product_id
        """, 
        category_id=category_id,
        name=name,
        description=description,
        image_url=image_url,
        created_by=created_by)
        
        product_id = product_id[0][0]
        
        app.db.execute("""
        INSERT INTO Seller_Inventory(seller_id, product_id, price, quantity)
        VALUES(:seller_id, :product_id, :price, :quantity)
        """,
        seller_id=created_by,
        product_id=product_id,
        price=price,
        quantity=quantity)
        
        return product_id

    @staticmethod
    def update_inventory_quantity(seller_id, product_id, new_quantity):
        try:
            app.db.execute("""
            UPDATE Seller_Inventory
            SET quantity = :new_quantity
            WHERE seller_id = :seller_id
            AND product_id = :product_id
            """,
            seller_id=seller_id,
            product_id=product_id,
            new_quantity=new_quantity)
            return True
        except Exception as e:
            print(str(e))
            return False

    @staticmethod
    def remove_from_inventory(seller_id, product_id, delete_product=False):
        try:
            app.db.execute("BEGIN")
            
            # First remove from Seller_Inventory
            app.db.execute("""
            DELETE FROM Seller_Inventory
            WHERE seller_id = :seller_id
            AND product_id = :product_id
            """,
            seller_id=seller_id,
            product_id=product_id)
            
            # If delete_product is true, forcibly delete from all related tables first
            if delete_product:
                # Delete from Cart_Items
                app.db.execute("""
                DELETE FROM Cart_Items 
                WHERE product_id = :product_id
                """, 
                product_id=product_id)
                
                # Delete from Product_Reviews
                app.db.execute("""
                DELETE FROM Product_Reviews 
                WHERE product_id = :product_id
                """, 
                product_id=product_id)
                
                # Delete from Order_Items (even though it might not be ideal for record-keeping)
                app.db.execute("""
                DELETE FROM Order_Items 
                WHERE product_id = :product_id
                """, 
                product_id=product_id)
                
                # Finally delete the product itself
                app.db.execute("""
                DELETE FROM Products
                WHERE product_id = :product_id
                AND created_by = :seller_id
                """,
                seller_id=seller_id,
                product_id=product_id)
            
            app.db.execute("COMMIT")
            return True
        except Exception as e:
            app.db.execute("ROLLBACK")
            print(str(e))
            return False

    @staticmethod
    def get_inventory_item(seller_id, product_id):
        try:
            rows = app.db.execute("""
            SELECT quantity
            FROM Seller_Inventory
            WHERE seller_id = :seller_id
            AND product_id = :product_id
            """,
            seller_id=seller_id,
            product_id=product_id)
            
            return rows[0][0] if rows else None
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def get_seller_orders(seller_id):
        """Get all orders that contain items sold by this seller"""
        rows = app.db.execute("""
        WITH seller_order_items AS (
            SELECT oi.order_id,
                   COUNT(*) as total_items,
                   SUM(CASE WHEN oi.fulfillment_status = 'Fulfilled' THEN 1 ELSE 0 END) as fulfilled_items,
                   SUM(oi.quantity * oi.unit_price) as seller_total,
                   array_agg(json_build_object(
                       'order_item_id', oi.order_item_id,
                       'product_name', p.name,
                       'quantity', oi.quantity,
                       'unit_price', oi.unit_price,
                       'subtotal', oi.quantity * oi.unit_price,
                       'status', oi.fulfillment_status
                   )) as order_items
            FROM Order_Items oi
            JOIN Products p ON oi.product_id = p.product_id
            WHERE oi.seller_id = :seller_id
            GROUP BY oi.order_id
        )
        SELECT o.order_id,
               o.order_date,
               u.full_name as buyer_name,
               u.address as buyer_address,
               soi.total_items,
               soi.fulfilled_items,
               soi.seller_total,
               CASE 
                   WHEN soi.fulfilled_items = 0 THEN 'Pending'
                   WHEN soi.fulfilled_items = soi.total_items THEN 'Fulfilled'
                   ELSE 'Partially Fulfilled'
               END as status,
               soi.order_items
        FROM Orders o
        JOIN Users u ON o.buyer_id = u.user_id
        JOIN seller_order_items soi ON o.order_id = soi.order_id
        ORDER BY o.order_date DESC
        """,
        seller_id=seller_id)
        
        return [
            {
                'order_id': row[0],
                'order_date': row[1],
                'buyer_name': row[2],
                'buyer_address': row[3],
                'total_items': row[4],
                'fulfilled_items': row[5],
                'seller_total': row[6],
                'status': row[7],
                'order_items': row[8]
            } for row in rows
        ]

    @staticmethod
    def get_seller_order_items(seller_id, order_id):
        rows = app.db.execute("""
        SELECT oi.order_item_id,
               p.name as product_name,
               oi.quantity,
               oi.unit_price,
               oi.fulfillment_status,
               oi.fulfillment_date
        FROM Order_Items oi
        JOIN Products p ON oi.product_id = p.product_id
        WHERE oi.seller_id = :seller_id
        AND oi.order_id = :order_id
        """,
        seller_id=seller_id,
        order_id=order_id)
        
        return rows

    @staticmethod
    def fulfill_order_item(seller_id, order_item_id):
        try:
            rows = app.db.execute("""
            UPDATE Order_Items
            SET fulfillment_status = 'Fulfilled',
                fulfillment_date = CURRENT_TIMESTAMP
            WHERE order_item_id = :order_item_id
            AND seller_id = :seller_id
            AND fulfillment_status != 'Fulfilled'
            RETURNING order_item_id
            """,
            order_item_id=order_item_id,
            seller_id=seller_id)
            
            return bool(rows)
        except Exception as e:
            print(str(e))
            return False

    @staticmethod
    def update_product_info(seller_id, product_id, name=None, price=None):
        """
        Update product name and/or price for a seller's product
        """
        try:
            if name is not None:
                app.db.execute("""
                UPDATE Products
                SET name = :name
                WHERE product_id = :product_id
                AND created_by = :seller_id
                """,
                name=name,
                product_id=product_id,
                seller_id=seller_id)
            
            if price is not None:
                app.db.execute("""
                UPDATE Seller_Inventory
                SET price = :price
                WHERE product_id = :product_id
                AND seller_id = :seller_id
                """,
                price=price,
                product_id=product_id,
                seller_id=seller_id)
            
            return True
        except Exception as e:
            print(str(e))
            return False
    
    @staticmethod
    def get_product_sales_stats(seller_id):
        """
        Get sales statistics for products sold by this seller
        """
        try:
            rows = app.db.execute("""
            SELECT p.product_id, 
                p.name AS product_name, 
                si.quantity AS current_quantity,
                COALESCE(SUM(oi.quantity), 0) AS quantity_sold,
                COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_sales
            FROM Seller_Inventory si
            JOIN Products p ON si.product_id = p.product_id
            LEFT JOIN Order_Items oi ON oi.product_id = si.product_id 
                                    AND oi.seller_id = si.seller_id
            WHERE si.seller_id = :seller_id
            GROUP BY p.product_id, p.name, si.quantity
            ORDER BY total_sales DESC
            """, seller_id=seller_id)
            
            return [
                {
                    'product_id': row[0],
                    'product_name': row[1],
                    'current_quantity': row[2],
                    'quantity_sold': row[3],
                    'total_sales': row[4]
                } for row in rows
            ]
        except Exception as e:
            print(str(e))
            return []

    #need to get buyer analytics
    @staticmethod
    def get_buyer_info(seller_id, buyer_id):
        """
        Get buyer information for a specific seller
        """
        try:
            rows = app.db.execute("""
            WITH buyer_data AS (
                SELECT 
                    u.user_id,
                    u.email,
                    u.full_name,
                    COUNT(DISTINCT o.order_id) AS order_count,
                    SUM(oi.quantity * oi.unit_price) AS total_spent,
                    MAX(o.order_date) AS last_order_date
                FROM Users u
                JOIN Orders o ON u.user_id = o.buyer_id
                JOIN Order_Items oi ON o.order_id = oi.order_id
                WHERE oi.seller_id = :seller_id AND u.user_id = :buyer_id
                GROUP BY u.user_id, u.email, u.full_name
            ),
            buyer_ratings AS (
                SELECT 
                    AVG(pr.rating) AS avg_rating
                FROM Product_Reviews pr
                JOIN Order_Items oi ON pr.product_id = oi.product_id
                WHERE oi.seller_id = :seller_id AND pr.user_id = :buyer_id
            )
            SELECT 
                bd.user_id,
                bd.email,
                bd.full_name,
                bd.order_count,
                bd.total_spent,
                bd.last_order_date,
                br.avg_rating
            FROM buyer_data bd, buyer_ratings br
            """, seller_id=seller_id, buyer_id=buyer_id)
            
            if not rows:
                return None
                
            return {
                'user_id': rows[0][0],
                'email': rows[0][1],
                'full_name': rows[0][2],
                'order_count': rows[0][3],
                'total_spent': float(rows[0][4]) if rows[0][4] else 0.0,
                'last_order_date': rows[0][5],
                'avg_rating': float(rows[0][6]) if rows[0][6] else None
            }
        except Exception as e:
            print(f"Error getting buyer info: {str(e)}")
            return None
            
    @staticmethod
    def get_buyer_orders(seller_id, buyer_id):
        """
        Get orders made by a specific buyer from a specific seller
        """
        try:
            rows = app.db.execute("""
            WITH seller_items AS (
                SELECT 
                    oi.order_id,
                    COUNT(oi.order_item_id) AS item_count,
                    SUM(oi.quantity * oi.unit_price) AS total,
                    CASE 
                        WHEN SUM(CASE WHEN oi.fulfillment_status = 'Fulfilled' THEN 1 ELSE 0 END) = COUNT(*) THEN 'Fulfilled'
                        WHEN SUM(CASE WHEN oi.fulfillment_status = 'Fulfilled' THEN 1 ELSE 0 END) > 0 THEN 'Partially Fulfilled'
                        ELSE 'Pending'
                    END AS status
                FROM Order_Items oi
                WHERE oi.seller_id = :seller_id
                GROUP BY oi.order_id
            )
            SELECT 
                o.order_id,
                o.order_date,
                si.item_count,
                si.total,
                si.status
            FROM Orders o
            JOIN seller_items si ON o.order_id = si.order_id
            WHERE o.buyer_id = :buyer_id
            ORDER BY o.order_date DESC
            LIMIT 10
            """, seller_id=seller_id, buyer_id=buyer_id)
            
            return [
                {
                    'order_id': row[0],
                    'order_date': row[1],
                    'item_count': row[2],
                    'total': float(row[3]),
                    'status': row[4]
                } for row in rows
            ]
        except Exception as e:
            print(f"Error getting buyer orders: {str(e)}")
            return []
            
    @staticmethod
    def get_buyer_reviews(seller_id, buyer_id):
        """
        Get reviews left by a specific buyer for products from a specific seller
        """
        try:
            rows = app.db.execute("""
            SELECT 
                pr.review_id,
                p.product_id,
                p.name AS product_name,
                pr.rating,
                pr.review_text,
                pr.review_date
            FROM Product_Reviews pr
            JOIN Products p ON pr.product_id = p.product_id
            JOIN Seller_Inventory si ON p.product_id = si.product_id
            WHERE si.seller_id = :seller_id
            AND pr.user_id = :buyer_id
            ORDER BY pr.review_date DESC
            """, seller_id=seller_id, buyer_id=buyer_id)
            
            return [
                {
                    'review_id': row[0],
                    'product_id': row[1],
                    'product_name': row[2],
                    'rating': row[3],
                    'review_text': row[4],
                    'review_date': row[5]
                } for row in rows
            ]
        except Exception as e:
            print(f"Error getting buyer reviews: {str(e)}")
            return []

    @staticmethod
    def get_seller_ratings_distribution(seller_id):
        """
        Get distribution of ratings for a seller
        """
        try:
            rows = app.db.execute("""
            WITH rating_counts AS (
                SELECT 
                    COUNT(CASE WHEN rating = 1 THEN 1 END) AS one_star,
                    COUNT(CASE WHEN rating = 2 THEN 1 END) AS two_star,
                    COUNT(CASE WHEN rating = 3 THEN 1 END) AS three_star,
                    COUNT(CASE WHEN rating = 4 THEN 1 END) AS four_star,
                    COUNT(CASE WHEN rating = 5 THEN 1 END) AS five_star
                FROM Product_Reviews pr
                JOIN Order_Items oi ON pr.product_id = oi.product_id
                WHERE oi.seller_id = :seller_id
            )
            SELECT 
                COALESCE(one_star, 0) AS one_star,
                COALESCE(two_star, 0) AS two_star,
                COALESCE(three_star, 0) AS three_star,
                COALESCE(four_star, 0) AS four_star,
                COALESCE(five_star, 0) AS five_star
            FROM rating_counts
            """, seller_id=seller_id)
            
            if not rows:
                return {
                    'one_star': 0,
                    'two_star': 0,
                    'three_star': 0,
                    'four_star': 0,
                    'five_star': 0
                }
                
            return {
                'one_star': rows[0][0],
                'two_star': rows[0][1],
                'three_star': rows[0][2],
                'four_star': rows[0][3],
                'five_star': rows[0][4]
            }
        except Exception as e:
            print(f"Error getting ratings distribution: {str(e)}")
            return {
                'one_star': 0,
                'two_star': 0,
                'three_star': 0,
                'four_star': 0,
                'five_star': 0
            }

    @staticmethod
    def get_top_buyers(seller_id, limit=5):
        """
        Get top buyers by total orders/purchases from this seller
        """
        try:
            rows = app.db.execute("""
            SELECT 
                o.buyer_id,
                u.full_name AS buyer_name,
                COUNT(DISTINCT o.order_id) AS total_orders,
                SUM(oi.quantity * oi.unit_price) AS total_spent
            FROM Orders o
            JOIN Users u ON o.buyer_id = u.user_id
            JOIN Order_Items oi ON o.order_id = oi.order_id
            WHERE oi.seller_id = :seller_id
            GROUP BY o.buyer_id, u.full_name
            ORDER BY total_orders DESC, total_spent DESC
            LIMIT :limit
            """, seller_id=seller_id, limit=limit)
            
            return [
                {
                    'buyer_id': row[0],
                    'buyer_name': row[1],
                    'total_orders': row[2],
                    'total_spent': row[3]
                } for row in rows
            ]
        except Exception as e:
            print(f"Error getting top buyers: {str(e)}")
            return []
    
    @staticmethod
    def get_buyer_engagement_data(seller_id):
        """
        Get comprehensive data about buyers who have interacted with this seller
        including orders, messages, and ratings
        """
        try:
            effective_seller_id = User.get_effective_seller_id(seller_id)
            
            rows = app.db.execute("""
            WITH buyer_orders AS (
                SELECT 
                    o.buyer_id,
                    u.full_name AS buyer_name,
                    COUNT(DISTINCT o.order_id) AS total_orders,
                    MAX(o.order_date) AS last_purchase,
                    SUM(oi.quantity * oi.unit_price) AS total_spent
                FROM Orders o
                JOIN Users u ON o.buyer_id = u.user_id
                JOIN Order_Items oi ON o.order_id = oi.order_id
                WHERE oi.seller_id = :seller_id
                GROUP BY o.buyer_id, u.full_name
            ),
            buyer_messages AS (
                SELECT 
                    mt.buyer_id AS user_id,
                    COUNT(m.message_id) AS message_count
                FROM Message_Threads mt
                LEFT JOIN Messages m ON m.thread_id = mt.thread_id
                WHERE mt.seller_id = :seller_id
                GROUP BY mt.buyer_id
            ),
            buyer_ratings AS (
                SELECT 
                    o.buyer_id AS user_id,
                    AVG(pr.rating) AS avg_rating
                FROM Orders o
                JOIN Order_Items oi ON o.order_id = oi.order_id
                JOIN Product_Reviews pr ON pr.product_id = oi.product_id AND pr.user_id = o.buyer_id
                WHERE oi.seller_id = :seller_id
                GROUP BY o.buyer_id
            ),
            all_buyers AS (
                SELECT 
                    COALESCE(bo.buyer_id, bm.user_id) AS buyer_id,
                    COALESCE(bo.buyer_name, u.full_name) AS buyer_name,
                    COALESCE(bo.total_orders, 0) AS total_orders,
                    COALESCE(bo.total_spent, 0) AS total_spent,
                    bo.last_purchase,
                    COALESCE(bm.message_count, 0) AS message_count,
                    br.avg_rating
                FROM buyer_orders bo
                FULL OUTER JOIN buyer_messages bm ON bo.buyer_id = bm.user_id
                LEFT JOIN Users u ON bm.user_id = u.user_id AND bo.buyer_id IS NULL
                LEFT JOIN buyer_ratings br ON COALESCE(bo.buyer_id, bm.user_id) = br.user_id
                WHERE COALESCE(bo.buyer_id, bm.user_id) IS NOT NULL
            )
            SELECT * FROM all_buyers
            ORDER BY total_orders DESC, last_purchase DESC
            """, seller_id=effective_seller_id)
            
            return [
                {
                    'buyer_id': row[0],
                    'buyer_name': row[1],
                    'total_orders': row[2],
                    'total_spent': row[3],
                    'last_purchase': row[4],
                    'message_count': row[5],
                    'avg_rating': row[6]
                } for row in rows
            ]
        except Exception as e:
            print(f"Error getting buyer engagement data: {str(e)}")
            return []

    @staticmethod
    def get_effective_seller_id(user_id):
        """
        Find the effective seller ID for a user, which may be different from
        their user ID in some cases due to database inconsistencies.
        """
        try:
            rows = app.db.execute("""
            SELECT DISTINCT seller_id
            FROM Message_Threads
            WHERE seller_id = :user_id
            LIMIT 1
            """, user_id=user_id)
            
            if rows:
                return rows[0][0]
                
            rows = app.db.execute("""
            SELECT DISTINCT seller_id
            FROM Order_Items
            WHERE seller_id = :user_id
            LIMIT 1
            """, user_id=user_id)
            
            if rows:
                return rows[0][0]
                
            return user_id
                
        except Exception as e:
            print(f"Error getting effective seller ID: {str(e)}")
            return user_id