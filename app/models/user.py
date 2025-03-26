from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, user_id, email, full_name, address, balance, is_seller):
        self.id = user_id  # Keep as self.id for Flask-Login compatibility
        self.user_id = user_id
        self.email = email
        self.full_name = full_name
        self.address = address
        self.balance = balance
        self.is_seller = is_seller

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT user_id, email, full_name, address, balance, is_seller, password
FROM users
WHERE email = :email
""",
                              email=email)
        print(rows)
        if not rows:  # email not found
            return None
        elif rows[0][6] != password:
            # incorrect password
            return None
        else:
            return User(*(rows[0][:-1]))  # Exclude password from User object

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, full_name, address, is_seller=False):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, full_name, address, balance, is_seller)
VALUES(:email, :password, :full_name, :address, 0.00, :is_seller)
RETURNING user_id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  full_name=full_name,
                                  address=address,
                                  is_seller=is_seller)
            user_id = rows[0][0]
            return User.get(user_id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(user_id):
        rows = app.db.execute("""
SELECT user_id, email, full_name, address, balance, is_seller
FROM Users
WHERE user_id = :user_id
""",
                              user_id=user_id)
        return User(*(rows[0])) if rows else None

    def update_balance(self, new_balance):
        rows = app.db.execute("""
UPDATE Users
SET balance = :new_balance
WHERE user_id = :user_id
RETURNING balance
""",
                              new_balance=new_balance,
                              user_id=self.user_id)
        if rows:
            self.balance = rows[0][0]
            return True
        return False
