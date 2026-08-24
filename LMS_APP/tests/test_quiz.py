def test_quizzes_requires_login(client):
    response = client.get("/lessons/1/quizzes")

    assert response.status_code == 302


def test_create_quiz_requires_login(client):
    response = client.get("/lessons/1/quizzes/create")

    assert response.status_code == 302


def test_student_cannot_create_quiz(student):
    response = student.get("/lessons/1/quizzes/create")

    assert response.status_code == 403


def test_student_cannot_edit_quiz(student):
    response = student.get("/quizzes/edit/1")

    assert response.status_code == 403


def test_student_cannot_delete_quiz(student):
    response = student.post("/quizzes/delete/1")

    assert response.status_code == 403