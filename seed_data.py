# seed_data.py
# Importerar emissionsfaktorer till databasen.
# Körs en gång med: python seed_data.py
# Trygg att köra om – kontrollerar om data redan finns.

from app.db import SessionLocal, create_tables
from app.models import EmissionFactor


# Emissionsfaktorer: (category, key, factor kg CO₂e/enhet, unit)
# Källor: Naturvårdsverket, IVL Svenska Miljöinstitutet, IPCC 2022
EMISSION_FACTORS = [
    # ── Transport ──────────────────────────────────────────────────────────
    # Bil (genomsnittlig personbil, bensin): 0.21 kg CO₂e/km
    ("transport", "bil",    0.210, "km"),
    # Buss (stadsbuss, genomsnitt Sverige): 0.089 kg CO₂e/km per passagerare
    ("transport", "buss",   0.089, "km"),
    # Tåg (el, Sverige): 0.014 kg CO₂e/km per passagerare
    ("transport", "tåg",    0.014, "km"),
    # Flyg (kortdistans, inkl. höghöjdseffekter): 0.255 kg CO₂e/km per passagerare
    ("transport", "flyg",   0.255, "km"),

    # ── Mat ────────────────────────────────────────────────────────────────
    # Nötkött (produktion, transport): 26.5 kg CO₂e/kg
    ("mat", "nötkött",      26.50, "kg"),
    # Kyckling: 5.7 kg CO₂e/kg
    ("mat", "kyckling",      5.70, "kg"),
    # Vegetarisk (bönor, grönsaker, genomsnitt): 2.0 kg CO₂e/kg
    ("mat", "vegetarisk",    2.00, "kg"),

    # ── Energi ─────────────────────────────────────────────────────────────
    # El (Sverige, nordisk mix 2023): 0.015 kg CO₂e/kWh
    ("energi", "el",         0.015, "kWh"),
    # Naturgas (förbränning): 0.200 kg CO₂e/kWh
    ("energi", "naturgas",   0.200, "kWh"),
    # Fjärrvärme (Sverige, genomsnitt): 0.066 kg CO₂e/kWh
    ("energi", "fjärrvärme", 0.066, "kWh"),
]


def seed():
    """
    Läser in emissionsfaktorer i databasen.
    Hoppar över faktorer som redan finns (baserat på category + key),
    så skriptet är tryggt att köra flera gånger.
    """
    create_tables()
    db = SessionLocal()

    try:
        inserted = 0
        skipped = 0

        for category, key, factor, unit in EMISSION_FACTORS:
            # Kontrollera om faktorn redan finns
            existing = (
                db.query(EmissionFactor)
                .filter_by(category=category, key=key)
                .first()
            )
            if existing:
                skipped += 1
                continue

            ef = EmissionFactor(category=category, key=key, factor=factor, unit=unit)
            db.add(ef)
            inserted += 1

        db.commit()
        print(f"[OK] Seed klar: {inserted} faktorer tillagda, {skipped} redan i DB.")

    except Exception as e:
        db.rollback()
        print(f"[FEL] Fel vid seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
