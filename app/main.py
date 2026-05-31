# app/main.py
# Applikationens hjärta – definierar alla routes (UI och API).
# UI-routes renderar HTML via Jinja2-templates.
# API-routes returnerar JSON och dokumenteras automatiskt i /docs (Swagger).

import datetime as dt
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_session, create_tables
from app.models import User, EmissionFactor, Activity
from app.schemas import WeeklyReportOut, ActivityOut

# ─── App-initialisering ──────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Körs automatiskt när servern startar.
    Skapar tabeller om de inte finns och kör seed om DB är tom.
    """
    create_tables()
    # Kör seed automatiskt om emissionsfaktorer saknas
    from app.db import SessionLocal
    from seed_data import seed

    db = SessionLocal()
    try:
        count = db.query(EmissionFactor).count()
        if count == 0:
            db.close()
            seed()
        else:
            db.close()
    except Exception:
        db.close()

    yield  # Applikationen körs här


app = FastAPI(
    title="Hållbarhetskollen",
    description="Logga vardagsaktiviteter och se din CO₂e-påverkan per vecka.",
    version="1.0.0",
    lifespan=lifespan,
)

# Servar statiska filer (CSS, bilder) från mappen /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2-templates läses från mappen /templates
templates = Jinja2Templates(directory="templates")


# ─── Startsida ───────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Startsidan – välkomstsida med snabblänkar."""
    return templates.TemplateResponse(request, "index.html")


# ─── Användarhantering (UI) ──────────────────────────────────────────────────


@app.get("/ui/users", response_class=HTMLResponse)
def ui_users_list(
    request: Request,
    ok: str | None = None,
    err: str | None = None,
    db: Session = Depends(get_session),
):
    """
    GET /ui/users – visar listan med alla användare och formulär för att skapa ny.
    ok/err är query-parametrar som sätts efter redirect (POST-redirect-GET-mönster).
    """
    users = db.query(User).order_by(User.id).all()
    return templates.TemplateResponse(
        request,
        "users.html",
        {"users": users, "ok": ok, "err": err},
    )


@app.post("/ui/users", response_class=HTMLResponse)
def ui_create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_session),
):
    """
    POST /ui/users – tar emot formuläret och skapar en ny användare.
    Validerar att namn och e-post inte är tomma och att e-post är unik.
    Använder Post-Redirect-Get (PRG) för att undvika dubbelskickning.
    """
    name = name.strip()
    email = email.strip().lower()

    # Validering
    if not name:
        users = db.query(User).order_by(User.id).all()
        return templates.TemplateResponse(
            request,
            "users.html",
            {"users": users, "err": "Namn får inte vara tomt.", "ok": None},
        )
    if not email or "@" not in email:
        users = db.query(User).order_by(User.id).all()
        return templates.TemplateResponse(
            request,
            "users.html",
            {"users": users, "err": "Ange en giltig e-postadress.", "ok": None},
        )

    # Kontrollera unik e-post
    existing = db.query(User).filter_by(email=email).first()
    if existing:
        users = db.query(User).order_by(User.id).all()
        return templates.TemplateResponse(
            request,
            "users.html",
            {
                "users": users,
                "err": f"E-postadressen {email} är redan registrerad.",
                "ok": None,
            },
        )

    user = User(name=name, email=email)
    db.add(user)
    db.commit()

    # PRG: redirect till GET med ok-meddelande i query-param
    from fastapi.responses import RedirectResponse

    return RedirectResponse(
        url=f"/ui/users?ok=Användaren+{name}+skapades!",
        status_code=303,
    )


@app.post("/ui/users/{user_id}/delete", response_class=HTMLResponse)
def ui_delete_user(
    user_id: int,
    db: Session = Depends(get_session),
):
    """
    POST /ui/users/{user_id}/delete – tar bort en användare.
    cascade="all, delete-orphan" i modellen tar automatiskt bort kopplade aktiviteter.
    """
    from fastapi.responses import RedirectResponse

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return RedirectResponse(
            url="/ui/users?err=Användaren+hittades+inte.", status_code=303
        )

    name = user.name
    db.delete(user)
    db.commit()
    return RedirectResponse(
        url=f"/ui/users?ok=Användaren+{name}+togs+bort.",
        status_code=303,
    )


