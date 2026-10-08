def test_create_event(client):
    response = client.post(
        "/events",
        json={
            "name": "Python Workshop",
            "description": "Backend Workshop",
            "event_date": "2026-10-20",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Python Workshop"
    assert data["description"] == "Backend Workshop"
    assert data["event_date"] == "2026-10-20"
    assert "id" in data