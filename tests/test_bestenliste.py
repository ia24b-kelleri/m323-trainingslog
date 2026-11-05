from datetime import date

import pytest

from app.models import Satz, Training
from app.services.bestenliste import bestenliste, geschaetztes_1rm


def test_epley():
    assert geschaetztes_1rm(Satz("X", 100.0, 3)) == pytest.approx(110.0)


def test_rangliste(beispiel_trainings):
    liste = bestenliste(beispiel_trainings)
    assert [b.uebung for b in liste] == ["Kreuzheben", "Kniebeugen", "Bankdrücken"]
    bank = liste[2]
    # 80×8 (101.3) schlägt 85×5 (99.2) und 82.5×6 (99.0)
    assert (bank.gewicht, bank.wiederholungen, bank.datum) == (80.0, 8, date(2026, 10, 26))
    assert bank.geschaetztes_1rm == pytest.approx(101.333, abs=0.001)


def test_gleichstand_alphabetisch_und_erster_satz_gewinnt():
    trainings = (
        Training(date(2026, 1, 1), (Satz("Rudern", 100.0, 5), Satz("Bankdrücken", 100.0, 5))),
        Training(date(2026, 1, 8), (Satz("Bankdrücken", 100.0, 5),)),
    )
    liste = bestenliste(trainings)
    assert [b.uebung for b in liste] == ["Bankdrücken", "Rudern"]
    assert liste[0].datum == date(2026, 1, 1)


def test_leer():
    assert bestenliste(()) == ()
