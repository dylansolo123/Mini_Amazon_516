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
SELECT order_id, buyer_id, order_date, total_amount, fulfillment_status
FROM Orders
WHERE order_id = :order_id
''',
                              order_id=order_id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_buyer_since(buyer_id, since):
        rows = app.db.execute('''
SELECT order_id, buyer_id, order_date, total_amount, fulfillment_status
FROM Orders
WHERE buyer_id = :buyer_id
AND order_date >= :since
ORDER BY order_date DESC
''',
                              buyer_id=buyer_id,
                              since=since)
        print(rows)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_by_uid_since(uid, since):
        """Alias for get_all_by_buyer_since for compatibility with index.py"""
        return Purchase.get_all_by_buyer_since(uid, since)

    @staticmethod
    def get_items(order_id):
        rows = app.db.execute('''
SELECT order_item_id, order_id, seller_id, product_id, 
       quantity, unit_price, fulfillment_status, fulfillment_date
FROM Order_Items
WHERE order_id = :order_id
''',
                              order_id=order_id)
        return rows
