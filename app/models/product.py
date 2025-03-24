from flask import current_app as app


class Product:
    def __init__(self, product_id, category_id, name, description, image_url, created_by, created_at):
        self.id = product_id  # Add id alias for template compatibility
        self.category_id = category_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.created_by = created_by
        self.created_at = created_at
        self.price = 0.00  # Default price since it's in Seller_Inventory table
        self.available = True  # Default availability

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT product_id, category_id, name, description, image_url, created_by, created_at
FROM Products
WHERE product_id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        print("get_all")
        rows = app.db.execute('''
SELECT product_id, category_id, name, description, image_url, created_by, created_at
FROM Products
''')
        return [Product(*row) for row in rows]
