"""Paradigmenvergleich (A1A): "schwerstes Gewicht pro Übung" dreimal gelöst.

Alle drei liefern dasselbe Ergebnis (siehe tests/test_vergleich.py).
Die funktionale Variante wird auf der Bestenliste-Seite verwendet.
"""
from collections.abc import Iterable
from functools import reduce

from app.models import Satz, Training


# ---------- 1) Objektorientiert: Zustand im Objekt ----------

class SchwersteGewichteRechner:
    def __init__(self) -> None:
        self._maxima: dict[str, float] = {}

    def verarbeite(self, training: Training) -> None:
        for satz in training.saetze:
            if satz.gewicht > self._maxima.get(satz.uebung, float("-inf")):
                self._maxima[satz.uebung] = satz.gewicht

    def ergebnis(self) -> dict[str, float]:
        return dict(sorted(self._maxima.items()))


def schwerste_gewichte_oo(trainings: Iterable[Training]) -> dict[str, float]:
    rechner = SchwersteGewichteRechner()
    for training in trainings:
        rechner.verarbeite(training)
    return rechner.ergebnis()


# ---------- 2) Prozedural: Schleife + veränderliches Dict ----------

def schwerste_gewichte_prozedural(trainings: Iterable[Training]) -> dict[str, float]:
    maxima = {}
    for training in trainings:
        for satz in training.saetze:
            if satz.uebung not in maxima or satz.gewicht > maxima[satz.uebung]:
                maxima[satz.uebung] = satz.gewicht
    return dict(sorted(maxima.items()))


# ---------- 3) Funktional: reduce, ohne Mutation ----------

def _uebernimm_maximum(maxima: dict[str, float], satz: Satz) -> dict[str, float]:
    bisher = maxima.get(satz.uebung, satz.gewicht)
    return {**maxima, satz.uebung: max(bisher, satz.gewicht)}   # neues Dict


def schwerste_gewichte_funktional(trainings: Iterable[Training]) -> dict[str, float]:
    alle_saetze = (satz for training in trainings for satz in training.saetze)
    return dict(sorted(reduce(_uebernimm_maximum, alle_saetze, {}).items()))
