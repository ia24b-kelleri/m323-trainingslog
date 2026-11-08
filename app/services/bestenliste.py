"""Feature 3: Bestenliste (C2A) – Aggregation + benutzerdefinierte Sortierung.

Geschätztes 1RM nach Epley: gewicht * (1 + wiederholungen / 30)

STAND NACHHER (D1): Ein einziger Durchlauf über alle Sätze, das beste 1RM
pro Übung liegt in einem Dict (Zugriff O(1) statt Listensuche).
Aufwand O(Sätze) statt O(Übungen × Sätze).
Das Dict ist lokal -> die Funktion bleibt nach aussen pure.
"""
from collections.abc import Iterable

from app.models import Bestleistung, Satz, Training


def geschaetztes_1rm(satz: Satz) -> float:
    return satz.gewicht * (1 + satz.wiederholungen / 30)


def rang_schluessel(b: Bestleistung) -> tuple[float, str]:
    """Benannte Sortierfunktion: 1RM absteigend, bei Gleichstand Übung alphabetisch."""
    return -b.geschaetztes_1rm, b.uebung.lower()


def bestenliste(trainings: Iterable[Training]) -> tuple[Bestleistung, ...]:
    beste: dict[str, Bestleistung] = {}
    for training in trainings:
        for satz in training.saetze:
            rm = geschaetztes_1rm(satz)
            aktuell = beste.get(satz.uebung)
            if aktuell is None or rm > aktuell.geschaetztes_1rm:   # ">" -> erster Satz gewinnt
                beste[satz.uebung] = Bestleistung(satz.uebung, rm, satz.gewicht,
                                                  satz.wiederholungen, training.datum)
    return tuple(sorted(beste.values(), key=rang_schluessel))
