from flask import current_app as app


class Product:
    def __init__(self, product_id, category_id, name, description, image_url, created_by, created_at):
        self.id = product_id
        self.category_id = category_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.created_by = created_by
        self.created_at = created_at
        self.price = None  # Will be set from Seller_Inventory
        self.available_quantity = 0

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT p.product_id, p.category_id, p.name, p.description, 
       p.image_url, p.created_by, p.created_at,
       MIN(si.price) as min_price,
       SUM(si.quantity) as total_quantity
FROM Products p
LEFT JOIN Seller_Inventory si ON p.product_id = si.product_id
WHERE p.product_id = :id
GROUP BY p.product_id, p.category_id, p.name, p.description, 
         p.image_url, p.created_by, p.created_at
''',
                              id=id)
        if not rows:
            return None
        
        product = Product(*(rows[0][:7]))  # First 7 columns are product info
        product.price = rows[0][7]  # Set the minimum price
        product.available_quantity = rows[0][8] or 0  # Set total available quantity
        return product

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT p.product_id, p.category_id, p.name, p.description, 
       p.image_url, p.created_by, p.created_at,
       MIN(si.price) as min_price,
       SUM(si.quantity) as total_quantity
FROM Products p
LEFT JOIN Seller_Inventory si ON p.product_id = si.product_id
GROUP BY p.product_id, p.category_id, p.name, p.description, 
         p.image_url, p.created_by, p.created_at
ORDER BY p.product_id
''')
        products = []
        for row in rows:
            product = Product(*(row[:7]))  # First 7 columns are product info
            product.price = row[7]  # Set the minimum price
            product.available_quantity = row[8] or 0  # Set total available quantity
            products.append(product)
        return products

    @staticmethod
    def get_by_seller(seller_id):
        rows = app.db.execute('''
SELECT p.product_id, p.category_id, p.name, p.description, 
       p.image_url, p.created_by, p.created_at,
       si.price,
       si.quantity
FROM Products p
JOIN Seller_Inventory si ON p.product_id = si.product_id
WHERE si.seller_id = :seller_id
ORDER BY p.product_id
''',
                              seller_id=seller_id)
        products = []
        for row in rows:
            product = Product(*(row[:7]))  # First 7 columns are product info
            product.price = row[7]  # Set the seller's price
            product.available_quantity = row[8]  # Set seller's quantity
            products.append(product)
        return products