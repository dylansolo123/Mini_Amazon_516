from flask import current_app as app
import datetime
from .. import db

class Review:
    def __init__(self, review_id, user_id, product_id, rating, review_text, review_date=None, 
                 reviewer_name=None, product_name=None, likes=0, dislikes=0, score=0):
        self.review_id = review_id
        self.user_id = user_id
        self.product_id = product_id
        self.rating = rating
        self.review_text = review_text
        self.review_date = review_date or datetime.datetime.now()
        self.reviewer_name = reviewer_name
        self.product_name = product_name
        self.likes = likes
        self.dislikes = dislikes
        self.score = score
    
    @staticmethod
    def get_by_id(review_id):
        """Get a review by its ID"""
        try:
            # Use app.db.execute instead of direct SQL query if that's your ORM approach
            rows = app.db.execute('''
                SELECT review_id, user_id, product_id, rating, review_text, review_date,
                       likes, dislikes, score
                FROM Product_Reviews
                WHERE review_id = :review_id
            ''', review_id=review_id)
            
            # Return the first row if found
            if rows and len(rows) > 0:
                row = rows[0]
                return Review(
                    review_id=row[0],
                    user_id=row[1],
                    product_id=row[2],
                    rating=row[3],
                    review_text=row[4],
                    review_date=row[5],
                    likes=row[6],
                    dislikes=row[7],
                    score=row[8]
                )
            return None
        except Exception as e:
            print(f"Error getting review by ID: {str(e)}")
            return None
    
    @staticmethod
    def get_user_reviews(user_id):
        """Get all reviews by a user"""
        try:
            rows = app.db.execute('''
                SELECT review_id, user_id, product_id, rating, review_text, review_date,
                       p.name as product_name, likes, dislikes, score
                FROM Product_Reviews r
                JOIN Products p ON p.id = r.product_id
                WHERE user_id = :user_id
                ORDER BY review_date DESC
            ''', user_id=user_id)
            
            return [Review(
                review_id=row[0],
                user_id=row[1],
                product_id=row[2],
                rating=row[3],
                review_text=row[4],
                review_date=row[5],
                product_name=row[6],
                likes=row[7] if len(row) > 7 else 0,
                dislikes=row[8] if len(row) > 8 else 0,
                score=row[9] if len(row) > 9 else 0
            ) for row in rows]
        except Exception as e:
            print(f"Error getting user reviews: {str(e)}")
            return []
    
    @staticmethod
    def get_product_reviews(product_id):
        """Get all reviews for a product"""
        try:
            rows = app.db.execute('''
                SELECT r.review_id, r.user_id, r.product_id, r.rating, r.review_text, r.review_date,
                       u.full_name as reviewer_name, r.likes, r.dislikes, r.score
                FROM Product_Reviews r
                JOIN Users u ON u.user_id = r.user_id
                WHERE r.product_id = :product_id
                ORDER BY r.score DESC, r.review_date DESC
            ''', product_id=product_id)
            
            return [Review(
                review_id=row[0],
                user_id=row[1],
                product_id=row[2],
                rating=row[3],
                review_text=row[4],
                review_date=row[5],
                reviewer_name=row[6],
                likes=row[7] if len(row) > 7 else 0,
                dislikes=row[8] if len(row) > 8 else 0,
                score=row[9] if len(row) > 9 else 0
            ) for row in rows]
        except Exception as e:
            print(f"Error getting product reviews: {str(e)}")
            return []
    
    @staticmethod
    def create(user_id, product_id, rating, review_text):
        """Create a new review"""
        try:
            # Check if user has already reviewed this product
            existing_review = app.db.execute('''
                SELECT 1 FROM Product_Reviews
                WHERE user_id = :user_id AND product_id = :product_id
            ''', user_id=user_id, product_id=product_id)
            
            if existing_review and len(existing_review) > 0:
                return None, "You have already reviewed this product"
            
            # Create new review
            review_id = app.db.execute('''
                INSERT INTO Product_Reviews(user_id, product_id, rating, review_text, review_date, likes, dislikes, score)
                VALUES(:user_id, :product_id, :rating, :review_text, :review_date, 0, 0, 0)
                RETURNING review_id
            ''', 
                user_id=user_id,
                product_id=product_id,
                rating=rating,
                review_text=review_text,
                review_date=datetime.datetime.now()
            )
            
            if review_id and len(review_id) > 0:
                new_review_id = review_id[0][0]
                return Review(
                    review_id=new_review_id,
                    user_id=user_id,
                    product_id=product_id,
                    rating=rating,
                    review_text=review_text,
                    review_date=datetime.datetime.now(),
                    likes=0,
                    dislikes=0,
                    score=0
                ), "Review created successfully"
            else:
                return None, "Failed to create review"
                
        except Exception as e:
            print(f"Error creating review: {str(e)}")
            return None, f"An error occurred: {str(e)}"
    
    def update_vote_counts(self, likes, dislikes, score):
        """Update the vote counts for this review"""
        try:
            self.likes = likes
            self.dislikes = dislikes
            self.score = score
            
            app.db.execute('''
                UPDATE Product_Reviews
                SET likes = :likes, dislikes = :dislikes, score = :score
                WHERE review_id = :review_id
            ''',
                likes=likes,
                dislikes=dislikes,
                score=score,
                review_id=self.review_id
            )
            return True
        except Exception as e:
            print(f"Error updating vote counts: {str(e)}")
            return False