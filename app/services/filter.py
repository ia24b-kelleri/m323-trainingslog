"""Feature 1: Suche / Filter / Sortierung der Trainings (C2B).

- Funktionen, die Funktionen zurückgeben (nach_uebung, ab_datum, ...)
- Sortierfunktionen in einem Dict gespeichert (SORTIERUNGEN)
- map, filter und reduce je einzeln eingesetzt
"""
import operator
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from functools import reduce
from typing import Any

from app.models import Training
from app.services.volumen import training_volumen

Filter = Callable[[Training], bool]


# ---------- Filter-Fabriken (Funktion gibt Funktion zurück) ----------

def nach_uebung(name: str) -> Filter:
    gesucht = name.strip().lower()

    def passt(training: Training) -> bool:
        return any(satz.uebung.lower() == gesucht for satz in training.saetze)
    return passt


def ab_datum(von: date) -> Filter:
    def passt(training: Training) -> bool:
        return training.datum >= von
    return passt


def bis_datum(bis: date) -> Filter:
    def passt(training: Training) -> bool:
        return training.datum <= bis
    return passt


def alle(*kriterien: Filter) -> Filter:
    """Kombiniert beliebig viele Filter zu einem (UND). Ohne Filter: alles passt."""
    def passt(training: Training) -> bool:
        return all(k(training) for k in kriterien)
    return passt


# ---------- Sortierungen als Werte in einem Dict ----------

@dataclass(frozen=True)
class Sortierung:
    bezeichnung: str
    schluessel: Callable[[Training], Any]
    absteigend: bool


def anzahl_saetze(training: Training) -> int:
    return len(training.saetze)


SORTIERUNGEN: dict[str, Sortierung] = {
    "datum": Sortierung("Datum (neueste zuerst)", lambda t: (t.datum, t.id or 0), True),
    "datum_alt": Sortierung("Datum (älteste zuerst)", lambda t: (t.datum, t.id or 0), False),
    "volumen": Sortierung("Volumen (höchstes zuerst)", training_volumen, True),
    "saetze": Sortierung("Anzahl Sätze", anzahl_saetze, True),
}
STANDARD_SORTIERUNG = "datum"


# ---------- Suchparameter aus der URL ----------

@dataclass(frozen=True)
class Suchparameter:
    uebung: str = ""
    von: date | None = None
    bis: date | None = None
    sort: str = STANDARD_SORTIERUNG


def _datum_oder_none(text: str) -> date | None:
    try:
        return date.fromisoformat(text.strip()) if text and text.strip() else None
    except ValueError:
        return None


def parse_suchparameter(args: Mapping[str, str]) -> Suchparameter:
    sort = args.get("sort", STANDARD_SORTIERUNG)
    return Suchparameter(
        uebung=args.get("uebung", "").strip(),
        von=_datum_oder_none(args.get("von", "")),
        bis=_datum_oder_none(args.get("bis", "")),
        sort=sort if sort in SORTIERUNGEN else STANDARD_SORTIERUNG,
    )


def baue_filter(p: Suchparameter) -> Filter:
    kriterien = ((nach_uebung(p.uebung) if p.uebung else None),
                 (ab_datum(p.von) if p.von else None),
                 (bis_datum(p.bis) if p.bis else None))
    return alle(*(k for k in kriterien if k is not None))


# ---------- map / filter / reduce einzeln ----------

def filtere(trainings: Iterable[Training], kriterium: Filter) -> tuple[Training, ...]:
    return tuple(filter(kriterium, trainings))                     # filter


def volumina(trainings: Iterable[Training]) -> tuple[float, ...]:
    return tuple(map(training_volumen, trainings))                 # map


def gesamtvolumen(werte: Iterable[float]) -> float:
    return reduce(operator.add, werte, 0.0)                        # reduce


def sortiere(trainings: Iterable[Training], sort: str) -> tuple[Training, ...]:
    s = SORTIERUNGEN[sort]
    return tuple(sorted(trainings, key=s.schluessel, reverse=s.absteigend))


# ---------- Komposition ----------

@dataclass(frozen=True)
class SuchErgebnis:
    trainings: tuple[Training, ...]
    volumina: tuple[float, ...]
    gesamtvolumen: float


def suche(trainings: Iterable[Training], p: Suchparameter) -> SuchErgebnis:
    treffer = sortiere(filtere(trainings, baue_filter(p)), p.sort)
    vol = volumina(treffer)
    return SuchErgebnis(treffer, vol, gesamtvolumen(vol))


def alle_uebungen(trainings: Iterable[Training]) -> tuple[str, ...]:
    return tuple(sorted({s.uebung for t in trainings for s in t.saetze}, key=str.lower))
