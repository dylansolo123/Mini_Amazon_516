from flask import current_app as app
from datetime import datetime

class ReviewVote:
    def __init__(self, vote_id, review_id, user_id, vote_value, created_at):
        self.vote_id = vote_id
        self.review_id = review_id
        self.user_id = user_id
        self.vote_value = vote_value
        self.created_at = created_at

    @staticmethod
    def get_vote(user_id, review_id):
        """Get a user's vote on a specific review."""
        rows = app.db.execute('''
            SELECT vote_id, review_id, user_id, vote_value, created_at
            FROM Review_Votes
            WHERE user_id = :user_id AND review_id = :review_id
        ''', user_id=user_id, review_id=review_id)
        return ReviewVote(*(rows[0])) if rows else None

    @staticmethod
    def create_or_update(user_id, review_id, vote_value):
        """Create or update a vote. Returns (vote, message)."""
        try:
            # Try to insert new vote
            rows = app.db.execute('''
                INSERT INTO Review_Votes(user_id, review_id, vote_value)
                VALUES(:user_id, :review_id, :vote_value)
                ON CONFLICT (user_id, review_id) 
                DO UPDATE SET vote_value = :vote_value
                RETURNING vote_id, review_id, user_id, vote_value, created_at
            ''', user_id=user_id, review_id=review_id, vote_value=vote_value)
            
            return ReviewVote(*(rows[0])), "Vote recorded successfully"
        except Exception as e:
            print(f"Error recording vote: {str(e)}")
            return None, "An error occurred while recording your vote"

    @staticmethod
    def delete(user_id, review_id):
        """Remove a vote."""
        try:
            app.db.execute('''
                DELETE FROM Review_Votes
                WHERE user_id = :user_id AND review_id = :review_id
            ''', user_id=user_id, review_id=review_id)
            return True, "Vote removed successfully"
        except Exception as e:
            print(f"Error removing vote: {str(e)}")
            return False, "An error occurred while removing your vote"

    @staticmethod
    def get_review_votes(review_id):
        """Get total upvotes and downvotes for a review."""
        rows = app.db.execute('''
            SELECT 
                SUM(CASE WHEN vote_value = 1 THEN 1 ELSE 0 END) as upvotes,
                SUM(CASE WHEN vote_value = -1 THEN 1 ELSE 0 END) as downvotes
            FROM Review_Votes
            WHERE review_id = :review_id
        ''', review_id=review_id)
        
        if not rows or not rows[0][0]:
            return 0, 0
        return rows[0][0] or 0, rows[0][1] or 0 