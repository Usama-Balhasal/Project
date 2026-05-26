# app/models.py
# Definierar databasmodellerna (tabeller) med SQLAlchemy ORM.
# Varje klass representerar en tabell i SQLite-databasen.

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    """
    Representerar en användare i systemet.
    Id genereras automatiskt av databasen – syns inte i formulär.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)

    # Relation: en användare kan ha många aktiviteter
    # cascade="all, delete-orphan" = när en användare tas bort, tas även aktiviteterna bort
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} name={self.name!r}>"


class EmissionFactor(Base):
    """
    Emissionsfaktorer kopplar en aktivitetstyp till kg CO₂e per enhet.
    Exempel: category="transport", key="bil", factor=0.21, unit="km"
    → att köra 100 km med bil ger 21 kg CO₂e.
    """
    __tablename__ = "emission_factors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(50), nullable=False)   # t.ex. "transport"
    key = Column(String(50), nullable=False)         # t.ex. "bil"
    factor = Column(Float, nullable=False)           # kg CO₂e per enhet
    unit = Column(String(20), nullable=False)        # t.ex. "km"

    def __repr__(self):
        return f"<EmissionFactor {self.category}/{self.key} = {self.factor} kg CO₂e/{self.unit}>"


class Activity(Base):
    """
    En loggad aktivitet kopplad till en användare.
    co2e beräknas och sparas direkt när aktiviteten skapas:
        co2e = amount × factor (från EmissionFactor)
    Om ingen matchande faktor finns, sparas co2e=0.
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)
    key = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)           # mängd i enhetens valuta (km, kg, kWh)
    date = Column(Date, nullable=False)
    co2e = Column(Float, nullable=False, default=0.0)  # kg CO₂e, beräknas vid insättning

    # Relation tillbaka till User
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<Activity id={self.id} user={self.user_id} {self.category}/{self.key} co2e={self.co2e}>"
