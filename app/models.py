from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Satz:
    uebung: str
    gewicht: float
    wiederholungen: int


@dataclass(frozen=True)
class Training:
    datum: date
    saetze: tuple[Satz, ...]
