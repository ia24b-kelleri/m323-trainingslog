"""Formular 'Training erfassen' -> Training oder Fehlerliste (pure)."""
from collections.abc import Mapping

from app.models import Satz, Training
from app.services.parsing import (parse_datum, parse_gewicht, parse_uebung,
                                  parse_wiederholungen)

ANZAHL_ZEILEN = 5

Zeile = tuple[str, str, str]  # (uebung, gewicht, wiederholungen) als Rohtext


def lies_zeile(daten: Mapping[str, str], index: int) -> Zeile:
    return (daten.get(f"uebung_{index}", ""),
            daten.get(f"gewicht_{index}", ""),
            daten.get(f"wdh_{index}", ""))


def ist_leer(zeile: Zeile) -> bool:
    return all(not feld.strip() for feld in zeile)


def pruefe_zeile(nummer: int, zeile: Zeile) -> Satz | str:
    """Gibt einen Satz zurück oder eine Fehlermeldung (str)."""
    uebung, gewicht, wdh = zeile
    try:
        return Satz(parse_uebung(uebung), parse_gewicht(gewicht), parse_wiederholungen(wdh))
    except ValueError as fehler:
        return f"Satz {nummer}: {fehler}"


def parse_formular(daten: Mapping[str, str],
                   anzahl_zeilen: int = ANZAHL_ZEILEN) -> tuple[Training | None, tuple[str, ...]]:
    zeilen = tuple(lies_zeile(daten, i) for i in range(anzahl_zeilen))
    resultate = tuple(pruefe_zeile(nr, z)
                      for nr, z in enumerate(zeilen, start=1) if not ist_leer(z))

    fehler = tuple(r for r in resultate if isinstance(r, str))
    saetze = tuple(r for r in resultate if isinstance(r, Satz))

    try:
        datum = parse_datum(daten.get("datum", ""))
    except ValueError as e:
        fehler = (f"Datum: {e}",) + fehler

    if not resultate:
        fehler = fehler + ("Mindestens ein Satz muss ausgefüllt sein",)

    if fehler:
        return None, fehler
    return Training(datum, saetze), ()
