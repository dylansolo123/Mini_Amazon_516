from flask import current_app as app


class Product:
    def __init__(self, product_id, category_id, name, description, image_url, created_by, created_at):
        self.product_id = product_id
        self.category_id = category_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.created_by = created_by
        self.created_at = created_at

    @staticmethod
    def get(product_id):
        rows = app.db.execute('''
SELECT product_id, category_id, name, description, image_url, created_by, created_at
FROM Products
WHERE product_id = :product_id
''',
                              product_id=product_id)
        return Product(*(rows[0])) if rows else None

    @staticmethod
    def get_all(category_id=None):
        if category_id is not None:
            rows = app.db.execute('''
SELECT product_id, category_id, name, description, image_url, created_by, created_at
FROM Products
WHERE category_id = :category_id
ORDER BY created_at DESC
''',
                                category_id=category_id)
        else:
            rows = app.db.execute('''
SELECT product_id, category_id, name, description, image_url, created_by, created_at
FROM Products
ORDER BY created_at DESC
''')
        return [Product(*row) for row in rows]