# ─── Aktivitetsloggning (UI) ─────────────────────────────────────────────────


@app.get("/ui/activities", response_class=HTMLResponse)
def ui_activities(
    request: Request,
    user_id: int | None = None,
    ok: str | None = None,
    err: str | None = None,
    db: Session = Depends(get_session),
):
    """
    GET /ui/activities – visar formulär för att logga aktivitet och lista aktiviteter.
    Om user_id anges filtreras listan per användare.
    Emissionsfaktorer grupperas per kategori för dropdown-menyer (VG-krav).
    """
    users = db.query(User).order_by(User.name).all()
    activities = []
    selected_user = None

    if user_id:
        selected_user = db.query(User).filter_by(id=user_id).first()
        if selected_user:
            activities = (
                db.query(Activity)
                .filter_by(user_id=user_id)
                .order_by(Activity.date.desc())
                .all()
            )

    # Hämta emissionsfaktorer grupperade per kategori för dropdowns (VG)
    all_factors = (
        db.query(EmissionFactor)
        .order_by(EmissionFactor.category, EmissionFactor.key)
        .all()
    )
    categories = {}
    for f in all_factors:
        if f.category not in categories:
            categories[f.category] = []
        categories[f.category].append(
            {"key": f.key, "unit": f.unit, "factor": f.factor}
        )

    return templates.TemplateResponse(
        request,
        "activities.html",
        {
            "users": users,
            "activities": activities,
            "selected_user": selected_user,
            "categories": categories,
            "ok": ok,
            "err": err,
            "today": dt.date.today().isoformat(),
        },
    )


@app.post("/ui/activities", response_class=HTMLResponse)
def ui_create_activity(
    request: Request,
    user_id: int = Form(...),
    category: str = Form(...),
    key: str = Form(...),
    amount: str = Form(...),  # tas emot som str för bättre felhantering
    date_str: str = Form(...),
    db: Session = Depends(get_session),
):
    """
    POST /ui/activities – validerar och sparar en ny aktivitet.
    Beräknar CO₂e direkt: co2e = amount × emissionsfaktor.
    """
    from fastapi.responses import RedirectResponse

    # ── Validering ──────────────────────────────────────────────────────────

    # Parsa datum
    try:
        parsed_date = dt.date.fromisoformat(date_str)
    except ValueError:
        return RedirectResponse(
            url=f"/ui/activities?user_id={user_id}&err=Ogiltigt+datumformat+(YYYY-MM-DD).",
            status_code=303,
        )

    # Parsa mängd
    try:
        parsed_amount = float(amount.replace(",", "."))
        if parsed_amount <= 0:
            raise ValueError
    except ValueError:
        return RedirectResponse(
            url=f"/ui/activities?user_id={user_id}&err=Mängden+måste+vara+ett+positivt+tal.",
            status_code=303,
        )

    # Kontrollera att användaren finns
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return RedirectResponse(
            url="/ui/activities?err=Användaren+hittades+inte.", status_code=303
        )

    # ── CO₂e-beräkning ──────────────────────────────────────────────────────
    # Sök emissionsfaktor för vald category + key
    factor_row = db.query(EmissionFactor).filter_by(category=category, key=key).first()
    co2e = round(parsed_amount * factor_row.factor, 4) if factor_row else 0.0

    # ── Spara aktivitet ──────────────────────────────────────────────────────
    activity = Activity(
        user_id=user_id,
        category=category,
        key=key,
        amount=parsed_amount,
        date=parsed_date,
        co2e=co2e,
    )
    db.add(activity)
    db.commit()

    co2e_msg = f"{co2e:.2f}+kg+CO₂e" if factor_row else "0+(ingen+faktor+hittad)"
    return RedirectResponse(
        url=f"/ui/activities?user_id={user_id}&ok=Aktivitet+sparad!+CO₂e:+{co2e_msg}",
        status_code=303,
    )


