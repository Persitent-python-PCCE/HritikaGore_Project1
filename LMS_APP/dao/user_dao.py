from models.user import User
from config.database import db

class UserDAO:
    def create_user(self, user):
        db.session.add(user)
        db.session.commit()
        return user

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_all_users(self):
        return User.query.all()