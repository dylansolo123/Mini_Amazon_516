from flask import current_app as app
from datetime import datetime

class Review:
    def __init__(self, review_id, user_id, product_id, rating, review_text, review_time):
        self.review_id = review_id
        self.user_id = user_id
        self.product_id = product_id
        self.rating = rating
        self.review_text = review_text
        self.review_time = review_time

    @staticmethod
    def get_user_reviews(user_id):
        """Get all reviews by a user with product information."""
        rows = app.db.execute('''
            SELECT r.review_id, r.user_id, r.product_id, r.rating, r.review_text, r.review_date,
                   p.name as product_name, p.image_url
            FROM Product_Reviews r
            JOIN Products p ON p.product_id = r.product_id
            WHERE r.user_id = :user_id
            ORDER BY r.review_date DESC
        ''', user_id=user_id)
        
        if not rows:
            return []
            
        reviews = []
        for row in rows:
            review = Review(
                row[0], row[1], row[2], row[3], row[4], row[5]
            )
            # Add product information
            review.product_name = row[6]
            review.product_image = row[7]
            reviews.append(review)
            
        return reviews

    @staticmethod
    def can_review(user_id, product_id):
        # Check if user has purchased the product
        purchase_rows = app.db.execute('''
            SELECT 1 FROM Order_Items oi
            JOIN Orders o ON o.order_id = oi.order_id
            WHERE o.buyer_id = :user_id 
            AND oi.product_id = :product_id
            AND oi.fulfillment_status = 'Fulfilled'
            LIMIT 1
        ''', user_id=user_id, product_id=product_id)
        
        if not purchase_rows:
            return False, "You must purchase this product before reviewing it"

        # Check if user has already reviewed the product
        review_rows = app.db.execute('''
            SELECT 1 FROM Product_Reviews
            WHERE user_id = :user_id AND product_id = :product_id
            LIMIT 1
        ''', user_id=user_id, product_id=product_id)
        
        if review_rows:
            return False, "You have already reviewed this product"
        
        return True, "Can review"

    @staticmethod
    def create(user_id, product_id, rating, review_text):
        can_review, message = Review.can_review(user_id, product_id)
        if not can_review:
            return None, message

        try:
            rows = app.db.execute('''
                INSERT INTO Product_Reviews(user_id, product_id, rating, review_text, review_date)
                VALUES(:user_id, :product_id, :rating, :review_text, :review_time)
                RETURNING review_id, user_id, product_id, rating, review_text, review_date
            ''', user_id=user_id,
                product_id=product_id,
                rating=rating,
                review_text=review_text,
                review_time=datetime.now())
            review = Review(*(rows[0]))
            return review, "Review added successfully"
        except Exception as e:
            print(f"Error creating review: {str(e)}")
            return None, "An error occurred while creating the review"

    @staticmethod
    def get(review_id):
        rows = app.db.execute('''
            SELECT review_id, user_id, product_id, rating, review_text, review_date
            FROM Product_Reviews
            WHERE review_id = :review_id
        ''', review_id=review_id)
        return Review(*(rows[0])) if rows else None

    @staticmethod
    def update(review_id, rating, review_text):
        app.db.execute('''
            UPDATE Product_Reviews
            SET rating = :rating, review_text = :review_text
            WHERE review_id = :review_id
        ''', rating=rating, review_text=review_text, review_id=review_id)
        return True

    @staticmethod
    def delete(review_id):
        """Delete a review and update product rating statistics."""
        try:
            # First get the product_id for the review before deleting
            product_id_row = app.db.execute('''
                SELECT product_id 
                FROM Product_Reviews 
                WHERE review_id = :review_id
            ''', review_id=review_id)
            
            if not product_id_row:
                return False
                
            product_id = product_id_row[0][0]
            
            # Delete the review
            app.db.execute('''
                DELETE FROM Product_Reviews
                WHERE review_id = :review_id
            ''', review_id=review_id)
            
            return True
            
        except Exception as e:
            print(f"Error in delete method: {str(e)}")
            return False

    @staticmethod
    def get_recent_reviews_by_user(user_id, limit=5):
        """Get the most recent reviews by a specific user."""
        rows = app.db.execute('''
            SELECT r.review_id, r.user_id, r.product_id, r.rating, r.review_text, r.review_date,
                   p.name as product_name, p.image_url,
                   u.full_name as reviewer_name
            FROM Product_Reviews r
            JOIN Products p ON p.product_id = r.product_id
            JOIN Users u ON u.user_id = r.user_id
            WHERE r.user_id = :user_id
            ORDER BY r.review_date DESC
            LIMIT :limit
        ''', user_id=user_id, limit=limit)
        
        if not rows:
            return []
            
        reviews = []
        for row in rows:
            review = Review(
                row[0], row[1], row[2], row[3], row[4], row[5]
            )
            # Add product and user information
            review.product_name = row[6]
            review.product_image = row[7]
            review.reviewer_name = row[8]
            reviews.append(review)
            
        return reviews 