"""Routes: dünn halten -> Request lesen, Service aufrufen, Template rendern."""
from datetime import date

from flask import (Blueprint, Response, current_app, flash, redirect,
                   render_template, request, url_for)

from app.db import lade_trainings, speichere_training, speichere_trainings
from app.services.bestenliste import bestenliste as berechne_bestenliste
from app.services.csv_import import importiere_csv
from app.services.erfassen import ANZAHL_ZEILEN, parse_formular
from app.services.filter import (SORTIERUNGEN, alle_uebungen,
                                 parse_suchparameter, suche)
from app.services.statistik import (balken_prozent, max_volumen,
                                    wochen_statistik)
from app.services.vergleich import schwerste_gewichte_funktional
from app.services.volumen import training_volumen

bp = Blueprint("main", __name__)


def db() -> str:
    return current_app.config["DATABASE"]


@bp.app_template_filter("kg")
def format_kg(wert: float) -> str:
    """1234.5 -> 1'234.5 (Schweizer Tausendertrennung)."""
    text = f"{wert:,.1f}".replace(",", "'")
    return text[:-2] if text.endswith(".0") else text


@bp.get("/")
def index():
    trainings = lade_trainings(db())
    letzte = tuple(reversed(trainings[-5:]))
    return render_template("index.html", letzte=letzte, anzahl=len(trainings),
                           volumen=training_volumen)


@bp.route("/trainings/neu", methods=["GET", "POST"])
def training_neu():
    if request.method == "POST":
        training, fehler = parse_formular(request.form)
        if training:
            speichere_training(db(), training)
            flash(f"Training vom {training.datum:%d.%m.%Y} gespeichert.")
            return redirect(url_for("main.trainings"))
        return render_template("training_neu.html", fehler=fehler, form=request.form,
                               zeilen=ANZAHL_ZEILEN), 400
    return render_template("training_neu.html", fehler=(), form={"datum": date.today().isoformat()},
                           zeilen=ANZAHL_ZEILEN)


@bp.get("/trainings")
def trainings():
    alle = lade_trainings(db())
    parameter = parse_suchparameter(request.args)
    ergebnis = suche(alle, parameter)
    return render_template("trainings.html", ergebnis=ergebnis, p=parameter,
                           zeilen=tuple(zip(ergebnis.trainings, ergebnis.volumina)),
                           sortierungen=SORTIERUNGEN, uebungen=alle_uebungen(alle),
                           anzahl_total=len(alle))


@bp.route("/import", methods=["GET", "POST"])
def import_csv():
    if request.method == "POST":
        datei = request.files.get("datei")
        if not datei or not datei.filename:
            flash("Bitte eine CSV-Datei auswählen.")
            return redirect(url_for("main.import_csv"))
        text = datei.read().decode("utf-8", errors="replace")
        ergebnis = importiere_csv(text)
        speichere_trainings(db(), ergebnis.trainings)
        return render_template("import_ergebnis.html", ergebnis=ergebnis)
    return render_template("import.html")


@bp.get("/export")
def export():
    # STAND VORHER (für B1A / D1): bewusst imperativ direkt in der Route.
    trainings = lade_trainings(db())
    zeilen = []
    zeilen.append("datum,uebung,gewicht,wiederholungen")
    for training in trainings:
        for satz in training.saetze:
            zeile = (str(training.datum) + "," + satz.uebung + ","
                     + str(satz.gewicht) + "," + str(satz.wiederholungen))
            zeilen.append(zeile)
    inhalt = ""
    for zeile in zeilen:
        inhalt = inhalt + zeile + "\n"
    return Response(inhalt, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=trainings.csv"})


@bp.get("/statistik")
def statistik():
    alle = lade_trainings(db())
    uebung = request.args.get("uebung", "").strip() or None
    wochen = wochen_statistik(alle, uebung)
    maximum = max_volumen(wochen)
    return render_template("statistik.html", wochen=wochen, uebung=uebung or "",
                           uebungen=alle_uebungen(alle), maximum=maximum,
                           balken=balken_prozent, hat_trainings=bool(alle))


@bp.get("/bestenliste")
def bestenliste():
    alle = lade_trainings(db())
    return render_template("bestenliste.html", liste=berechne_bestenliste(alle),
                           maxima=schwerste_gewichte_funktional(alle))
