from flask import current_app
from app import create_app

def create_comment_tables():
    app = create_app()
    with app.app_context():
        # Create Comments table
        app.db.execute('''
            CREATE TABLE IF NOT EXISTS Comments (
                comment_id SERIAL PRIMARY KEY,
                review_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                points INTEGER DEFAULT 0,
                CONSTRAINT fk_comments_review FOREIGN KEY (review_id)
                    REFERENCES Product_Reviews(review_id) ON DELETE CASCADE,
                CONSTRAINT fk_comments_user FOREIGN KEY (user_id)
                    REFERENCES Users(user_id)
            )
        ''')
        
        # Create Comment_Votes table
        app.db.execute('''
            CREATE TABLE IF NOT EXISTS Comment_Votes (
                vote_id SERIAL PRIMARY KEY,
                comment_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                vote_value INTEGER NOT NULL CHECK (vote_value IN (-1, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_comment_votes_comment FOREIGN KEY (comment_id)
                    REFERENCES Comments(comment_id) ON DELETE CASCADE,
                CONSTRAINT fk_comment_votes_user FOREIGN KEY (user_id)
                    REFERENCES Users(user_id),
                CONSTRAINT uq_user_comment_vote UNIQUE (user_id, comment_id)
            )
        ''')
        
        print("Comment tables created successfully!")

if __name__ == '__main__':
    create_comment_tables() 