from flask import current_app as app
from datetime import datetime

# In-memory storage for comments and votes
comments_store = {}  # {comment_id: Comment}
votes_store = {}    # {(user_id, comment_id): vote_value}
comment_counter = 0  # For generating unique comment IDs

class Comment:
    def __init__(self, comment_id, review_id, user_id, comment_text, created_at=None, points=0):
        self.comment_id = comment_id
        self.review_id = review_id
        self.user_id = user_id
        self.comment_text = comment_text
        self.created_at = created_at or datetime.now()
        self.points = points
        self.user_vote = None
        self.commenter_name = "User " + str(user_id)  # Simplified user name

    @staticmethod
    def create(review_id, user_id, comment_text):
        """Create a new comment."""
        try:
            global comment_counter
            comment_counter += 1
            comment = Comment(
                comment_id=comment_counter,
                review_id=review_id,
                user_id=user_id,
                comment_text=comment_text
            )
            comments_store[comment.comment_id] = comment
            return comment, "Comment added successfully"
        except Exception as e:
            print(f"Error creating comment: {str(e)}")
            return None, "An error occurred while creating the comment"

    @staticmethod
    def get_review_comments(review_id, current_user_id=None):
        """Get all comments for a review with vote information."""
        review_comments = [
            comment for comment in comments_store.values()
            if comment.review_id == review_id
        ]
        
        # Sort comments by points and creation time
        review_comments.sort(key=lambda x: (-x.points, x.created_at))
        
        # Add user's vote if logged in
        if current_user_id:
            for comment in review_comments:
                vote_key = (current_user_id, comment.comment_id)
                comment.user_vote = votes_store.get(vote_key)
                
        return review_comments

    @staticmethod
    def vote(comment_id, user_id, vote_value):
        """Add or update a vote on a comment."""
        try:
            if comment_id not in comments_store:
                return False, "Comment not found"
                
            comment = comments_store[comment_id]
            vote_key = (user_id, comment_id)
            old_vote = votes_store.get(vote_key, 0)
            
            # Remove old vote from points
            comment.points -= old_vote
            
            # Add new vote
            votes_store[vote_key] = vote_value
            comment.points += vote_value
            
            return True, "Vote recorded successfully"
        except Exception as e:
            print(f"Error recording vote: {str(e)}")
            return False, "An error occurred while recording your vote"

    @staticmethod
    def remove_vote(comment_id, user_id):
        """Remove a user's vote from a comment."""
        try:
            if comment_id not in comments_store:
                return False, "Comment not found"
                
            vote_key = (user_id, comment_id)
            if vote_key in votes_store:
                # Remove the vote's points from the comment
                comment = comments_store[comment_id]
                comment.points -= votes_store[vote_key]
                del votes_store[vote_key]
                
            return True, "Vote removed successfully"
        except Exception as e:
            print(f"Error removing vote: {str(e)}")
            return False, "An error occurred while removing your vote"

    @staticmethod
    def delete(comment_id, user_id):
        """Delete a comment (only if user is the author)."""
        try:
            if comment_id not in comments_store:
                return False, "Comment not found"
                
            comment = comments_store[comment_id]
            if comment.user_id != user_id:
                return False, "You can only delete your own comments"
                
            # Delete the comment and its votes
            del comments_store[comment_id]
            votes_to_delete = [
                key for key in votes_store.keys()
                if key[1] == comment_id
            ]
            for vote_key in votes_to_delete:
                del votes_store[vote_key]
                
            return True, "Comment deleted successfully"
        except Exception as e:
            print(f"Error deleting comment: {str(e)}")
            return False, "An error occurred while deleting the comment" 