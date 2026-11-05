"""CSV-Import (Algorithmus für C1): in Teilfunktionen zerlegt und komponiert.

Format:   datum,uebung,gewicht,wiederholungen
Beispiel: 2026-11-02,Bankdrücken,82.5,8

Ablauf von importiere_csv:
  Text -> Zeilen -> Kopfzeile prüfen -> parse_zeile -> validiere_zeile
       -> (gültig) normalisiere_zeile -> gruppiere_zu_trainings
       -> (ungültig) ImportFehler mit Zeilennummer
"""
import csv
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from itertools import groupby

from app.models import Satz, Training
from app.services.parsing import (parse_datum, parse_gewicht, parse_uebung,
                                  parse_wiederholungen)

KOPFZEILE = ("datum", "uebung", "gewicht", "wiederholungen")

Felder = tuple[str, ...]
Eintrag = tuple[date, Satz]


@dataclass(frozen=True)
class ImportFehler:
    zeile: int
    grund: str


@dataclass(frozen=True)
class ImportErgebnis:
    trainings: tuple[Training, ...]
    fehler: tuple[ImportFehler, ...]

    @property
    def anzahl_saetze(self) -> int:
        return sum(len(t.saetze) for t in self.trainings)


# ---------- Teilfunktionen ----------

def erkenne_trennzeichen(kopfzeile: str) -> str:
    """Excel (CH) exportiert oft mit Semikolon."""
    return ";" if ";" in kopfzeile else ","


def parse_zeile(zeile: str, trennzeichen: str = ",") -> Felder:
    """Zerlegt eine Zeile in Felder.

    Sonderfall Dezimal-Komma bei Trennzeichen ',':
    '2026-01-05,Bankdrücken,82,5,8' ergibt 5 Felder -> Feld 3+4 = '82,5'.
    """
    felder = tuple(f.strip() for f in next(csv.reader([zeile], delimiter=trennzeichen)))
    if trennzeichen == "," and len(felder) == 5:
        return (felder[0], felder[1], f"{felder[2]},{felder[3]}", felder[4])
    return felder


def validiere_zeile(felder: Felder) -> str | None:
    """None = gültig, sonst Fehlergrund."""
    if len(felder) != 4:
        return f"erwartet 4 Felder, gefunden {len(felder)}"
    datum, uebung, gewicht, wdh = felder
    for parser, wert in ((parse_datum, datum), (parse_uebung, uebung),
                         (parse_gewicht, gewicht), (parse_wiederholungen, wdh)):
        try:
            parser(wert)
        except ValueError as fehler:
            return str(fehler)
    return None


def normalisiere_zeile(felder: Felder) -> Eintrag:
    """Wandelt eine GÜLTIGE Zeile in (datum, Satz) um."""
    datum, uebung, gewicht, wdh = felder
    return parse_datum(datum), Satz(parse_uebung(uebung), parse_gewicht(gewicht),
                                    parse_wiederholungen(wdh))


def gruppiere_zu_trainings(eintraege: Iterable[Eintrag]) -> tuple[Training, ...]:
    """Alle Sätze mit gleichem Datum werden zu einem Training (Reihenfolge bleibt)."""
    sortiert = sorted(eintraege, key=lambda e: e[0])   # sorted ist stabil
    return tuple(Training(datum, tuple(satz for _, satz in gruppe))
                 for datum, gruppe in groupby(sortiert, key=lambda e: e[0]))


def ist_kopfzeile(felder: Felder) -> bool:
    return tuple(f.lower() for f in felder) == KOPFZEILE


# ---------- Komposition ----------

def importiere_csv(text: str) -> ImportErgebnis:
    zeilen = tuple(enumerate(text.lstrip("\ufeff").splitlines(), start=1))
    nicht_leer = tuple((nr, z) for nr, z in zeilen if z.strip())

    if not nicht_leer:
        return ImportErgebnis((), (ImportFehler(0, "Datei ist leer"),))

    kopf_nr, kopf = nicht_leer[0]
    trennzeichen = erkenne_trennzeichen(kopf)
    if not ist_kopfzeile(parse_zeile(kopf, trennzeichen)):
        return ImportErgebnis((), (ImportFehler(
            kopf_nr, "Kopfzeile fehlt oder ist falsch (erwartet: " + ",".join(KOPFZEILE) + ")"),))

    geparst = tuple((nr, parse_zeile(z, trennzeichen)) for nr, z in nicht_leer[1:])
    geprueft = tuple((nr, felder, validiere_zeile(felder)) for nr, felder in geparst)

    fehler = tuple(ImportFehler(nr, grund) for nr, _, grund in geprueft if grund)
    gueltig = (normalisiere_zeile(felder) for _, felder, grund in geprueft if not grund)

    return ImportErgebnis(gruppiere_zu_trainings(gueltig), fehler)
