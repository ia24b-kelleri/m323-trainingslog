from datetime import date

from app.models import Satz
from app.services.csv_import import (ImportFehler, gruppiere_zu_trainings,
                                     importiere_csv, normalisiere_zeile,
                                     parse_zeile, validiere_zeile)

KOPF = "datum,uebung,gewicht,wiederholungen\n"


# ---------- Teilfunktionen ----------

def test_parse_zeile_normal():
    assert parse_zeile("2026-11-02, Bankdrücken ,80,8") == ("2026-11-02", "Bankdrücken", "80", "8")


def test_parse_zeile_dezimalkomma():
    assert parse_zeile("2026-11-02,Bankdrücken,82,5,8") == ("2026-11-02", "Bankdrücken", "82,5", "8")


def test_validiere_zeile():
    assert validiere_zeile(("2026-11-02", "Bankdrücken", "80", "8")) is None
    assert "Datum" in validiere_zeile(("2026-13-40", "Bankdrücken", "80", "8"))
    assert "4 Felder" in validiere_zeile(("2026-11-02", "Bankdrücken"))


def test_normalisiere_zeile():
    assert normalisiere_zeile(("2026-11-02", "Bankdrücken", "82,5", "8")) == \
        (date(2026, 11, 2), Satz("Bankdrücken", 82.5, 8))


def test_gruppiere_gleiches_datum_zu_einem_training():
    a, b, c = Satz("A", 1.0, 1), Satz("B", 2.0, 2), Satz("C", 3.0, 3)
    trainings = gruppiere_zu_trainings([(date(2026, 1, 2), a), (date(2026, 1, 1), b),
                                        (date(2026, 1, 2), c)])
    assert [(t.datum.day, t.saetze) for t in trainings] == [(1, (b,)), (2, (a, c))]


# ---------- Komposition + Edge Cases ----------

def test_import_gueltig():
    erg = importiere_csv(KOPF + "2026-11-02,Bankdrücken,80,8\n2026-11-02,Rudern,60,10\n")
    assert erg.fehler == ()
    assert len(erg.trainings) == 1 and erg.anzahl_saetze == 2


def test_leere_datei():
    erg = importiere_csv("")
    assert erg.trainings == () and erg.fehler == (ImportFehler(0, "Datei ist leer"),)


def test_nur_kopfzeile():
    erg = importiere_csv(KOPF)
    assert erg.trainings == () and erg.fehler == ()


def test_falsche_kopfzeile():
    erg = importiere_csv("a,b,c\n2026-11-02,Bankdrücken,80,8\n")
    assert erg.trainings == () and erg.fehler[0].zeile == 1


def test_ungueltiges_datum_und_negatives_gewicht_brechen_nicht_ab():
    text = KOPF + "2026-02-30,Bankdrücken,80,8\n2026-11-02,Bankdrücken,-5,8\n2026-11-03,Rudern,60,10\n"
    erg = importiere_csv(text)
    assert [f.zeile for f in erg.fehler] == [2, 3]
    assert "negativ" in erg.fehler[1].grund
    assert erg.anzahl_saetze == 1


def test_dezimalkomma_und_semikolon():
    erg1 = importiere_csv(KOPF + "2026-11-02,Bankdrücken,82,5,8\n")
    erg2 = importiere_csv("datum;uebung;gewicht;wiederholungen\n2026-11-02;Bankdrücken;82,5;8\n")
    assert erg1.trainings[0].saetze == erg2.trainings[0].saetze == (Satz("Bankdrücken", 82.5, 8),)


def test_bom_und_leerzeilen_werden_toleriert():
    erg = importiere_csv("\ufeff" + KOPF + "\n2026-11-02,Bankdrücken,80,8\n\n")
    assert erg.fehler == () and erg.anzahl_saetze == 1
