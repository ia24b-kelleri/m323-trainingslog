from datetime import date

from app.services.filter import (SORTIERUNGEN, Suchparameter, ab_datum, alle,
                                 bis_datum, gesamtvolumen, nach_uebung,
                                 parse_suchparameter, suche, volumina)


def test_filter_fabrik_liefert_funktion(beispiel_trainings):
    ist_kreuzheben = nach_uebung("kreuzheben")          # Funktion in Variable
    assert callable(ist_kreuzheben)
    assert [t.id for t in beispiel_trainings if ist_kreuzheben(t)] == [3]


def test_alle_kombiniert_filter(beispiel_trainings):
    zeitraum = alle(ab_datum(date(2026, 10, 27)), bis_datum(date(2026, 10, 31)))
    assert [t.id for t in filter(zeitraum, beispiel_trainings)] == [2]


def test_map_und_reduce(beispiel_trainings):
    vol = volumina(beispiel_trainings)
    assert vol == (1140.0, 495.0, 845.0)
    assert gesamtvolumen(vol) == 2480.0
    assert gesamtvolumen(()) == 0.0


def test_sortierungen_sind_im_dict_gespeichert():
    assert set(SORTIERUNGEN) == {"datum", "datum_alt", "volumen", "saetze"}
    assert callable(SORTIERUNGEN["volumen"].schluessel)


def test_suche_komplett(beispiel_trainings):
    p = Suchparameter(uebung="Bankdrücken", sort="volumen")
    erg = suche(beispiel_trainings, p)
    assert [t.id for t in erg.trainings] == [1, 3, 2]
    assert erg.gesamtvolumen == 2480.0


def test_ungueltige_parameter_werden_ignoriert():
    p = parse_suchparameter({"von": "gestern", "sort": "quatsch", "uebung": "  "})
    assert p == Suchparameter()


def test_eingabe_bleibt_unveraendert(beispiel_trainings):
    kopie = tuple(beispiel_trainings)
    suche(beispiel_trainings, Suchparameter(sort="volumen"))
    assert beispiel_trainings == kopie
