"""Grundbausteine: Volumen = Gewicht × Wiederholungen."""
from app.models import Satz, Training


def satz_volumen(satz: Satz) -> float:
    return satz.gewicht * satz.wiederholungen


def training_volumen(training: Training) -> float:
    return sum(map(satz_volumen, training.saetze), 0.0)
