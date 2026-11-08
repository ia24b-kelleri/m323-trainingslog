"""A1I: Mutation vs. immutable – dieselbe Aufgabe zweimal gelöst.

Aufgabe: Ein Training soll nur noch die Sätze einer Übung enthalten
(gebraucht vom Übungsfilter der Statistik-Seite).

- Immutable Variante: app/services/statistik.py -> nur_uebung (wird in der App verwendet)
- Mutierende Variante: hier, NUR zum Vergleich. Wird in der App bewusst nicht verwendet.
"""
from dataclasses import dataclass
from datetime import date

from app.models import Satz


@dataclass  # NICHT frozen -> Felder können verändert werden
class TrainingVeraenderbar:
    datum: date
    saetze: list[Satz]


def nur_uebung_mutierend(training: TrainingVeraenderbar, uebung: str) -> TrainingVeraenderbar:
    """Filtert die Sätze IN PLACE: das übergebene Training wird verändert."""
    gesucht = uebung.strip().lower()
    training.saetze[:] = [s for s in training.saetze if s.uebung.lower() == gesucht]
    return training
