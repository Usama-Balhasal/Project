# tests/test_users.py
# Testar användarhantering: skapa, lista och ta bort användare.

import pytest


class TestCreateUser:
    """Tester för att skapa användare via POST /ui/users."""

    def test_create_user_success(self, client):
        """En användare med giltigt namn och e-post ska skapas framgångsrikt."""
        response = client.post(
            "/ui/users",
            data={"name": "Anna Svensson", "email": "anna@test.se"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Anna Svensson" in response.text
        assert "skapades" in response.text.lower()

    def test_create_user_empty_name(self, client):
        """Tom namnfält ska ge ett felmeddelande."""
        response = client.post(
            "/ui/users",
            data={"name": "   ", "email": "test@test.se"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Namn får inte vara tomt" in response.text

    def test_create_user_invalid_email(self, client):
        """Ogiltig e-post (utan @) ska ge felmeddelande."""
        response = client.post(
            "/ui/users",
            data={"name": "Bo Karlsson", "email": "inteenemail"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "giltig e-postadress" in response.text.lower()

    def test_create_user_duplicate_email(self, client):
        """Duplicerad e-post ska ge felmeddelande."""
        client.post(
            "/ui/users",
            data={"name": "Anna", "email": "duplikat@test.se"},
            follow_redirects=True,
        )
        response = client.post(
            "/ui/users",
            data={"name": "Anna 2", "email": "duplikat@test.se"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "redan registrerad" in response.text.lower()


class TestListUsers:
    """Tester för att lista användare via GET /ui/users."""

    def test_list_users_empty(self, client):
        """Tom lista ska visas utan fel."""
        response = client.get("/ui/users")
        assert response.status_code == 200
        assert "Inga användare" in response.text

    def test_list_users_shows_created(self, client):
        """Skapade användare ska synas i listan."""
        client.post(
            "/ui/users",
            data={"name": "Lukas Forsling", "email": "lukas@test.se"},
            follow_redirects=True,
        )
        response = client.get("/ui/users")
        assert "Lukas Forsling" in response.text
        assert "lukas@test.se" in response.text


class TestDeleteUser:
    """Tester för att ta bort användare."""

    def test_delete_user_success(self, client):
        """En befintlig användare ska kunna tas bort och ett bekräftelsemeddelande visas."""
        # Skapa användare
        client.post(
            "/ui/users",
            data={"name": "Nicklas Eriksson", "email": "nicklas@test.se"},
            follow_redirects=True,
        )
        # Kontrollera att användaren syns i listan
        resp = client.get("/ui/users")
        assert "Nicklas Eriksson" in resp.text

        # Ta bort användaren (id=1 i en tom testdb)
        response = client.post("/ui/users/1/delete", follow_redirects=True)
        assert response.status_code == 200
        # Kontrollera att bekräftelsemeddelandet visas
        assert "togs bort" in response.text.lower()

    def test_delete_nonexistent_user(self, client):
        """Försök att ta bort en icke-existerande användare ska ge felmeddelande."""
        response = client.post("/ui/users/9999/delete", follow_redirects=True)
        assert response.status_code == 200
        assert "hittades inte" in response.text.lower()
