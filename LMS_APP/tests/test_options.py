def test_options_require_login(client):
    response = client.get("/questions/1/options")

    assert response.status_code == 302


def test_student_cannot_create_option(student):
    response = student.get("/questions/1/options/create")

    assert response.status_code == 403