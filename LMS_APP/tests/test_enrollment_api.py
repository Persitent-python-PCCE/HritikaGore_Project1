import pytest

from models.course import Course
from models.user import User

from config.database import db
from werkzeug.security import generate_password_hash


def get_student_token(client):

    response = client.post(
        "/api/v2/auth/login",
        json={
            "email": "student@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    return response.get_json()["access_token"]


def get_instructor_token(client):

    with client.application.app_context():

        instructor = User(
            name="Test Instructor",
            email="instructor@test.com",
            password=generate_password_hash("password123"),
            role="instructor",
            is_active=True
        )

        db.session.add(instructor)
        db.session.commit()

    response = client.post(
        "/api/v2/auth/login",
        json={
            "email": "instructor@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    return response.get_json()["access_token"]


def create_course():

    course = Course(
        title="Python API Course",
        description="API Test Course",
        instructor_id=1
    )

    db.session.add(course)
    db.session.commit()

    return course


def test_api_student_can_enroll(client):

    course = create_course()

    token = get_student_token(client)

    response = client.post(
        f"/api/v2/courses/{course.id}/enroll",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Course enrollment successful"
    assert data["enrollment"]["course_id"] == course.id
    assert data["enrollment"]["status"].lower() == "active"


def test_api_student_cannot_enroll_twice(client):

    course = create_course()

    token = get_student_token(client)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    first = client.post(
        f"/api/v2/courses/{course.id}/enroll",
        headers=headers
    )

    assert first.status_code == 201

    second = client.post(
        f"/api/v2/courses/{course.id}/enroll",
        headers=headers
    )

    assert second.status_code == 400


def test_api_my_courses(client):

    course = create_course()

    token = get_student_token(client)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    enroll = client.post(
        f"/api/v2/courses/{course.id}/enroll",
        headers=headers
    )

    assert enroll.status_code == 201

    response = client.get(
        "/api/v2/my-courses",
        headers=headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["course_id"] == course.id


def test_api_check_enrollment(client):

    course = create_course()

    token = get_student_token(client)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get(
        f"/api/v2/courses/{course.id}/enrollment",
        headers=headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["enrolled"] is False

    client.post(
        f"/api/v2/courses/{course.id}/enroll",
        headers=headers
    )

    response = client.get(
        f"/api/v2/courses/{course.id}/enrollment",
        headers=headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["enrolled"] is True


def test_api_instructor_cannot_enroll(client):

    course = create_course()

    token = get_instructor_token(client)

    response = client.post(
        f"/api/v2/courses/{course.id}/enroll",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403