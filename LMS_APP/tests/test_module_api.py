import pytest

from app import app
from config.database import db

from models.user import User
from models.course import Course
from models.module import Module

from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

        # Instructor
        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            password=generate_password_hash("password123"),
            role="instructor",
            is_active=True
        )

        # Student
        student = User(
            name="Student",
            email="student@test.com",
            password=generate_password_hash("password123"),
            role="student",
            is_active=True
        )

        db.session.add_all([
            instructor,
            student
        ])

        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def get_token(client, email, password="password123"):
    response = client.post(
        "/api/v2/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.get_json()["access_token"]


def create_course():
    instructor = User.query.filter_by(
        email="instructor@test.com"
    ).first()

    course = Course(
        title="Python Programming",
        description="Python Course",
        instructor_id=instructor.id
    )

    db.session.add(course)
    db.session.commit()

    return course


def create_module(course_id):
    module = Module(
        title="Introduction to Python",
        description="Python basics",
        course_id=course_id
    )

    db.session.add(module)
    db.session.commit()

    return module


def test_api_instructor_can_create_module(client):

    course = create_course()

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/courses/{course.id}/modules",
        json={
            "title": "Python Basics",
            "description": "Introduction to Python"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Module created successfully"
    assert data["module"]["title"] == "Python Basics"
    assert data["module"]["course_id"] == course.id


def test_api_instructor_can_get_modules(client):

    course = create_course()

    create_module(course.id)

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        f"/api/v2/courses/{course.id}/modules",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["title"] == "Introduction to Python"


def test_api_student_cannot_get_unenrolled_modules(client):

    course = create_course()

    create_module(course.id)

    token = get_token(
        client,
        "student@test.com"
    )

    response = client.get(
        f"/api/v2/courses/{course.id}/modules",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_api_instructor_can_get_module(client):

    course = create_course()

    module = create_module(course.id)

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        f"/api/v2/modules/{module.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == module.id
    assert data["title"] == "Introduction to Python"
    assert data["course_id"] == course.id


def test_api_instructor_can_update_module(client):

    course = create_course()

    module = create_module(course.id)

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.put(
        f"/api/v2/modules/{module.id}",
        json={
            "title": "Updated Python Module",
            "description": "Updated description"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Module updated successfully"
    assert data["module"]["title"] == "Updated Python Module"
    assert data["module"]["description"] == "Updated description"


def test_api_instructor_can_delete_module(client):

    course = create_course()

    module = create_module(course.id)

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.delete(
        f"/api/v2/modules/{module.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Module deleted successfully"

    deleted_module = db.session.get(
        Module,
        module.id
    )

    assert deleted_module is None


def test_api_student_cannot_create_module(client):

    course = create_course()

    token = get_token(
        client,
        "student@test.com"
    )

    response = client.post(
        f"/api/v2/courses/{course.id}/modules",
        json={
            "title": "Unauthorized Module",
            "description": "Should not be created"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_api_module_not_found(client):

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        "/api/v2/modules/9999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_api_create_module_missing_body(client):

    course = create_course()

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/courses/{course.id}/modules",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400


def test_api_create_module_missing_title(client):

    course = create_course()

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/courses/{course.id}/modules",
        json={
            "description": "Description without title"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400