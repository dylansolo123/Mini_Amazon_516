from flask import current_app as app


class Purchase:
    def __init__(self, order_id, buyer_id, order_date, total_amount, fulfillment_status):
        self.order_id = order_id
        self.buyer_id = buyer_id
        self.order_date = order_date
        self.total_amount = total_amount
        self.fulfillment_status = fulfillment_status

    @staticmethod
    def get(order_id):
        rows = app.db.execute('''
SELECT o.order_id, o.buyer_id, o.order_date, 
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_amount,
       o.fulfillment_status
FROM Orders o
LEFT JOIN Order_Items oi ON o.order_id = oi.order_id
WHERE o.order_id = :order_id
GROUP BY o.order_id, o.buyer_id, o.order_date, o.fulfillment_status
''',
                              order_id=order_id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_buyer_since(buyer_id, since):
        rows = app.db.execute('''
SELECT o.order_id, o.buyer_id, o.order_date, 
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_amount,
       o.fulfillment_status
FROM Orders o
LEFT JOIN Order_Items oi ON o.order_id = oi.order_id
WHERE o.buyer_id = :buyer_id
AND o.order_date >= :since
GROUP BY o.order_id, o.buyer_id, o.order_date, o.fulfillment_status
ORDER BY o.order_date DESC
''',
                              buyer_id=buyer_id,
                              since=since)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_by_uid_since(uid, since):
        """Alias for get_all_by_buyer_since for compatibility with index.py"""
        return Purchase.get_all_by_buyer_since(uid, since)

    @staticmethod
    def get_items(order_id):
        rows = app.db.execute('''
SELECT oi.order_item_id, oi.order_id, oi.seller_id, oi.product_id, 
       oi.quantity, oi.unit_price, oi.fulfillment_status, oi.fulfillment_date,
       p.name as product_name,
       u.full_name as seller_name,
       (oi.quantity * oi.unit_price) as item_total
FROM Order_Items oi
JOIN Products p ON oi.product_id = p.product_id
JOIN Users u ON oi.seller_id = u.user_id
WHERE oi.order_id = :order_id
''',
                              order_id=order_id)
        return rows

    @staticmethod
    def add_purchase(buyer_id, total_amount):
        rows = app.db.execute("""
INSERT INTO Orders(buyer_id, total_amount, fulfillment_status)
VALUES(:buyer_id, :total_amount, 'Pending')
RETURNING order_id
""",
                            buyer_id=buyer_id,
                            total_amount=total_amount)
        order_id = rows[0][0]
        return order_id

    @staticmethod
    def add_order_item(order_id, seller_id, product_id, quantity, unit_price):
        rows = app.db.execute("""
INSERT INTO Order_Items(order_id, seller_id, product_id, quantity, unit_price, fulfillment_status)
VALUES(:order_id, :seller_id, :product_id, :quantity, :unit_price, 'Pending')
RETURNING order_item_id
""",
                            order_id=order_id,
                            seller_id=seller_id,
                            product_id=product_id,
                            quantity=quantity,
                            unit_price=unit_price)
        return rows[0][0]

    @staticmethod
    def get_by_seller(seller_id):
        rows = app.db.execute('''
SELECT DISTINCT o.order_id, o.buyer_id, o.order_date,
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_amount,
       o.fulfillment_status
FROM Orders o
JOIN Order_Items oi ON o.order_id = oi.order_id
WHERE oi.seller_id = :seller_id
GROUP BY o.order_id, o.buyer_id, o.order_date, o.fulfillment_status
ORDER BY o.order_date DESC
''',
                              seller_id=seller_id)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def update_fulfillment_status(order_id, new_status):
        rows = app.db.execute("""
UPDATE Orders
SET fulfillment_status = :new_status
WHERE order_id = :order_id
RETURNING order_id
""",
                            order_id=order_id,
                            new_status=new_status)
        return rows[0][0] if rows else None

    @staticmethod
    def update_order_item_fulfillment(order_item_id, new_status):
        rows = app.db.execute("""
UPDATE Order_Items
SET fulfillment_status = :new_status,
    fulfillment_date = CASE 
        WHEN :new_status = 'Fulfilled' THEN CURRENT_TIMESTAMP
        ELSE fulfillment_date
    END
WHERE order_item_id = :order_item_id
RETURNING order_item_id
""",
                            order_item_id=order_item_id,
                            new_status=new_status)
        return rows[0][0] if rows else None

    @staticmethod
    def get_order_items_by_seller(order_id, seller_id):
        rows = app.db.execute('''
SELECT oi.order_item_id, oi.order_id, oi.seller_id, oi.product_id,
       oi.quantity, oi.unit_price, oi.fulfillment_status, oi.fulfillment_date,
       p.name as product_name
FROM Order_Items oi
JOIN Products p ON oi.product_id = p.product_id
WHERE oi.order_id = :order_id
AND oi.seller_id = :seller_id
''',
                              order_id=order_id,
                              seller_id=seller_id)
        return rows

    @staticmethod
    def get_order_items_with_products(order_id):
        rows = app.db.execute('''
SELECT oi.order_item_id, oi.order_id, oi.seller_id, oi.product_id,
       oi.quantity, oi.unit_price, oi.fulfillment_status, oi.fulfillment_date,
       p.name as product_name, u.full_name as seller_name
FROM Order_Items oi
JOIN Products p ON oi.product_id = p.product_id
JOIN Users u ON oi.seller_id = u.user_id
WHERE oi.order_id = :order_id
''',
                              order_id=order_id)
        return rows