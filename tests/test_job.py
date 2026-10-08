def create_event(client):
    response = client.post(
        "/events",
        json={
            "name": "Testing Event",
            "description": "Testing",
            "event_date": "2026-10-22",
        },
    )

    return response.json()["id"]


def test_get_job_status(client):
    event_id = create_event(client)

    create_response = client.post(
        f"/events/{event_id}/certificate-jobs",
        json={
            "recipients": [
                {
                    "name": "Test User",
                    "email": "job_status@example.com",
                }
            ]
        },
    )

    job_id = create_response.json()["job_id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["event_id"] == event_id
    assert data["total"] == 1
    assert data["successful"] == 0
    assert data["failed"] == 0
    assert data["pending"] == 1
