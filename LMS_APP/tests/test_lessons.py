def test_lessons_requires_login(client):
    response = client.get("/modules/1/lessons")

    assert response.status_code == 302


def test_create_lesson_requires_login(client):
    response = client.get("/modules/1/lessons/create")

    assert response.status_code == 302


def test_student_cannot_create_lesson(student):
    response = student.get("/modules/1/lessons/create")

    assert response.status_code == 403


def test_student_cannot_edit_lesson(student):
    response = student.get("/lessons/edit/1")

    assert response.status_code == 403


def test_student_cannot_delete_lesson(student):
    response = student.post("/lessons/delete/1")

    assert response.status_code == 403