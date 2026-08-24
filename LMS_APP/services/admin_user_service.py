from werkzeug.security import generate_password_hash
from models.user import User

class AdminUserService:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def create_user(self, name, email, password, role):
        if not name or not name.strip():
            raise ValueError("Name is required")

        if not email or not email.strip():
            raise ValueError("Email is required")

        if not password:
            raise ValueError("Password is required")

        if role not in ["student", "instructor"]:
            raise ValueError("Only student or instructor accounts can be created")

        existing_user = self.user_dao.get_user_by_email(email.strip())

        if existing_user:
            raise ValueError("Email already registered")

        user = User(
            name=name.strip(),
            email=email.strip(),
            password=generate_password_hash(password),
            role=role,
            is_active=True
        )

        return self.user_dao.create_user(user)