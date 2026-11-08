"""CSV-Export als pure function (B1A / D1: aus der Route extrahiert).

Vorher: for-Schleifen, append und String-Verkettung direkt in der Route.
Nachher: deklarativ beschrieben, WAS exportiert wird; das csv-Modul
kümmert sich um Trennzeichen und Anführungszeichen (z. B. Komma im Übungsnamen).
"""
import csv
import io
from collections.abc import Iterable

from app.models import Training
from app.services.csv_import import KOPFZEILE


def export_zeilen(trainings: Iterable[Training]) -> tuple[tuple, ...]:
    return tuple((t.datum.isoformat(), s.uebung, s.gewicht, s.wiederholungen)
                 for t in trainings for s in t.saetze)


def exportiere_csv(trainings: Iterable[Training]) -> str:
    puffer = io.StringIO()
    writer = csv.writer(puffer, lineterminator="\n")
    writer.writerow(KOPFZEILE)
    writer.writerows(export_zeilen(trainings))
    return puffer.getvalue()
