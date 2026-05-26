# tests/conftest.py
# Delade test-fixtures som används av alla testfiler.
# pytest hittar denna fil automatiskt och kör fixtures vid behov.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_session
from app.models import EmissionFactor, User, Activity


# ── Testdatabas ──────────────────────────────────────────────────────────────
# Vi använder en in-memory SQLite-databas för tester.
# Den är helt isolerad från app.db och försvinner efter varje testkörning.
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _seed_test_factors(session):
    """Lägger in ett litet urval emissionsfaktorer för tester."""
    factors = [
        EmissionFactor(category="transport", key="bil",       factor=0.210, unit="km"),
        EmissionFactor(category="transport", key="tåg",       factor=0.014, unit="km"),
        EmissionFactor(category="mat",       key="nötkött",   factor=26.50, unit="kg"),
        EmissionFactor(category="mat",       key="kyckling",  factor=5.70,  unit="kg"),
        EmissionFactor(category="energi",    key="el",        factor=0.015, unit="kWh"),
    ]
    session.add_all(factors)
    session.commit()


@pytest.fixture(scope="function")
def client():
    """
    Skapar en färsk testdatabas + FastAPI TestClient för varje testfunktion.
    - Tabeller skapas mot test_engine (in-memory SQLite)
    - Emissionsfaktorer seedas
    - get_session overridas till att använda testdatabasen
    - Tabeller rivs efter testet
    """
    # Skapa tabeller i testdatabasen
    Base.metadata.create_all(bind=test_engine)

    # Skapa en session och seeda emissionsfaktorer
    seed_session = TestingSessionLocal()
    _seed_test_factors(seed_session)
    seed_session.close()

    # Skapa en delad session för hela testet
    connection = test_engine.connect()
    test_session = TestingSessionLocal(bind=connection)

    def override_get_session():
        """Ersätter get_session-dependency med testdatabasens session."""
        try:
            yield test_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    # Teardown: rensa allt
    app.dependency_overrides.clear()
    test_session.close()
    connection.close()
    Base.metadata.drop_all(bind=test_engine)
