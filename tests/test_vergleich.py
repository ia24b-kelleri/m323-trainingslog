from app.services.vergleich import (schwerste_gewichte_funktional,
                                    schwerste_gewichte_oo,
                                    schwerste_gewichte_prozedural)


def test_alle_drei_paradigmen_liefern_dasselbe(beispiel_trainings):
    erwartet = {"Bankdrücken": 85.0, "Kniebeugen": 100.0, "Kreuzheben": 140.0}
    assert schwerste_gewichte_oo(beispiel_trainings) == erwartet
    assert schwerste_gewichte_prozedural(beispiel_trainings) == erwartet
    assert schwerste_gewichte_funktional(beispiel_trainings) == erwartet


def test_leer():
    assert schwerste_gewichte_oo(()) == schwerste_gewichte_prozedural(()) \
        == schwerste_gewichte_funktional(()) == {}
