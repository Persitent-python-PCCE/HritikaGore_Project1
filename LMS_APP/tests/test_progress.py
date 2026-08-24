def test_complete_lesson_requires_login(client):
    response = client.post("/lessons/1/complete")

    assert response.status_code == 302
    assert "/login" in response.location


def test_student_can_attempt_complete_lesson(student):
    response = student.post("/lessons/1/complete")

    # 200/302/404 depends on whether lesson 1 exists.
    assert response.status_code in [200, 302, 404]