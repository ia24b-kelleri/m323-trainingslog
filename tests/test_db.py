from datetime import date

from app.db import (init_db, lade_trainings, loesche_alle, speichere_training,
                    speichere_trainings)
from app.models import Satz, Training


def test_leere_db_liefert_leeres_tuple(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    assert lade_trainings(db) == ()


def test_roundtrip_mit_zwei_saetzen(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    t = Training(date(2026, 11, 2), (Satz("Bankdrücken", 80.0, 8), Satz("Rudern", 60.0, 10)))
    neue_id = speichere_training(db, t)
    geladen = lade_trainings(db)
    assert geladen == (Training(t.datum, t.saetze, neue_id),)


def test_sortiert_nach_datum(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    speichere_trainings(db, (Training(date(2026, 11, 5), (Satz("A", 1.0, 1),)),
                             Training(date(2026, 11, 1), (Satz("B", 1.0, 1),))))
    assert [t.datum.day for t in lade_trainings(db)] == [1, 5]


def test_training_ohne_saetze_und_reihenfolge_der_saetze(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    speichere_training(db, Training(date(2026, 1, 1), ()))
    speichere_training(db, Training(date(2026, 1, 2), (Satz("Z", 1.0, 1), Satz("A", 2.0, 2))))
    leer, zwei = lade_trainings(db)
    assert leer.saetze == ()
    assert [s.uebung for s in zwei.saetze] == ["Z", "A"]


def test_loesche_alle(tmp_path):
    db = str(tmp_path / "t.db")
    init_db(db)
    speichere_training(db, Training(date(2026, 1, 1), (Satz("A", 1.0, 1),)))
    loesche_alle(db)
    assert lade_trainings(db) == ()
