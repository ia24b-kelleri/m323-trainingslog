"""Unveränderliche Datentypen (frozen dataclasses) des Trainingslogs."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Satz:
    uebung: str
    gewicht: float          # kg
    wiederholungen: int


@dataclass(frozen=True)
class Training:
    datum: date
    saetze: tuple[Satz, ...]
    id: int | None = None


@dataclass(frozen=True)
class WochenStatistik:
    jahr: int
    kw: int
    volumen: float
    anzahl_trainings: int
    durchschnitt: float


@dataclass(frozen=True)
class Bestleistung:
    uebung: str
    geschaetztes_1rm: float
    gewicht: float
    wiederholungen: int
    datum: date
