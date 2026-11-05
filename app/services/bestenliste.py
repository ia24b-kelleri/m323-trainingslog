"""Feature 3: Bestenliste (C2A) – Aggregation + benutzerdefinierte Sortierung.

Geschätztes 1RM nach Epley: gewicht * (1 + wiederholungen / 30)

STAND VORHER (für D1): Die Suche ist bewusst NAIV:
- alle_uebungen sucht linear in einer Liste ("in" auf list)
- bester_satz läuft für JEDE Übung erneut über ALLE Sätze aller Trainings
  -> Aufwand O(Übungen × Sätze)
"""
from collections.abc import Sequence

from app.models import Bestleistung, Satz, Training


def geschaetztes_1rm(satz: Satz) -> float:
    return satz.gewicht * (1 + satz.wiederholungen / 30)


def rang_schluessel(b: Bestleistung) -> tuple[float, str]:
    """Benannte Sortierfunktion: 1RM absteigend, bei Gleichstand Übung alphabetisch."""
    return -b.geschaetztes_1rm, b.uebung.lower()


def alle_uebungen(trainings: Sequence[Training]) -> list[str]:
    uebungen = []
    for training in trainings:
        for satz in training.saetze:
            if satz.uebung not in uebungen:          # lineare Suche in Liste
                uebungen.append(satz.uebung)
    return uebungen


def bester_satz(trainings: Sequence[Training], uebung: str) -> Bestleistung | None:
    bester = None
    for training in trainings:                       # für jede Übung: alles nochmal
        for satz in training.saetze:
            if satz.uebung != uebung:
                continue
            rm = geschaetztes_1rm(satz)
            if bester is None or rm > bester.geschaetztes_1rm:
                bester = Bestleistung(satz.uebung, rm, satz.gewicht,
                                      satz.wiederholungen, training.datum)
    return bester


def bestenliste(trainings: Sequence[Training]) -> tuple[Bestleistung, ...]:
    bestleistungen = [bester_satz(trainings, u) for u in alle_uebungen(trainings)]
    return tuple(sorted(bestleistungen, key=rang_schluessel))
