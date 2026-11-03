from datetime import date

import pytest

from app.db import init_db, lade_trainings, speichere_training
from app.models import Satz, Training


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


def test_leere_db_gibt_leeres_tuple(db):
    assert lade_trainings(db) == ()


def test_training_speichern_und_laden(db):
    training = Training(
        datum=date(2024, 1, 15),
        saetze=(
            Satz(uebung="Kniebeuge", gewicht=80.0, wiederholungen=5),
            Satz(uebung="Bankdruecken", gewicht=60.0, wiederholungen=8),
        ),
    )
    speichere_training(db, training)
    geladen = lade_trainings(db)
    assert geladen == (training,)


def test_trainings_kommen_nach_datum_sortiert(db):
    spaeter = Training(datum=date(2024, 3, 1), saetze=(Satz("Deadlift", 100.0, 3),))
    frueher = Training(datum=date(2024, 1, 1), saetze=(Satz("Rudern", 50.0, 10),))
    speichere_training(db, spaeter)
    speichere_training(db, frueher)
    geladen = lade_trainings(db)
    assert geladen[0].datum < geladen[1].datum
    assert geladen == (frueher, spaeter)
