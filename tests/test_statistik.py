from datetime import date

from app.models import Satz, Training
from app.services.statistik import (balken_prozent, kalenderwoche,
                                    wochen_statistik)


def test_wochen_neueste_zuerst(beispiel_trainings):
    wochen = wochen_statistik(beispiel_trainings)
    # 26.10. + 29.10.2026 = KW 44, 02.11.2026 = KW 45
    assert [(w.jahr, w.kw) for w in wochen] == [(2026, 45), (2026, 44)]
    kw44 = wochen[1]
    assert kw44.volumen == 1140.0 + 495.0
    assert kw44.anzahl_trainings == 2
    assert kw44.durchschnitt == (1140.0 + 495.0) / 2


def test_filter_auf_uebung_zaehlt_nur_deren_saetze(beispiel_trainings):
    wochen = wochen_statistik(beispiel_trainings, "kreuzheben")
    assert len(wochen) == 1 and wochen[0].volumen == 420.0 and wochen[0].anzahl_trainings == 1


def test_unbekannte_uebung_und_leere_liste():
    assert wochen_statistik((), None) == ()
    assert wochen_statistik((Training(date(2026, 1, 5), (Satz("A", 1.0, 1),)),), "B") == ()


def test_jahreswechsel_iso_woche():
    t = Training(date(2024, 12, 30), ())
    assert kalenderwoche(t) == (2025, 1)


def test_training_ohne_saetze_hat_volumen_null():
    w = wochen_statistik((Training(date(2026, 1, 5), ()),))
    assert w[0].volumen == 0.0


def test_balken_prozent():
    assert balken_prozent(50, 200) == 25.0
    assert balken_prozent(10, 0) == 0.0


def test_original_bleibt_unveraendert(beispiel_trainings):
    vorher = tuple(beispiel_trainings)
    wochen_statistik(beispiel_trainings, "Bankdrücken")
    assert beispiel_trainings == vorher
