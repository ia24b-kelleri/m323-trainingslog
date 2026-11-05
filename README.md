# Trainingslog – Modul 323 (Funktionale Programmierung)

Flask-App zum Erfassen und Auswerten von Krafttrainings. Die Business-Logik ist
als *pure functions* in `app/services/` umgesetzt, Daten sind unveränderlich
(`frozen` dataclasses, `tuple` statt `list`).

## Features

| Route | Feature | Funktionale Konzepte |
|---|---|---|
| `/` | Startseite, letzte 5 Trainings | – |
| `/trainings/neu` | Training erfassen (5 Satz-Zeilen, Validierung) | pure Parser, Fehler als Werte |
| `/trainings` | Suche / Filter / Sortierung | Filter-Fabriken, Funktionen im Dict, map / filter / reduce |
| `/import`, `/export` | CSV-Import und -Export | Algorithmus in Teilfunktionen, Komposition |
| `/statistik` | Volumen pro Kalenderwoche | Lambda, verkettete map → filter → reduce-Pipeline |
| `/bestenliste` | Bestes geschätztes 1RM pro Übung | Aggregation, eigene Sortierfunktion (`key=`) |

## Setup (PyCharm, Windows)

1. Projektordner in PyCharm öffnen (*File → Open*).
2. Interpreter: *Settings → Project → Python Interpreter* → bestehende `.venv` wählen
   oder *Add Interpreter → Virtualenv* neu anlegen (Python 3.10 oder neuer).
3. Im PyCharm-Terminal:

```bash
pip install -r requirements.txt
```

## Starten

```bash
python scripts/seed.py --anzahl 200 --reset   # Testdaten erzeugen (optional)
python run.py
```

Dann <http://127.0.0.1:5000> öffnen. Die Datenbank liegt in `instance/trainingslog.db`
(nicht im Repo, siehe `.gitignore`).

## Tests

```bash
python -m pytest -v
```

In PyCharm alternativ: Rechtsklick auf den Ordner `tests` → *Run 'pytest in tests'*.

## Weitere Skripte

| Befehl | Zweck |
|---|---|
| `python scripts/seed.py --anzahl 500` | Fake-Trainings hinzufügen (`--reset` leert vorher, `--seed` für andere Zufallsdaten) |
| `python scripts/messung.py --ausgabe docs/messung_vorher.txt` | Laufzeit von `lade_trainings` und `bestenliste` mit 500 / 2000 / 5000 Trainings messen |

Zum Testen des Imports: `beispieldaten/import_test.csv` hochladen. Sie enthält gültige
Zeilen, ein Dezimal-Komma und mehrere fehlerhafte Zeilen.

## Projektstruktur

```
app/
  __init__.py        App-Factory (create_app)
  models.py          frozen dataclasses: Satz, Training, WochenStatistik, Bestleistung
  db.py              SQLite-Zugriff (Prozeduren mit Seiteneffekten)
  routes.py          dünne Routes: Request lesen -> Service -> Template
  services/
    volumen.py       satz_volumen, training_volumen
    parsing.py       Parser für Datum, Gewicht, Wiederholungen, Übung
    erfassen.py      Formular -> Training oder Fehlerliste
    filter.py        Suche/Filter/Sortierung (Feature 1)
    csv_import.py    CSV-Import-Algorithmus
    statistik.py     Wochenstatistik (Feature 2)
    bestenliste.py   Bestenliste (Feature 3)
    vergleich.py     gleiche Aufgabe in OO, prozedural, funktional
  templates/         Jinja-Templates (base.html + Seiten)
  static/style.css
scripts/             seed.py, messung.py
tests/               pytest-Tests pro Modul + Routes
docs/                Design-Blatt, Portfolio-Leitfaden, Messungen
```

## CSV-Format

```
datum,uebung,gewicht,wiederholungen
2026-11-02,Bankdrücken,82.5,8
```

Semikolon als Trennzeichen und Dezimal-Komma (`82,5`) werden ebenfalls akzeptiert.
