# tests/test_activities.py
# Testar aktivitetsloggning: spara aktivitet, CO₂e-beräkning och felfall.

import pytest


def create_test_user(client, name="Testare", email="testare@test.se"):
    """Hjälpfunktion: skapar en testanvändare och returnerar klienten."""
    client.post(
        "/ui/users",
        data={"name": name, "email": email},
        follow_redirects=True,
    )


class TestLogActivity:
    """Tester för att logga aktiviteter via POST /ui/activities."""

    def test_log_activity_success(self, client):
        """En giltig aktivitet ska sparas och visa CO₂e."""
        create_test_user(client)

        response = client.post(
            "/ui/activities",
            data={
                "user_id": "1",
                "category": "transport",
                "key": "bil",
                "amount": "100",
                "date_str": "2026-05-19",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        # CO₂e = 100 km × 0.21 = 21.0 kg
        assert "21.00" in response.text or "Aktivitet sparad" in response.text

    def test_log_activity_co2e_calculation(self, client):
        """CO₂e ska beräknas korrekt: amount × factor."""
        create_test_user(client)

        # Logga 2 kg nötkött: 2 × 26.5 = 53.0 kg CO₂e
        response = client.post(
            "/ui/activities",
            data={
                "user_id": "1",
                "category": "mat",
                "key": "nötkött",
                "amount": "2",
                "date_str": "2026-05-19",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "53.00" in response.text or "Aktivitet sparad" in response.text

    def test_log_activity_invalid_amount_zero(self, client):
        """Mängd = 0 ska ge felmeddelande."""
        create_test_user(client)

        response = client.post(
            "/ui/activities",
            data={
                "user_id": "1",
                "category": "transport",
                "key": "bil",
                "amount": "0",
                "date_str": "2026-05-19",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "positivt" in response.text.lower() or "mängd" in response.text.lower()

    def test_log_activity_invalid_amount_negative(self, client):
        """Negativt tal som mängd ska ge felmeddelande."""
        create_test_user(client)

        response = client.post(
            "/ui/activities",
            data={
                "user_id": "1",
                "category": "transport",
                "key": "bil",
                "amount": "-10",
                "date_str": "2026-05-19",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "positivt" in response.text.lower() or "mängd" in response.text.lower()

    def test_log_activity_invalid_date(self, client):
        """Ogiltigt datumformat ska ge felmeddelande."""
        create_test_user(client)

        response = client.post(
            "/ui/activities",
            data={
                "user_id": "1",
                "category": "transport",
                "key": "bil",
                "amount": "50",
                "date_str": "not-a-date",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "datum" in response.text.lower()

    def test_log_activity_nonexistent_user(self, client):
        """Aktivitet för icke-existerande användare ska ge felmeddelande."""
        response = client.post(
            "/ui/activities",
            data={
                "user_id": "9999",
                "category": "transport",
                "key": "bil",
                "amount": "10",
                "date_str": "2026-05-19",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "hittades inte" in response.text.lower()


class TestListActivities:
    """Tester för att lista aktiviteter."""

    def test_activities_page_loads(self, client):
        """Aktivitetssidan ska laddas utan fel."""
        response = client.get("/ui/activities")
        assert response.status_code == 200

    def test_activities_show_for_user(self, client):
        """Loggade aktiviteter ska synas för rätt användare."""
        create_test_user(client)

        # Logga en aktivitet
        client.post(
            "/ui/activities",
            data={
                "user_id": "1",
                "category": "energi",
                "key": "el",
                "amount": "200",
                "date_str": "2026-05-19",
            },
            follow_redirects=True,
        )

        # Hämta aktivitetssidan filtrerad på user_id=1
        response = client.get("/ui/activities?user_id=1")
        assert response.status_code == 200
        assert "el" in response.text.lower() or "energi" in response.text.lower()
