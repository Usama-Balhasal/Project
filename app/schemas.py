# app/schemas.py
# Pydantic-scheman för validering och API-svar (JSON).
# Separerar API-kontraktet från databasmodellerna.

from pydantic import BaseModel, EmailStr, field_validator
from datetime import date


# ─── User-scheman ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Validerar indata när en ny användare skapas."""
    name: str
    email: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Namn får inte vara tomt.")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v.strip() or "@" not in v:
            raise ValueError("Ange en giltig e-postadress.")
        return v.strip().lower()


class UserOut(BaseModel):
    """Schema för att returnera användardata i API-svar."""
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


# ─── Activity-scheman ────────────────────────────────────────────────────────

class ActivityCreate(BaseModel):
    """Validerar indata när en ny aktivitet loggas."""
    user_id: int
    category: str
    key: str
    amount: float
    date: date

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Mängd måste vara större än 0.")
        return v

    @field_validator("category", "key")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Fältet får inte vara tomt.")
        return v.strip()


class ActivityOut(BaseModel):
    """Schema för att returnera aktivitetsdata i API-svar."""
    id: int
    user_id: int
    category: str
    key: str
    amount: float
    date: date
    co2e: float

    model_config = {"from_attributes": True}


# ─── Rapport-scheman ─────────────────────────────────────────────────────────

class WeeklyReportOut(BaseModel):
    """API-svar för veckorapport."""
    user_id: int
    week_start: date
    week_end: date
    total_co2e: float
    activities: list[ActivityOut]
