def test_my_courses_requires_login(client):
    response = client.get("/my-courses")

    assert response.status_code == 302


def test_student_can_access_my_courses(student):
    response = student.get("/my-courses")

    assert response.status_code == 200


def test_instructor_cannot_enroll(instructor):
    response = instructor.post("/courses/1/enroll")

    assert response.status_code == 403


def test_admin_cannot_enroll(admin):
    response = admin.post("/courses/1/enroll")

    assert response.status_code == 403