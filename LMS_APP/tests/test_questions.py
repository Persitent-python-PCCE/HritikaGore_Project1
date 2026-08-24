def test_questions_requires_login(client):
    response = client.get("/quizzes/1/questions")

    assert response.status_code == 302


def test_create_question_requires_login(client):
    response = client.get("/quizzes/1/questions/create")

    assert response.status_code == 302


def test_student_cannot_create_question(student):
    response = student.get("/quizzes/1/questions/create")

    assert response.status_code == 403


def test_student_cannot_delete_question(student):
    response = student.post("/questions/delete/1")

    assert response.status_code == 403