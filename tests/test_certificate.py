def test_certificate_not_ready(client):
    response = client.get("/certificates/999999")

    assert response.status_code == 404