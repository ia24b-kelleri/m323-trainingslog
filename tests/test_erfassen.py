from datetime import date

from app.models import Satz, Training
from app.services.erfassen import parse_formular


def test_gueltiges_formular_leere_zeilen_ignoriert():
    form = {"datum": "2026-11-02", "uebung_0": "Bankdrücken", "gewicht_0": "82,5", "wdh_0": "8",
            "uebung_3": " Rudern ", "gewicht_3": "60", "wdh_3": "10"}
    training, fehler = parse_formular(form)
    assert fehler == ()
    assert training == Training(date(2026, 11, 2),
                                (Satz("Bankdrücken", 82.5, 8), Satz("Rudern", 60.0, 10)))


def test_halb_ausgefuellte_zeile_gibt_fehler_mit_nummer():
    form = {"datum": "2026-11-02", "uebung_1": "Bankdrücken", "gewicht_1": "", "wdh_1": "8"}
    training, fehler = parse_formular(form)
    assert training is None
    assert fehler[0].startswith("Satz 2:")


def test_ohne_saetze_und_ohne_datum():
    training, fehler = parse_formular({})
    assert training is None
    assert len(fehler) == 2


def test_negatives_gewicht_wird_abgelehnt():
    form = {"datum": "2026-11-02", "uebung_0": "Dips", "gewicht_0": "-5", "wdh_0": "8"}
    _, fehler = parse_formular(form)
    assert "negativ" in fehler[0]
