"""A1I: Mutation vs. immutable Variante von nur_uebung."""
from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from app.models import Satz, Training
from app.services.bestenliste import bestenliste
from app.services.mutation_vergleich import (TrainingVeraenderbar,
                                             nur_uebung_mutierend)
from app.services.statistik import nur_uebung

BANK = Satz("Bankdrücken", 80.0, 8)
KNIE = Satz("Kniebeugen", 100.0, 5)


def test_mutierend_veraendert_das_original():
    original = TrainingVeraenderbar(date(2026, 11, 2), [BANK, KNIE])
    gefiltert = nur_uebung_mutierend(original, "Bankdrücken")

    assert gefiltert is original          # gleiches Objekt, keine Kopie
    assert original.saetze == [BANK]      # Kniebeugen sind im Original weg


def test_immutable_laesst_original_unveraendert():
    original = Training(date(2026, 11, 2), (BANK, KNIE))
    gefiltert = nur_uebung(original, "bankdrücken")

    assert gefiltert.saetze == (BANK,)
    assert original.saetze == (BANK, KNIE)  # Original unverändert
    assert gefiltert is not original        # neues Objekt


def test_folgefehler_in_der_bestenliste():
    """Nach dem Statistik-Filter fehlt die Übung plötzlich in der Bestenliste."""
    trainings = [TrainingVeraenderbar(date(2026, 11, 2), [BANK, KNIE])]
    nur_uebung_mutierend(trainings[0], "Bankdrücken")

    assert [b.uebung for b in bestenliste(trainings)] == ["Bankdrücken"]


def test_frozen_verhindert_mutation():
    training = Training(date(2026, 11, 2), (BANK, KNIE))
    with pytest.raises(FrozenInstanceError):
        training.saetze = (BANK,)
    with pytest.raises(AttributeError):
        training.saetze.append(BANK)        # tuple hat kein append
