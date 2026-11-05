"""Feature 2: Wochenstatistik (C2I) – umgesetzt gemäss docs/design-statistik.md.

Datenfluss:
  Trainings -> [map] nur Sätze der gewählten Übung -> [filter] Trainings mit Sätzen
            -> nach (jahr, kw) gruppieren -> [reduce] Volumen summieren
            -> WochenStatistik -> neueste Woche zuerst
"""
from collections.abc import Iterable
from dataclasses import replace
from functools import reduce
from itertools import groupby

from app.models import Training, WochenStatistik
from app.services.volumen import training_volumen

Woche = tuple[int, int]  # (ISO-Jahr, ISO-Kalenderwoche)


def kalenderwoche(training: Training) -> Woche:
    """ISO-Woche: 30.12.2024 gehört zu KW 1/2025, darum (jahr, kw) als Schlüssel."""
    iso = training.datum.isocalendar()
    return iso.year, iso.week


def nur_uebung(training: Training, uebung: str) -> Training:
    """Neues Training mit nur den Sätzen einer Übung (Original bleibt unverändert)."""
    gesucht = uebung.strip().lower()
    return replace(training, saetze=tuple(s for s in training.saetze
                                          if s.uebung.lower() == gesucht))


def auswahl(trainings: Iterable[Training], uebung: str | None) -> tuple[Training, ...]:
    if not uebung:
        return tuple(trainings)
    # verkettet: map -> filter
    return tuple(filter(lambda t: len(t.saetze) > 0,
                        map(lambda t: nur_uebung(t, uebung), trainings)))


def baue_woche(woche: Woche, trainings: tuple[Training, ...]) -> WochenStatistik:
    volumen = reduce(lambda summe, t: summe + training_volumen(t), trainings, 0.0)  # reduce
    anzahl = len(trainings)
    return WochenStatistik(jahr=woche[0], kw=woche[1], volumen=volumen,
                           anzahl_trainings=anzahl,
                           durchschnitt=volumen / anzahl if anzahl else 0.0)


def wochen_statistik(trainings: Iterable[Training],
                     uebung: str | None = None) -> tuple[WochenStatistik, ...]:
    nach_woche = sorted(auswahl(trainings, uebung), key=kalenderwoche)
    wochen = (baue_woche(woche, tuple(gruppe))
              for woche, gruppe in groupby(nach_woche, key=kalenderwoche))
    return tuple(sorted(wochen, key=lambda w: (w.jahr, w.kw), reverse=True))


def balken_prozent(wert: float, maximum: float) -> float:
    return round(wert / maximum * 100, 1) if maximum > 0 else 0.0


def max_volumen(wochen: Iterable[WochenStatistik]) -> float:
    return max(map(lambda w: w.volumen, wochen), default=0.0)
