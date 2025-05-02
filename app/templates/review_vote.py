from flask import current_app as app
from app import db  # Import db from app

class ReviewVote(db.Model):
    """
    Model for review votes (likes/dislikes)
    """
    __tablename__ = 'review_votes'
    
    # Primary key is a combination of user_id and review_id
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('product_reviews.review_id', ondelete='CASCADE'), primary_key=True)
    
    # Vote value: 1 for like, -1 for dislike
    value = db.Column(db.Integer, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                            onupdate=db.func.current_timestamp())
    
    def __init__(self, user_id, review_id, value):
        self.user_id = user_id
        self.review_id = review_id
        self.value = value
    
    @staticmethod
    def get_review_votes(review_id):
        """Get all votes for a specific review"""
        try:
            return ReviewVote.query.filter_by(review_id=review_id).all()
        except Exception as e:
            print(f"Error getting review votes: {str(e)}")
            return []
    
    @staticmethod
    def get_user_vote(user_id, review_id):
        """Get a user's vote on a specific review"""
        try:
            return ReviewVote.query.filter_by(
                user_id=user_id,
                review_id=review_id
            ).first()
        except Exception as e:
            print(f"Error getting user vote: {str(e)}")
            return None