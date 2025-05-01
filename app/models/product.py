from flask import current_app as app
from decimal import Decimal

class Product:
    # Dictionary mapping category names to their image files
    CATEGORY_IMAGES = {
        'Beauty': 'css/images/beauty.jpg',
        'Books': 'css/images/books.jpg',
        'Clothing': 'css/images/clothing.jpg',
        'Electronics': 'css/images/electronics.jpeg',
        'Food': 'css/images/food.jpg',
        'Garden': 'css/images/garden.jpeg',
        'Home': 'css/images/home.jpg',
        'Sports': 'css/images/sports.jpeg',
        'Toys': 'css/images/toys.jpg'
    }

    def __init__(self, product_id, category_id, name, description, image_url, created_by, created_at):
        self.id = int(product_id)  # Ensure ID is always an integer
        self.category_id = category_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.created_by = created_by
        self.created_at = created_at
        self.price = None
        self.available_quantity = 0
        self.seller_id = None
        self.seller_name = None
        self.category_name = None
        self.original_price = None
        self.review_count = 0
        self.avg_rating = 0.0
        self.reviews = []
        self.sellers = []

    @property
    def category_image(self):
        """Get the appropriate image for this product's category"""
        if self.category_name:
            return self.CATEGORY_IMAGES.get(self.category_name, self.image_url)
        return self.image_url

    @staticmethod
    def get(id):
        try:
            rows = app.db.execute('''
SELECT p.product_id, p.category_id, p.name, p.description, 
       p.image_url, p.created_by, p.created_at,
       pc.category_name
FROM Products p
LEFT JOIN Product_Categories pc ON p.category_id = pc.category_id
WHERE p.product_id = :id
''', id=id)
            
            if not rows:
                return None
            
            product = Product(*(rows[0][:7]))
            product.category_name = rows[0][7]
            
            # Get inventory information
            inventory = app.db.execute('''
SELECT MIN(price) as min_price, SUM(quantity) as total_quantity
FROM Seller_Inventory
WHERE product_id = :id
''', id=id)
            
            if inventory and inventory[0]:
                product.price = inventory[0][0]
                product.available_quantity = inventory[0][1] or 0
                
            return product
        except Exception as e:
            print(f"Error in get method: {str(e)}")
            return None

    @staticmethod
    def get_all(available=True, category_id=None, search_query=None, sort_by_price=None, page=1, per_page=30, top_k=None):
        try:
            # Calculate offset for pagination
            offset = (page - 1) * per_page
            
            # Base params
            params = {'per_page': per_page, 'offset': offset}
            
            # Build the WHERE clause and params
            where_clauses = ["1=1"]
            if category_id:
                where_clauses.append("p.category_id = :category_id")
                params['category_id'] = category_id
                
            if search_query:
                where_clauses.append("(LOWER(p.name) LIKE LOWER(:search_pattern) OR LOWER(p.description) LIKE LOWER(:search_pattern))")
                params['search_pattern'] = f'%{search_query}%'

            where_clause = " AND ".join(where_clauses)

            # Count total products
            count_query = f'''
SELECT COUNT(DISTINCT p.product_id)
FROM Products p
WHERE {where_clause}
'''
            total_count = app.db.execute(count_query, **params)[0][0]

            # Main query for products
            query = f'''
SELECT DISTINCT 
    p.product_id, p.category_id, p.name, p.description, 
    p.image_url, p.created_by, p.created_at,
    pc.category_name,
    COALESCE(inv.min_price, NULL) as min_price,
    COALESCE(inv.total_quantity, 0) as total_quantity
FROM Products p
LEFT JOIN Product_Categories pc ON p.category_id = pc.category_id
LEFT JOIN (
    SELECT product_id, 
           MIN(price) as min_price,
           SUM(quantity) as total_quantity
    FROM Seller_Inventory
    GROUP BY product_id
) inv ON p.product_id = inv.product_id
WHERE {where_clause}
'''
            
            if sort_by_price:
                query += f' ORDER BY min_price {sort_by_price} NULLS LAST'
            else:
                query += ' ORDER BY p.created_at DESC'

            if top_k:
                query += ' LIMIT :top_k'
                params['top_k'] = top_k
            else:
                query += ' LIMIT :per_page OFFSET :offset'

            rows = app.db.execute(query, **params)
            
            products = []
            for row in rows:
                if row:
                    product = Product(*(row[:7]))
                    product.category_name = row[7]
                    product.price = row[8]
                    product.available_quantity = row[9] or 0
                    products.append(product)

            total_pages = (total_count + per_page - 1) // per_page if per_page > 0 else 1
            
            return {
                'products': products,
                'total_pages': total_pages,
                'current_page': page,
                'total_count': total_count
            }

        except Exception as e:
            print(f"Error in get_all method: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

    @staticmethod
    def get_top_k_expensive(k):
        try:
            rows = app.db.execute('''
SELECT p.product_id, p.category_id, p.name, p.description, 
       p.image_url, p.created_by, p.created_at,
       pc.category_name,
       MIN(si.price) as min_price,
       SUM(si.quantity) as total_quantity
FROM Products p
JOIN Seller_Inventory si ON p.product_id = si.product_id
LEFT JOIN Product_Categories pc ON p.category_id = pc.category_id
GROUP BY p.product_id, p.category_id, p.name, p.description, 
         p.image_url, p.created_by, p.created_at, pc.category_name
HAVING SUM(si.quantity) > 0
ORDER BY min_price DESC
LIMIT :k
''', k=k)
            
            products = []
            for row in rows:
                if row:
                    product = Product(*(row[:7]))
                    product.category_name = row[7]
                    product.price = row[8]
                    product.available_quantity = row[9]
                    products.append(product)
            return products
        except Exception as e:
            print(f"Error in get_top_k_expensive: {str(e)}")
            return []

    @staticmethod
    def get_product_details(product_id):
        try:
            # First, get the basic product information
            basic_info = app.db.execute('''
SELECT p.product_id, p.category_id, p.name, p.description, 
       p.image_url, p.created_by, p.created_at,
       pc.category_name
FROM Products p
LEFT JOIN Product_Categories pc ON p.category_id = pc.category_id
WHERE p.product_id = :product_id
''', product_id=product_id)

            if not basic_info:
                print(f"Product {product_id} not found")
                return None

            # Create product object with basic info
            product = Product(*(basic_info[0][:7]))
            product.category_name = basic_info[0][7]

            # Get review statistics
            review_stats = app.db.execute('''
SELECT COUNT(*) as review_count, COALESCE(AVG(rating), 0) as avg_rating
FROM Product_Reviews
WHERE product_id = :product_id
''', product_id=product_id)

            if review_stats:
                product.review_count = review_stats[0][0]
                product.avg_rating = float(review_stats[0][1])

            # Get seller information and inventory
            seller_info = app.db.execute('''
SELECT si.seller_id,
       si.price,
       si.quantity,
       u.full_name as seller_name,
       COALESCE(sr.avg_rating, 0) as seller_rating,
       COALESCE(sr.review_count, 0) as seller_review_count
FROM Seller_Inventory si
JOIN Users u ON si.seller_id = u.user_id
LEFT JOIN (
    SELECT seller_id, 
           AVG(rating) as avg_rating,
           COUNT(*) as review_count
    FROM Seller_Reviews
    GROUP BY seller_id
) sr ON si.seller_id = sr.seller_id
WHERE si.product_id = :product_id
ORDER BY si.price ASC
''', product_id=product_id)

            sellers = []
            total_quantity = 0
            min_price = None

            for seller in seller_info:
                seller_obj = type('Seller', (), {})()
                seller_obj.seller_id = seller[0]
                seller_obj.price = seller[1]
                seller_obj.quantity = seller[2]
                seller_obj.seller_name = seller[3]
                seller_obj.avg_rating = float(seller[4])
                seller_obj.review_count = seller[5]

                # Get seller's reviews
                seller_obj.reviews = app.db.execute('''
SELECT sr.rating, sr.review_text, sr.review_date,
       u.full_name as reviewer_name
FROM Seller_Reviews sr
JOIN Users u ON sr.user_id = u.user_id
WHERE sr.seller_id = :seller_id
ORDER BY sr.review_date DESC
LIMIT 5
''', seller_id=seller_obj.seller_id)

                # Updated query to include category information for other products
                seller_obj.other_products = app.db.execute('''
SELECT p.product_id, p.name, p.image_url, si.price, pc.category_name
FROM Products p
JOIN Seller_Inventory si ON p.product_id = si.product_id
LEFT JOIN Product_Categories pc ON p.category_id = pc.category_id
WHERE si.seller_id = :seller_id
AND p.product_id != :product_id
AND si.quantity > 0
ORDER BY si.price ASC
LIMIT 4
''', seller_id=seller_obj.seller_id, product_id=product_id)

                sellers.append(seller_obj)
                total_quantity += seller_obj.quantity
                if min_price is None or seller_obj.price < min_price:
                    min_price = seller_obj.price

            product.sellers = sellers
            product.available_quantity = total_quantity
            product.price = min_price

            # Get product reviews
            product.reviews = app.db.execute('''
SELECT pr.rating, pr.review_text, pr.review_date,
       u.full_name as reviewer_name
FROM Product_Reviews pr
JOIN Users u ON pr.user_id = u.user_id
WHERE pr.product_id = :product_id
ORDER BY pr.review_date DESC
''', product_id=product_id)

            return product

        except Exception as e:
            print(f"Error in get_product_details: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

    @staticmethod
    def update(product_id, category_id, name, description, image_url, user_id):
        try:
            rows = app.db.execute('''
UPDATE Products
SET category_id = :category_id,
    name = :name,
    description = :description,
    image_url = :image_url
WHERE product_id = :product_id
AND created_by = :user_id
RETURNING product_id
''',
                                product_id=product_id,
                                category_id=category_id,
                                name=name,
                                description=description,
                                image_url=image_url,
                                user_id=user_id)
            return rows[0][0] if rows else None
        except Exception as e:
            print(f"Error in update method: {str(e)}")
            return None

    @staticmethod
    def create(category_id, name, description, image_url, user_id):
        try:
            rows = app.db.execute('''
INSERT INTO Products(category_id, name, description, image_url, created_by)
VALUES(:category_id, :name, :description, :image_url, :user_id)
RETURNING product_id
''',
                                category_id=category_id,
                                name=name,
                                description=description,
                                image_url=image_url,
                                user_id=user_id)
            return rows[0][0]
        except Exception as e:
            print(f"Error in create method: {str(e)}")
            return None

    @staticmethod
    def get_categories():
        try:
            return app.db.execute('''
SELECT category_id, category_name
FROM Product_Categories
ORDER BY category_name
''')
        except Exception as e:
            print(f"Error in get_categories: {str(e)}")
            return []