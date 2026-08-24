def test_login_page(client):
    response = client.get("/login")

    assert response.status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/login" in response.location


def test_logout(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_role"] = "student"

    response = client.get("/logout")

    assert response.status_code == 302
    assert "/login" in response.location

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "user_role" not in sess