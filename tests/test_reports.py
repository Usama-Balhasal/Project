# tests/test_reports.py
# Testar veckorapport-funktionen: UI och API (JSON).

import pytest
import datetime as dt


def create_user_and_activities(client):
    """
    Hjälpfunktion: skapar en testanvändare och loggar tre aktiviteter
    för veckan som börjar 2026-05-18 (måndag).
    Förväntad total CO₂e:
      - bil 100 km    = 100 × 0.21 = 21.00
      - nötkött 1 kg  = 1   × 26.5 = 26.50
      - el 100 kWh    = 100 × 0.015 = 1.50
      Total = 49.00 kg CO₂e
    """
    client.post("/ui/users", data={"name": "Fani Hagos", "email": "fani@test.se"}, follow_redirects=True)

    client.post("/ui/activities", data={
        "user_id": "1", "category": "transport", "key": "bil",
        "amount": "100", "date_str": "2026-05-18",
    }, follow_redirects=True)

    client.post("/ui/activities", data={
        "user_id": "1", "category": "mat", "key": "nötkött",
        "amount": "1", "date_str": "2026-05-20",
    }, follow_redirects=True)

    client.post("/ui/activities", data={
        "user_id": "1", "category": "energi", "key": "el",
        "amount": "100", "date_str": "2026-05-24",  # söndag = sista dagen i veckan
    }, follow_redirects=True)


class TestWeeklyReportUI:
    """Tester för veckorapporten (UI)."""

    def test_report_page_loads(self, client):
        """Rapportsidan ska laddas utan fel."""
        response = client.get("/ui/reports/weekly")
        assert response.status_code == 200

    def test_report_shows_total_co2e(self, client):
        """Veckorapporten ska visa korrekt total CO₂e."""
        create_user_and_activities(client)

        response = client.get("/ui/reports/weekly?user_id=1&week_start=2026-05-18")
        assert response.status_code == 200
        # Förväntat: 21.00 + 26.50 + 1.50 = 49.00
        assert "49.00" in response.text

    def test_report_excludes_outside_week(self, client):
        """Aktiviteter utanför veckan ska inte ingå i rapporten."""
        create_user_and_activities(client)

        # Logga en aktivitet utanför veckan (veckan efter)
        client.post("/ui/activities", data={
            "user_id": "1", "category": "transport", "key": "bil",
            "amount": "1000", "date_str": "2026-05-25",  # nästa måndag
        }, follow_redirects=True)

        response = client.get("/ui/reports/weekly?user_id=1&week_start=2026-05-18")
        # Aktiviteten på 1000 km (210 kg CO₂e) ska INTE finnas med
        assert "210" not in response.text
        assert "49.00" in response.text

    def test_report_invalid_date_format(self, client):
        """Ogiltigt datumformat ska ge felmeddelande."""
        create_user_and_activities(client)

        response = client.get("/ui/reports/weekly?user_id=1&week_start=fel-datum")
        assert response.status_code == 200
        assert "datum" in response.text.lower() or "ogiltigt" in response.text.lower()

    def test_report_nonexistent_user(self, client):
        """Rapport för icke-existerande användare ska ge felmeddelande."""
        response = client.get("/ui/reports/weekly?user_id=9999&week_start=2026-05-18")
        assert response.status_code == 200
        assert "hittades inte" in response.text.lower()


class TestWeeklyReportAPI:
    """Tester för veckorapport-API:et (JSON via GET /reports/weekly)."""

    def test_api_returns_json(self, client):
        """API-endpointen ska returnera giltig JSON."""
        create_user_and_activities(client)

        response = client.get("/reports/weekly?user_id=1&week_start=2026-05-18")
        assert response.status_code == 200
        data = response.json()
        assert "total_co2e" in data
        assert "activities" in data

    def test_api_correct_total(self, client):
        """API:et ska returnera korrekt total CO₂e."""
        create_user_and_activities(client)

        response = client.get("/reports/weekly?user_id=1&week_start=2026-05-18")
        data = response.json()
        assert data["total_co2e"] == pytest.approx(49.00, abs=0.01)

    def test_api_correct_week_end(self, client):
        """API:et ska returnera korrekt week_end (start + 6 dagar)."""
        create_user_and_activities(client)

        response = client.get("/reports/weekly?user_id=1&week_start=2026-05-18")
        data = response.json()
        assert data["week_start"] == "2026-05-18"
        assert data["week_end"] == "2026-05-24"

    def test_api_invalid_date(self, client):
        """Ogiltigt datum i API:et ska ge 422."""
        create_user_and_activities(client)

        response = client.get("/reports/weekly?user_id=1&week_start=fel")
        assert response.status_code == 422

    def test_api_nonexistent_user(self, client):
        """API-anrop för icke-existerande användare ska ge 404."""
        response = client.get("/reports/weekly?user_id=9999&week_start=2026-05-18")
        assert response.status_code == 404

    def test_api_empty_week(self, client):
        """En vecka utan aktiviteter ska ge total_co2e = 0."""
        create_user_and_activities(client)

        # Vecka utan aktiviteter (en vecka före)
        response = client.get("/reports/weekly?user_id=1&week_start=2026-05-11")
        data = response.json()
        assert data["total_co2e"] == 0.0
        assert data["activities"] == []
