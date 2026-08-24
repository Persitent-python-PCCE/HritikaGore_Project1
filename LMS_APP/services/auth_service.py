from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def register_user(self, name,email, password, role):
        if not name or not name.strip():
            raise ValueError("Name is required")

        if not email or not email.strip():
            raise ValueError("Email is required")

        if not password:
            raise ValueError("Password is required")

        if len(password) < 6:
            raise ValueError("Password must contain at least 6 characters")

        if role not in ["student", "instructor"]:
            raise ValueError("Invalid role")

        email = email.strip().lower()

        existing_user = self.user_dao.get_user_by_email(email)

        if existing_user:
            raise ValueError("Email already registered")

        hashed_password = generate_password_hash(password)

        user = User(
            name = name,
            email = email,
            password = hashed_password,
            role=role
        )
        return self.user_dao.create_user(user)

    def login_user(self, email, password):
        if not email or not email.strip():
            raise ValueError("Email is required")

        if not password:
            raise ValueError("Password is required")

        user = self.user_dao.get_user_by_email(email.strip().lower())

        if not user:
            raise ValueError("Invalid email or password")

        if not check_password_hash(user.password, password):
            raise ValueError("Invalid email or password")

        return user

        