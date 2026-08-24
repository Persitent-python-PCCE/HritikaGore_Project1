import pytest

from app import app
from config.database import db

from models.user import User
from models.course import Course
from models.material import Material

from werkzeug.security import generate_password_hash


@pytest.fixture
def client():

    app.config["TESTING"] = True

    with app.app_context():

        db.drop_all()
        db.create_all()

        instructor = User(
            name="Instructor",
            email="instructor@test.com",
            password=generate_password_hash(
                "password123"
            ),
            role="instructor",
            is_active=True
        )

        student = User(
            name="Student",
            email="student@test.com",
            password=generate_password_hash(
                "password123"
            ),
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


def get_token(client, email):

    response = client.post(
        "/api/v2/auth/login",
        json={
            "email": email,
            "password": "password123"
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


def create_material(course_id):

    instructor = User.query.filter_by(
        email="instructor@test.com"
    ).first()

    material = Material(
        title="Python Notes",
        file_path="uploads/python_notes.pdf",
        material_type="pdf",
        course_id=course_id,
        module_id=None,
        uploaded_by=instructor.id
    )

    db.session.add(material)
    db.session.commit()

    return material


def test_api_instructor_can_create_material(client):

    course = create_course()

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/courses/{course.id}/materials",
        json={
            "title": "Python Notes",
            "file_path": "uploads/python_notes.pdf",
            "material_type": "pdf"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Material created successfully"
    assert data["material"]["title"] == "Python Notes"
    assert data["material"]["course_id"] == course.id


def test_api_instructor_can_get_course_materials(client):

    course = create_course()

    create_material(course.id)

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        f"/api/v2/courses/{course.id}/materials",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["title"] == "Python Notes"


def test_api_instructor_can_get_material(client):

    course = create_course()

    material = create_material(
        course.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        f"/api/v2/materials/{material.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == material.id
    assert data["title"] == "Python Notes"


def test_api_student_cannot_create_material(client):

    course = create_course()

    token = get_token(
        client,
        "student@test.com"
    )

    response = client.post(
        f"/api/v2/courses/{course.id}/materials",
        json={
            "title": "Unauthorized",
            "file_path": "test.pdf",
            "material_type": "pdf"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_api_student_cannot_access_unenrolled_materials(client):

    course = create_course()

    create_material(course.id)

    token = get_token(
        client,
        "student@test.com"
    )

    response = client.get(
        f"/api/v2/courses/{course.id}/materials",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_api_instructor_can_delete_material(client):

    course = create_course()

    material = create_material(
        course.id
    )

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.delete(
        f"/api/v2/materials/{material.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Material deleted successfully"

    deleted_material = db.session.get(
        Material,
        material.id
    )

    assert deleted_material is None


def test_api_material_not_found(client):

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.get(
        "/api/v2/materials/9999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_api_create_material_missing_body(client):

    course = create_course()

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/courses/{course.id}/materials",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400


def test_api_create_material_missing_title(client):

    course = create_course()

    token = get_token(
        client,
        "instructor@test.com"
    )

    response = client.post(
        f"/api/v2/courses/{course.id}/materials",
        json={
            "file_path": "test.pdf",
            "material_type": "pdf"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400