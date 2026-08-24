import pytest

from config.database import db
from models.user import User
from models.course import Course
from models.module import Module
from models.lesson import Lesson

from werkzeug.security import generate_password_hash

def create_user(
    email,
    role="student",
    password="password123"
):
    user = User(
        name=role.title(),
        email=email,
        password=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return user


def create_course(instructor_id):
    course = Course(
        title="Python Programming",
        description="Python course",
        instructor_id=instructor_id
    )

    db.session.add(course)
    db.session.commit()

    return course


def create_module(course_id):
    module = Module(
        title="Python Basics",
        description="Introduction to Python",
        course_id=course_id
    )

    db.session.add(module)
    db.session.commit()

    return module


def create_lesson(module_id):
    lesson = Lesson(
        title="Introduction to Python",
        content="Python is a programming language.",
        module_id=module_id
    )

    db.session.add(lesson)
    db.session.commit()

    return lesson


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


@pytest.fixture
def client():
    from app import app

    app.config["TESTING"] = True

    with app.app_context():

        db.drop_all()
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()

def test_api_create_lesson(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/modules/{module.id}/lessons",
        json={
            "title": "Variables",
            "content": "Variables store values."
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["msg"] == "Lesson created successfully"
    assert data["lesson"]["title"] == "Variables"
    assert data["lesson"]["content"] == "Variables store values."
    assert data["lesson"]["module_id"] == module.id


def test_api_create_lesson_missing_body(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/modules/{module.id}/lessons",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["msg"] == "Request body is required"


def test_api_create_lesson_missing_title(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/modules/{module.id}/lessons",
        json={
            "content": "Some lesson content"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400

def test_api_create_lesson_missing_content(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/modules/{module.id}/lessons",
        json={
            "title": "Variables"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400


def test_api_student_cannot_create_lesson(client):

    student = create_user(
        "student@test.com",
        "student"
    )

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    token = get_token(
        client,
        "student@test.com"
    )

    response = client.post(
        f"/api/v2/modules/{module.id}/lessons",
        json={
            "title": "Unauthorized Lesson",
            "content": "Student should not create this."
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_api_instructor_cannot_create_lesson_in_other_course(client):

    instructor1 = create_user(
        "instructor1@test.com",
        "instructor"
    )

    instructor2 = create_user(
        "instructor2@test.com",
        "instructor"
    )

    course = create_course(
        instructor1.id
    )

    module = create_module(
        course.id
    )

    token = get_token(
        client,
        "instructor2@test.com"
    )

    response = client.post(
        f"/api/v2/modules/{module.id}/lessons",
        json={
            "title": "Unauthorized Lesson",
            "content": "Should not be allowed."
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_api_get_module_lessons(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    create_lesson(module.id)

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        f"/api/v2/modules/{module.id}/lessons",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["title"] == "Introduction to Python"
    assert data[0]["module_id"] == module.id

def test_api_get_module_lessons_not_found(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        "/api/v2/modules/9999/lessons",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_api_get_lesson(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    lesson = create_lesson(
        module.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        f"/api/v2/lessons/{lesson.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == lesson.id
    assert data["title"] == "Introduction to Python"
    assert data["module_id"] == module.id

def test_api_get_lesson_not_found(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        "/api/v2/lessons/9999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

def test_api_update_lesson(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    lesson = create_lesson(
        module.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.put(
        f"/api/v2/lessons/{lesson.id}",
        json={
            "title": "Updated Lesson",
            "content": "Updated lesson content."
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["msg"] == "Lesson updated successfully"
    assert data["lesson"]["title"] == "Updated Lesson"
    assert data["lesson"]["content"] == "Updated lesson content."



def test_api_update_lesson_missing_body(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    lesson = create_lesson(
        module.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.put(
        f"/api/v2/lessons/{lesson.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400


def test_api_student_cannot_update_lesson(client):

    student = create_user(
        "student@test.com",
        "student"
    )

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    lesson = create_lesson(
        module.id
    )

    token = get_token(
        client,
        "student@test.com"
    )

    response = client.put(
        f"/api/v2/lessons/{lesson.id}",
        json={
            "title": "Hacked Lesson",
            "content": "Student should not update."
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_api_instructor_cannot_update_other_course_lesson(client):

    instructor1 = create_user(
        "instructor1@test.com",
        "instructor"
    )

    instructor2 = create_user(
        "instructor2@test.com",
        "instructor"
    )

    course = create_course(
        instructor1.id
    )

    module = create_module(
        course.id
    )

    lesson = create_lesson(
        module.id
    )

    token = get_token(
        client,
        "instructor2@test.com"
    )

    response = client.put(
        f"/api/v2/lessons/{lesson.id}",
        json={
            "title": "Unauthorized",
            "content": "Should not update."
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403

def test_api_delete_lesson(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    lesson = create_lesson(
        module.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.delete(
        f"/api/v2/lessons/{lesson.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["msg"] == "Lesson deleted successfully"

    deleted = db.session.get(
        Lesson,
        lesson.id
    )

    assert deleted is None


def test_api_delete_lesson_not_found(client):

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.delete(
        "/api/v2/lessons/9999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

def test_api_student_cannot_delete_lesson(client):

    student = create_user(
        "student@test.com",
        "student"
    )

    instructor = create_user(
        "instructor@test.com",
        "instructor"
    )

    course = create_course(
        instructor.id
    )

    module = create_module(
        course.id
    )

    lesson = create_lesson(
        module.id
    )

    token = get_token(
        client,
        "student@test.com"
    )

    response = client.delete(
        f"/api/v2/lessons/{lesson.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403