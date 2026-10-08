def create_event(client):
    response = client.post(
        "/events",
        json={
            "name": "AI Workshop",
            "description": "AI event",
            "event_date": "2026-10-21",
        },
    )

    assert response.status_code == 200

    return response.json()["id"]


def test_create_certificate_job(client):
    event_id = create_event(client)

    response = client.post(
        f"/events/{event_id}/certificate-jobs",
        json={
            "recipients": [
                {
                    "name": "Mukul",
                    "email": "mukul_test@example.com",
                },
                {
                    "name": "Rahul",
                    "email": "rahul_test@example.com",
                },
            ]
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_id"] == event_id
    assert data["total"] == 2
    assert data["status"] == "queued"
    assert "job_id" in data
    def test_invalid_recipient_does_not_stop_job(client):
        event_id = create_event(client)

        response = client.post(
            f"/events/{event_id}/certificate-jobs",
            json={
                "recipients": [
                    {
                        "name": "",
                        "email": "valid@example.com",
                    },
                    {
                        "name": "Valid User",
                        "email": "valid2@example.com",
                    },
                ]
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 2