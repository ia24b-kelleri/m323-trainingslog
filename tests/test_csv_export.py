from datetime import date

from app.models import Satz, Training
from app.services.csv_export import exportiere_csv
from app.services.csv_import import importiere_csv


def test_leer_nur_kopfzeile():
    assert exportiere_csv(()) == "datum,uebung,gewicht,wiederholungen\n"


def test_komma_im_uebungsnamen_wird_korrekt_gequotet():
    t = (Training(date(2026, 11, 2), (Satz("Rudern, eng", 60.0, 10),)),)
    text = exportiere_csv(t)
    assert '"Rudern, eng"' in text
    assert importiere_csv(text).trainings == t     # Roundtrip klappt jetzt auch damit
