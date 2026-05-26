# app/db.py
# Hanterar databasanslutning och session-fabrik för SQLAlchemy.
# Vi använder SQLite som är enkelt att sätta upp och kräver ingen extern server.

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Databas-URL: SQLite-fil i projektrooten
DATABASE_URL = "sqlite:///./app.db"

# create_engine skapar en koppling till databasen.
# check_same_thread=False krävs för SQLite + FastAPI (flera requests kan använda samma connection)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal är en fabrik som skapar nya databas-sessioner.
# autocommit=False: vi styr när ändringar sparas
# autoflush=False: vi styr när data skickas till DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base är basklassen som alla SQLAlchemy-modeller ärver från.
# Den håller koll på alla tabeller vi definierar i models.py.
Base = declarative_base()


def get_session():
    """
    FastAPI-dependency som ger en DB-session per request.
    Stänger sessionen automatiskt när requesten är klar (via try/finally).
    Används med Depends(get_session) i route-funktioner.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Skapar alla tabeller i databasen om de inte redan finns.
    Kallas vid appstart i main.py.
    """
    from app import models  # noqa: F401 – importeras för att Base ska känna till modellerna
    Base.metadata.create_all(bind=engine)
