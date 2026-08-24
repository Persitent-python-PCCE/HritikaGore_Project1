import pytest


def get_login_token(client):
    response = client.post(
        "/api/v2/auth/login",
        json={
            "email": "student@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    return response.get_json()["access_token"]


def test_api_login(client):
    response = client.post(
        "/api/v2/auth/login",
        json={
            "email": "student@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "access_token" in data
    assert data["user"]["role"] == "student"


def test_api_login_missing_body(client):
    response = client.post(
        "/api/v2/auth/login"
    )

    assert response.status_code == 400


def test_api_courses_requires_jwt(client):
    response = client.get(
        "/api/v2/courses"
    )

    assert response.status_code == 401


def test_api_get_courses(client):
    token = get_login_token(client)

    response = client.get(
        "/api/v2/courses",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_api_get_course_not_found(client):
    token = get_login_token(client)

    response = client.get(
        "/api/v2/courses/999999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_api_student_cannot_create_course(client):
    token = get_login_token(client)

    response = client.post(
        "/api/v2/courses",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Unauthorized Course",
            "description": "Should fail"
        }
    )

    assert response.status_code == 403