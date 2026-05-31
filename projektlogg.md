# Projektlogg – Hållbarhetskollen

> **Projekt:** Hållbarhetskollen – CO₂e-tracker  
> **Kurs:** Projektmetodik inom IT, gmc VT2026  
> **Start:** 2026-05-21  
> **Mål:** Betyg VG

---

## Team och arbetsfördelning

| Namn | Primär roll | Ansvarsområden i projektet |
|------|-------------|----------------------------|
| **Usama Balhasal** | Backend-utvecklare | Ansvarig för backend: API, routes, databas (SQLite + SQLAlchemy) samt kvalitetssäkring (pytest). |
| **Fani Hagos** | Frontend-utvecklare | Ansvarig för frontend: Gränssnitt (UI), server-renderad HTML (Jinja2-templates) samt layout och design (CSS). |
| **Lukas Forsling** | Scrum Master & Utvecklare | Ansvarig för Scrum-processen (sprintplanering, mötesstruktur) samt delaktig i systemutveckling och slutrapport. |
| **Nicklas Eriksson** | Product Owner & Utvecklare | Ansvarig för kravuppfyllnad (G/VG-kriterier), PowerPoint-presentation samt delaktig i systemutveckling och slutrapport. |

---

## Projektstruktur (skapad 2026-05-21)

```
hållbarhetskollen/
  app/
    __init__.py      ← Python-paket (tom fil)
    main.py          ← Alla routes (UI + API), FastAPI-app
    db.py            ← SQLAlchemy engine, SessionLocal, get_session
    models.py        ← User, EmissionFactor, Activity-modeller
    schemas.py       ← Pydantic-scheman för validering och API
  templates/
    base.html        ← Gemensam layout, navbar, footer
    index.html       ← Startsida med hero
    users.html       ← Användarhantering (skapa, lista, ta bort)
    activities.html  ← Logga aktiviteter (VG-dropdowns)
    weekly.html      ← Veckorapport
  static/
    styles.css       ← Gemensam CSS (grön design, responsiv)
  tests/
    __init__.py
    conftest.py      ← In-memory testdatabas + TestClient fixture
    test_users.py    ← 8 tester för användarhantering
    test_activities.py ← 8 tester för aktivitetsloggning
    test_reports.py  ← 11 tester för veckorapport (UI + API)
  seed_data.py       ← Importerar 10 emissionsfaktorer till DB
  requirements.txt   ← Alla Python-beroenden
  app.db             ← SQLite-databas (skapas automatiskt vid start)
  projektlogg.md     ← Denna fil
```

---

## Viktiga tekniska beslut

| Datum | Beslut | Motivering |
|-------|--------|-----------|
| 2026-05-21 | CO₂e beräknas och sparas direkt i Activity-tabellen | Snabb läsning vid rapport, undviker join-beräkning |
| 2026-05-21 | `base.html` med Jinja2 `extends` | DRY – navigation och CSS definieras en gång |
| 2026-05-21 | Separat in-memory testdatabas via conftest.py | Tester påverkar inte produktionsdatabasen |
| 2026-05-21 | `seed_data.py` separat script | Idempotent (trygg att köra om), håller main.py ren |
| 2026-05-21 | Email-fält på User-modellen | Mer realistisk modell, unik identifiering |
| 2026-05-21 | Post-Redirect-Get (PRG) mönster i formulär | Undviker dubbelskickning vid siduppdatering |
| 2026-05-21 | `/api/emission-factors` JSON-endpoint | Möjliggör dynamiska dropdowns via JavaScript (VG) |
| 2026-05-21 | CO₂e-preview i realtid med JavaScript | VG-krav: användarvänlig GUI |

---

## Sprint-logg

### 2026-05-21 – Sprint start + hela Fas 1–5 slutförd

**Vad vi gjort:**

**Fas 1 – Projektgrund:**
- Skapat hela mappstrukturen (app/, templates/, static/, tests/)
- Skrivit `requirements.txt` med fastapi, uvicorn, sqlalchemy, jinja2, pytest, httpx
- Skapat `app/db.py` med SQLAlchemy engine (SQLite), SessionLocal och get_session-dependency
- Skapat `app/models.py` med tre modeller: User, EmissionFactor, Activity
- Skapat `app/schemas.py` med Pydantic-scheman och field_validators
- Skapat `seed_data.py` med 10 emissionsfaktorer i 3 kategorier

**Fas 2 – Användarhantering:**
- Implementerat GET/POST `/ui/users` och POST `/ui/users/{id}/delete`
- Skapat `templates/base.html` med navbar och footer
- Skapat `templates/users.html` med formulär, tabell och JS-validering
- Skapat `static/styles.css` med grön design, CSS-variabler, responsiv layout

**Fas 3 – Aktivitetsloggning:**
- Implementerat GET/POST `/ui/activities` med CO₂e-beräkning
- Skapat `templates/activities.html` med dynamiska dropdowns (VG)
- CO₂e-förhandsgranskning i realtid via JavaScript

