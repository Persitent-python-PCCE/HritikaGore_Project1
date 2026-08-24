def test_materials_requires_login(client):
    response = client.get("/courses/1/materials")

    assert response.status_code == 302


def test_student_cannot_upload_material(student):
    response = student.get("/courses/1/materials/create")

    assert response.status_code == 403