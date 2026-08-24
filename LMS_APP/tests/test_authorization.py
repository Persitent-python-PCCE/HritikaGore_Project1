def test_courses_requires_login(client):
    response = client.get("/courses")

    assert response.status_code == 302
    assert "/login" in response.location


def test_my_courses_requires_login(client):
    response = client.get("/my-courses")

    assert response.status_code == 302
    assert "/login" in response.location


def test_create_course_requires_login(client):
    response = client.get("/courses/create")

    assert response.status_code == 302
    assert "/login" in response.location


def test_create_course_student_forbidden(student):
    response = student.get("/courses/create")

    assert response.status_code == 403