"""A1B: Unterschied pure function vs. Prozedur mit Tests belegt."""
from datetime import date

from app.db import init_db, lade_trainings, speichere_training
from app.models import Satz, Training
from app.services.volumen import training_volumen


def test_training_volumen_ist_pure(beispiel_trainings):
    training = beispiel_trainings[0]   # 80 kg x 8 + 100 kg x 5
    vorher = training

    assert training_volumen(training) == 1140.0
    assert training_volumen(training) == 1140.0   # gleicher Input -> gleicher Output
    assert training == vorher                     # Parameter unverändert


def test_training_ohne_saetze_hat_volumen_null():
    assert training_volumen(Training(date(2026, 11, 2), ())) == 0.0


def test_speichere_training_hat_seiteneffekt(tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    training = Training(date(2026, 11, 2), (Satz("Bankdrücken", 80.0, 8),))

    assert speichere_training(db, training) == 1
    assert speichere_training(db, training) == 2  # gleicher Input -> anderes Ergebnis
    assert len(lade_trainings(db)) == 2           # Zustand der DB hat sich verändert