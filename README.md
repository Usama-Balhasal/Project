# 🌱 Hållbarhetskollen

Hållbarhetskollen är en webbtjänst utvecklad på uppdrag av Gävle kommun som ett skolprojekt inom kursen *Projektmetodik inom IT (VT2026)*. Tanken är enkel: du loggar vad du gör i vardagen – resor, mat och energiförbrukning – och får direkt se hur stor klimatpåverkan det har i kilo CO₂e (koldioxidekvivalenter).

---

## ✨ Funktioner

- 👤 **Användarhantering** – Skapa, lista och ta bort användare
- 📋 **Logga aktiviteter** – Välj kategori och aktivitet från smarta dropdowns
- ⚡ **CO₂e-preview** – Se beräknad klimatpåverkan i realtid innan du sparar
- 📊 **Veckorapport** – Total CO₂e för en valfri vecka, med färgkodad feedback
- 🔌 **REST API** – JSON-endpoint för veckorapport, dokumenterad via Swagger
- 🎨 **Responsiv design** – Fungerar på både dator och mobil

### Aktivitetskategorier och emissionsfaktorer

| Kategori | Aktivitet | Faktor | Enhet |
|----------|-----------|--------|-------|
| 🚗 Transport | Bil | 0,21 kg CO₂e | per km |
| 🚗 Transport | Buss | 0,089 kg CO₂e | per km |
| 🚗 Transport | Tåg | 0,014 kg CO₂e | per km |
| 🚗 Transport | Flyg | 0,255 kg CO₂e | per km |
| 🥩 Mat | Nötkött | 26,5 kg CO₂e | per kg |
| 🥩 Mat | Kyckling | 5,7 kg CO₂e | per kg |
| 🥩 Mat | Vegetarisk | 2,0 kg CO₂e | per kg |
| ⚡ Energi | El | 0,015 kg CO₂e | per kWh |
| ⚡ Energi | Naturgas | 0,20 kg CO₂e | per kWh |
| ⚡ Energi | Fjärrvärme | 0,066 kg CO₂e | per kWh |

---

## 🛠️ Tech stack

| Teknik | Vad det används till |
|--------|----------------------|
| **FastAPI** | Webbramverk – hanterar routes och API |
| **Uvicorn** | ASGI-server som kör FastAPI |
| **SQLite** | Databas – sparas som `app.db` i projektmappen |
| **SQLAlchemy** | ORM – Python-klasser mappar mot databastabeller |
| **Jinja2** | HTML-templates med arv (`extends`) |
| **pytest** | Automatiserade tester med isolerad testdatabas |
| **httpx** | HTTP-klient som används av TestClient i tester |

---

## 📁 Projektstruktur

```
hållbarhetskollen/
│
├── app/
│   ├── __init__.py        ← Gör "app" till ett Python-paket
│   ├── main.py            ← Alla routes: UI (/ui/...) och API (/reports/...)
│   ├── db.py              ← Databasanslutning och session-factory
│   ├── models.py          ← SQLAlchemy-modeller: User, EmissionFactor, Activity
│   └── schemas.py         ← Pydantic-scheman för validering och API-svar
│
├── templates/
│   ├── base.html          ← Gemensam layout med navigation och footer
│   ├── index.html         ← Startsida
│   ├── users.html         ← Skapa, lista och ta bort användare
│   ├── activities.html    ← Logga aktiviteter (dynamiska dropdowns)
│   └── weekly.html        ← Veckorapport med total CO₂e
│
├── static/
│   └── styles.css         ← Gemensam CSS: design, navigation, tabeller
│
├── tests/
│   ├── conftest.py        ← Testfixtures: in-memory SQLite + TestClient
│   ├── test_users.py      ← 8 tester för användarhantering
│   ├── test_activities.py ← 8 tester för aktivitetsloggning
│   └── test_reports.py    ← 11 tester för veckorapport (UI + API)
│
├── seed_data.py           ← Importerar emissionsfaktorer till databasen
├── requirements.txt       ← Python-beroenden
├── projektlogg.md         ← Löpande dokumentation av hela processen
└── README.md              ← Den här filen
```

---

## 🚀 Kom igång

### 1. Klona repot

