"""Kleine Parser für Benutzereingaben. Werfen ValueError mit deutscher Meldung.

Werden vom Formular (erfassen.py) UND vom CSV-Import (csv_import.py) verwendet.
"""
from datetime import date


def parse_datum(text: str) -> date:
    try:
        return date.fromisoformat(text.strip())
    except ValueError:
        raise ValueError(f"ungültiges Datum «{text.strip()}» (erwartet JJJJ-MM-TT)") from None


def parse_gewicht(text: str) -> float:
    """Akzeptiert Punkt und Komma als Dezimaltrennzeichen: '82.5' und '82,5'."""
    try:
        wert = float(text.strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"Gewicht «{text.strip()}» ist keine Zahl") from None
    if wert < 0:
        raise ValueError("Gewicht darf nicht negativ sein")
    return wert


def parse_wiederholungen(text: str) -> int:
    try:
        wert = int(text.strip())
    except ValueError:
        raise ValueError(f"Wiederholungen «{text.strip()}» sind keine ganze Zahl") from None
    if wert < 1:
        raise ValueError("Wiederholungen müssen mindestens 1 sein")
    return wert


def parse_uebung(text: str) -> str:
    name = " ".join(text.split())
    if not name:
        raise ValueError("Übung fehlt")
    return name
