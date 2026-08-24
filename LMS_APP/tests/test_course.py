def test_course_list_requires_login(client):
    response = client.get("/courses")

    assert response.status_code == 302


def test_instructor_can_open_create_course_page(instructor):
    response = instructor.get("/courses/create")

    assert response.status_code == 200


def test_student_cannot_create_course(student):
    response = student.get("/courses/create")

    assert response.status_code == 403


def test_student_cannot_delete_course(student):
    response = student.post("/courses/delete/1")

    assert response.status_code == 403


def test_student_cannot_edit_course(student):
    response = student.get("/courses/edit/1")

    assert response.status_code == 403