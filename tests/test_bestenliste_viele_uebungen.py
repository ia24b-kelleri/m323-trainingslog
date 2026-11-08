"""Sicherheitsnetz VOR der Optimierung der Bestenliste (D1I).

Läuft gegen die naive UND die optimierte Version -> beweist gleiches Verhalten.
"""
from datetime import date

from app.models import Satz, Training
from app.services.bestenliste import bestenliste
from scripts.seed import erzeuge_trainings


def test_viele_uebungen_mit_gleichstaenden():
    # 3 Übungen mit exakt gleichem 1RM + späterer gleich guter Satz (erster muss gewinnen)
    trainings = (
        Training(date(2026, 1, 1), (Satz("Rudern", 90.0, 3), Satz("bankdrücken", 90.0, 3),
                                    Satz("Dips", 90.0, 3), Satz("Curls", 20.0, 10))),
        Training(date(2026, 1, 3), (Satz("Rudern", 90.0, 3), Satz("Curls", 25.0, 8))),
    )
    liste = bestenliste(trainings)
    assert [b.uebung for b in liste] == ["bankdrücken", "Dips", "Rudern", "Curls"]
    assert liste[2].datum == date(2026, 1, 1)
    assert (liste[3].gewicht, liste[3].wiederholungen) == (25.0, 8)


def test_seed_daten_snapshot():
    """Grosser Datensatz: Ergebnis muss vor und nach dem Refactoring identisch sein."""
    trainings = erzeuge_trainings(300, seed=7, ende=date(2026, 11, 1))
    liste = bestenliste(trainings)
    assert len(liste) == 12
    assert [b.geschaetztes_1rm for b in liste] == sorted((b.geschaetztes_1rm for b in liste), reverse=True)
    # Kontrolle gegen eine einfache, unabhängige Berechnung
    erwartet = {}
    for t in trainings:
        for s in t.saetze:
            rm = s.gewicht * (1 + s.wiederholungen / 30)
            if s.uebung not in erwartet or rm > erwartet[s.uebung][0]:
                erwartet[s.uebung] = (rm, t.datum)
    assert {b.uebung: (b.geschaetztes_1rm, b.datum) for b in liste} == erwartet