# ─── Veckorapport (UI) ───────────────────────────────────────────────────────


@app.get("/ui/reports/weekly", response_class=HTMLResponse)
def ui_weekly_report(
    request: Request,
    user_id: int | None = None,
    week_start: str | None = None,
    db: Session = Depends(get_session),
):
    """
    GET /ui/reports/weekly – veckorapport för en användare.
    Beräknar total CO₂e för perioden week_start … week_start+6 dagar.
    """
    users = db.query(User).order_by(User.name).all()
    total_co2e = None
    activities = []
    err = None
    selected_user = None
    week_end = None

    if user_id and week_start:
        # Parsa och validera startdatum
        try:
            start = dt.date.fromisoformat(week_start)
        except ValueError:
            err = "Ogiltigt datumformat. Använd YYYY-MM-DD."
        else:
            end = start + dt.timedelta(days=6)
            week_end = end.isoformat()
            selected_user = db.query(User).filter_by(id=user_id).first()

            if not selected_user:
                err = "Användaren hittades inte."
            else:
                # Hämta alla aktiviteter i veckan för vald användare
                activities = (
                    db.query(Activity)
                    .filter(
                        Activity.user_id == user_id,
                        Activity.date >= start,
                        Activity.date <= end,
                    )
                    .order_by(Activity.date)
                    .all()
                )
                total_co2e = round(sum(a.co2e for a in activities), 2)

    return templates.TemplateResponse(
        request,
        "weekly.html",
        {
            "users": users,
            "selected_user": selected_user,
            "week_start": week_start,
            "week_end": week_end,
            "total_co2e": total_co2e,
            "activities": activities,
            "err": err,
        },
    )


# ─── Veckorapport (API / JSON) ───────────────────────────────────────────────


@app.get("/reports/weekly", response_model=WeeklyReportOut)
def api_weekly_report(
    user_id: int,
    week_start: str,
    db: Session = Depends(get_session),
):
    """
    GET /reports/weekly?user_id=...&week_start=YYYY-MM-DD
    Returnerar JSON med total CO₂e och lista av aktiviteter för veckan.
    Testbar via Swagger på /docs.
    """
    # Validera datum
    try:
        start = dt.date.fromisoformat(week_start)
    except ValueError:
        raise HTTPException(status_code=422, detail="week_start måste vara YYYY-MM-DD.")

    end = start + dt.timedelta(days=6)

    # Kontrollera att användaren finns
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail=f"Användare med id={user_id} hittades inte."
        )

    activities = (
        db.query(Activity)
        .filter(
            Activity.user_id == user_id,
            Activity.date >= start,
            Activity.date <= end,
        )
        .order_by(Activity.date)
        .all()
    )

    total_co2e = round(sum(a.co2e for a in activities), 2)

    return WeeklyReportOut(
        user_id=user_id,
        week_start=start,
        week_end=end,
        total_co2e=total_co2e,
        activities=[ActivityOut.model_validate(a) for a in activities],
    )


# ─── API: Emissionsfaktorer (för AJAX-dropdowns, VG) ─────────────────────────


@app.get("/api/emission-factors")
def api_emission_factors(db: Session = Depends(get_session)):
    """
    GET /api/emission-factors
    Returnerar alla emissionsfaktorer grupperade per kategori.
    Används av JavaScript på aktivitetssidan för att fylla dropdown dynamiskt.
    """
    factors = (
        db.query(EmissionFactor)
        .order_by(EmissionFactor.category, EmissionFactor.key)
        .all()
    )
    result = {}
    for f in factors:
        if f.category not in result:
            result[f.category] = []
        result[f.category].append(
            {
                "key": f.key,
                "unit": f.unit,
                "factor": f.factor,
            }
        )
    return result