**Fas 4 – Veckorapport:**
- Implementerat GET `/ui/reports/weekly` (UI)
- Implementerat GET `/reports/weekly` API med Pydantic-schema (JSON)
- Skapat `templates/weekly.html` med totalsiffra, tabell och procentandel

**Fas 5 – Tester:**
- Skapat `tests/conftest.py` med in-memory SQLite och dependency override
- Skapat `tests/test_users.py` – 8 tester
- Skapat `tests/test_activities.py` – 8 tester
- Skapat `tests/test_reports.py` – 11 tester

**Testresultat:**
```
27 passed in 0.79s ✓
```

**Problem vi stötte på och hur vi löste dem:**

| Problem | Lösning |
|---------|---------|
| `no such table: users` i tester | conftest.py använde in-memory DB men varje TestClient-request öppnade ny connection. Löstes med explicit `connection`-objekt som hålls öppen under hela testet. |
| `UnicodeEncodeError` i seed_data.py | Windows-terminalen klarar inte emoji i print(). Byttes mot ASCII [OK]/[FEL]. |
| DeprecationWarning: TemplateResponse | Bytt ordning på parametrar enligt ny Starlette-API: request som första arg. |

**Emissionsfaktorer i databasen:**

| Kategori | Nyckel | Faktor | Enhet |
|----------|--------|--------|-------|
| transport | bil | 0.21 | km |
| transport | buss | 0.089 | km |
| transport | tåg | 0.014 | km |
| transport | flyg | 0.255 | km |
| mat | nötkött | 26.5 | kg |
| mat | kyckling | 5.7 | kg |
| mat | vegetarisk | 2.0 | kg |
| energi | el | 0.015 | kWh |
| energi | naturgas | 0.2 | kWh |
| energi | fjärrvärme | 0.066 | kWh |

**Hinder:** Inga

---

## Skapade filer (kronologisk ordning)

| Datum | Fil | Beskrivning |
|-------|-----|-------------|
| 2026-05-21 | `projektlogg.md` | Denna logg |
| 2026-05-21 | `requirements.txt` | Python-beroenden |
| 2026-05-21 | `app/__init__.py` | Paket-init |
| 2026-05-21 | `app/db.py` | Databaskoppling |
| 2026-05-21 | `app/models.py` | SQLAlchemy-modeller |
| 2026-05-21 | `app/schemas.py` | Pydantic-scheman |
| 2026-05-21 | `app/main.py` | Alla routes (UI + API) |
| 2026-05-21 | `seed_data.py` | Emissionsfaktor-seed |
| 2026-05-21 | `static/styles.css` | Gemensam CSS |
| 2026-05-21 | `templates/base.html` | Grundlayout |
| 2026-05-21 | `templates/index.html` | Startsida |
| 2026-05-21 | `templates/users.html` | Användarhantering |
| 2026-05-21 | `templates/activities.html` | Aktivitetsloggning |
| 2026-05-21 | `templates/weekly.html` | Veckorapport |
| 2026-05-21 | `tests/__init__.py` | Test-paket |
| 2026-05-21 | `tests/conftest.py` | Testfixtures |
| 2026-05-21 | `tests/test_users.py` | Användartester |
| 2026-05-21 | `tests/test_activities.py` | Aktivitetstester |
| 2026-05-21 | `tests/test_reports.py` | Rapporttester |

---

## Idéer och förbättringar

- Eventuellt lägga till ett stapeldiagram per kategori i veckorapporten
- Möjlighet att filtrera aktiviteter per datumintervall
- Exportera veckorapport som CSV
- Lägg till fler emissionsfaktorer (t.ex. konsumtion, flygresor i km)

---

## Vad som återstår

- [x] Fas 1: Projektgrund (mappar, requirements, db, models, seed)
- [x] Fas 2: Användarhantering + CSS-grund
- [x] Fas 3: Aktivitetsloggning + VG-dropdowns
- [x] Fas 4: Veckorapport + API
- [x] Fas 5: CSS-polish, navigation
- [x] Tester – 27/27 gröna
- [ ] Scrum-möte 2 (mitt i sprint)
- [ ] Scrum-möte 3 (slutet av sprint)
- [ ] Git-repo setup och commits
- [ ] Redovisning (15 min live-demo)
- [ ] Processdokument (max 2 sidor)
- [ ] PowerPoint-presentation

---

## Hur man kör projektet

```bash
# 1. Installera beroenden
pip install -r requirements.txt

# 2. Starta servern
python -m uvicorn app.main:app --reload

# 3. Öppna webbläsaren
# http://localhost:8000         ← Startsida
# http://localhost:8000/ui/users       ← Användare
# http://localhost:8000/ui/activities  ← Aktiviteter
# http://localhost:8000/ui/reports/weekly ← Veckorapport
# http://localhost:8000/docs           ← Swagger API

# 4. Kör tester
python -m pytest tests/ -v
```

---

*Loggen uppdateras löpande under projektets gång.*
