import pytest
import os

os.environ["TESTING"] = "1"
from app import app
from config.database import db
from models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():

        db.drop_all()
        db.create_all()

        student = User(
            name="Test Student",
            email="student@test.com",
            password=generate_password_hash("password123"),
            role="student",
            is_active=True
        )

        db.session.add(student)
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()

@pytest.fixture
def student(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_role"] = "student"

    return client


@pytest.fixture
def instructor(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_role"] = "instructor"

    return client


@pytest.fixture
def admin(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_role"] = "admin"

    return client