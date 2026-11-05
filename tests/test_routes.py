import io
from datetime import date

from app.db import speichere_training
from app.models import Satz, Training
from app.services.csv_import import importiere_csv


def _speichere(app, *trainings):
    for t in trainings:
        speichere_training(app.config["DATABASE"], t)


def test_alle_seiten_leer_erreichbar(client):
    for url in ("/", "/trainings", "/trainings/neu", "/statistik", "/bestenliste", "/import", "/export"):
        assert client.get(url).status_code == 200, url
    assert "Noch keine Trainings erfasst" in client.get("/statistik").get_data(as_text=True)


def test_training_erfassen(client):
    antwort = client.post("/trainings/neu", data={
        "datum": "2026-11-02", "uebung_0": "Bankdrücken", "gewicht_0": "80", "wdh_0": "8"},
        follow_redirects=True)
    html = antwort.get_data(as_text=True)
    assert antwort.status_code == 200
    assert "gespeichert" in html and "Bankdrücken" in html


def test_training_erfassen_fehler(client):
    antwort = client.post("/trainings/neu", data={"datum": "", "uebung_0": "Bankdrücken"})
    assert antwort.status_code == 400
    assert "nicht gespeichert" in antwort.get_data(as_text=True)


def test_filter_route(app, client):
    _speichere(app, Training(date(2026, 11, 2), (Satz("Kreuzheben", 140.0, 3),)),
               Training(date(2026, 11, 3), (Satz("Rudern", 60.0, 10),)))
    html = client.get("/trainings?uebung=Rudern").get_data(as_text=True)
    assert "1 von 2 Trainings" in html


def test_export_inhalt_exakt(app, client):
    """Sichert das Verhalten von /export ab (wichtig fürs Refactoring!)."""
    _speichere(app, Training(date(2026, 11, 3), (Satz("Rudern", 60.0, 10),)),
               Training(date(2026, 11, 2), (Satz("Bankdrücken", 82.5, 8), Satz("Kniebeugen", 100.0, 5))))
    antwort = client.get("/export")
    assert antwort.mimetype == "text/csv"
    assert "attachment" in antwort.headers["Content-Disposition"]
    assert antwort.get_data(as_text=True) == (
        "datum,uebung,gewicht,wiederholungen\n"
        "2026-11-02,Bankdrücken,82.5,8\n"
        "2026-11-02,Kniebeugen,100.0,5\n"
        "2026-11-03,Rudern,60.0,10\n"
    )


def test_export_import_roundtrip(app, client):
    original = (Training(date(2026, 11, 2), (Satz("Bankdrücken", 82.5, 8),)),)
    _speichere(app, *original)
    csv_text = client.get("/export").get_data(as_text=True)
    assert importiere_csv(csv_text).trainings == original


def test_import_upload(client):
    daten = "datum,uebung,gewicht,wiederholungen\n2026-11-02,Bankdrücken,80,8\nkaputt\n".encode()
    antwort = client.post("/import", data={"datei": (io.BytesIO(daten), "t.csv")},
                          content_type="multipart/form-data")
    html = antwort.get_data(as_text=True)
    assert antwort.status_code == 200
    assert "Übersprungene Zeilen" in html
    assert "Bankdrücken" in client.get("/trainings").get_data(as_text=True)


def test_statistik_und_bestenliste_mit_daten(app, client):
    _speichere(app, Training(date(2026, 11, 2), (Satz("Kreuzheben", 140.0, 3),)))
    assert "KW 45 / 2026" in client.get("/statistik").get_data(as_text=True)
    assert "Kreuzheben" in client.get("/bestenliste").get_data(as_text=True)