```bash
git clone https://github.com/Usama-Balhasal/Project
cd Project
```

### 2. Installera beroenden

```bash
pip install -r requirements.txt
```

### 3. Starta servern

```bash
python -m uvicorn app.main:app --reload
```

### 4. Öppna i webbläsaren

| URL | Beskrivning |
|-----|-------------|
| `http://localhost:8000` | Startsida |
| `http://localhost:8000/ui/users` | Hantera användare |
| `http://localhost:8000/ui/activities` | Logga aktiviteter |
| `http://localhost:8000/ui/reports/weekly` | Veckorapport |
| `http://localhost:8000/docs` | Swagger API-dokumentation |

---

## 🧪 Kör tester

Vi har 27 automatiserade tester med en helt isolerad in-memory-databas, så de påverkar aldrig din riktiga data.

```bash
python -m pytest tests/ -v
```

Förväntat resultat:

```
tests/test_activities.py ........  8 passed
tests/test_reports.py    ........... 11 passed
tests/test_users.py      ........  8 passed
======================== 27 passed in 0.79s ========================
```

---

## 🔌 API-dokumentation

FastAPI genererar automatiskt en interaktiv dokumentation via Swagger.

Öppna **[http://localhost:8000/docs](http://localhost:8000/docs)** när servern är igång.

### Tillgängliga API-endpoints

#### `GET /reports/weekly`
Hämtar veckorapport som JSON.

**Parametrar:**
| Parameter | Typ | Beskrivning | Exempel |
|-----------|-----|-------------|---------|
| `user_id` | int | Användarens ID | `1` |
| `week_start` | string | Veckans startdatum (måndag) | `2026-05-18` |

**Exempelsvar:**
```json
{
  "user_id": 1,
  "week_start": "2026-05-18",
  "week_end": "2026-05-24",
  "total_co2e": 49.0,
  "activities": [
    {
      "id": 1,
      "user_id": 1,
      "category": "transport",
      "key": "bil",
      "amount": 100.0,
      "date": "2026-05-18",
      "co2e": 21.0
    }
  ]
}
```

#### `GET /api/emission-factors`
Hämtar alla emissionsfaktorer grupperade per kategori (används av aktivitetssidans dropdowns).

---

## 📖 Hur CO₂e beräknas

CO₂e beräknas direkt när du sparar en aktivitet:

```
CO₂e (kg) = mängd × emissionsfaktor
```

**Exempel:**
- Bil 100 km → `100 × 0,21 = 21,0 kg CO₂e`
- Nötkött 2 kg → `2 × 26,5 = 53,0 kg CO₂e`
- El 200 kWh → `200 × 0,015 = 3,0 kg CO₂e`

Värdet sparas direkt i databasen för snabb åtkomst vid rapporter.

---

## 🌍 Emissionsfaktorernas källor

Faktorerna är hämtade från:
- **Naturvårdsverket** – svenska transport- och energifaktorer
- **IVL Svenska Miljöinstitutet** – livscykelanalyser för mat
- **IPCC 2022** – globala referensvärden

---

## 👥 Teamet

Projektet är utvecklat av ett tvärfunktionellt Scrum-team på kursen Projektmetodik:

| Namn | Primär roll | Ansvarsområden i projektet |
|------|-------------|----------------------------|
| **Usama Balhasal** | Backend-utvecklare | Ansvarig för backend: API, routes, databas (SQLite + SQLAlchemy) samt kvalitetssäkring (pytest). |
| **Fani Hagos** | Frontend-utvecklare | Ansvarig för frontend: Gränssnitt (UI), server-renderad HTML (Jinja2-templates) samt layout och design (CSS). |
| **Lucas Forsling** | Scrum Master & Utvecklare | Ansvarig för Scrum-processen (sprintplanering, mötesstruktur) samt delaktig i systemutveckling och slutrapport. |
| **Nicklas Eriksson** | Product Owner & Utvecklare | Ansvarig för kravuppfyllnad (G/VG-kriterier), PowerPoint-presentation samt delaktig i systemutveckling och slutrapport. |

---

## 📄 Licens

Det här projektet är ett skolprojekt och är inte licensierat för kommersiell användning.