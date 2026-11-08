"""Datenbank-Zugriff (SQLite). Alle Funktionen bekommen den Pfad als Parameter.

Hinweis: Das sind bewusst *Prozeduren* mit Seiteneffekten (Datei/DB).
Die Business-Logik liegt als pure functions in app/services/.
"""
import sqlite3
from contextlib import closing
from datetime import date
from itertools import groupby
from operator import itemgetter
from pathlib import Path

from app.models import Satz, Training

SCHEMA = """
CREATE TABLE IF NOT EXISTS training (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    datum TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS satz (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    training_id    INTEGER NOT NULL REFERENCES training(id) ON DELETE CASCADE,
    uebung         TEXT    NOT NULL,
    gewicht        REAL    NOT NULL,
    wiederholungen INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_satz_training ON satz(training_id, id);
"""


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as con:
        con.executescript(SCHEMA)


def _insert(con: sqlite3.Connection, training: Training) -> int:
    cur = con.execute("INSERT INTO training (datum) VALUES (?)",
                      (training.datum.isoformat(),))
    training_id = cur.lastrowid
    con.executemany(
        "INSERT INTO satz (training_id, uebung, gewicht, wiederholungen) VALUES (?, ?, ?, ?)",
        [(training_id, s.uebung, s.gewicht, s.wiederholungen) for s in training.saetze],
    )
    return training_id


def speichere_training(db_path: str, training: Training) -> int:
    """Speichert ein Training inkl. Sätze in einer Transaktion, gibt die neue id zurück."""
    with closing(sqlite3.connect(db_path)) as con, con:
        return _insert(con, training)


def speichere_trainings(db_path: str, trainings: tuple[Training, ...]) -> tuple[int, ...]:
    """Mehrere Trainings in EINER Transaktion speichern (Import, Seed)."""
    with closing(sqlite3.connect(db_path)) as con, con:
        return tuple(_insert(con, t) for t in trainings)


def loesche_alle(db_path: str) -> None:
    with closing(sqlite3.connect(db_path)) as con, con:
        con.execute("DELETE FROM satz")
        con.execute("DELETE FROM training")


def lade_trainings(db_path: str) -> tuple[Training, ...]:
    """Lädt alle Trainings, aufsteigend nach Datum sortiert.

    STAND NACHHER (D1): deklarativ. Die DB sortiert die Sätze nach training_id,
    groupby fasst sie zusammen, eine Dict-Comprehension baut die Zuordnung.
    Keine append/sort-Mutation mehr, der Index beschleunigt ORDER BY training_id.
    """
    with closing(sqlite3.connect(db_path)) as con:
        training_rows = con.execute(
            "SELECT id, datum FROM training ORDER BY datum, id").fetchall()
        satz_rows = con.execute(
            "SELECT training_id, uebung, gewicht, wiederholungen FROM satz "
            "ORDER BY training_id, id").fetchall()

    saetze_pro_training = {
        training_id: tuple(Satz(uebung, gewicht, wdh) for _, uebung, gewicht, wdh in gruppe)
        for training_id, gruppe in groupby(satz_rows, key=itemgetter(0))
    }
    return tuple(Training(date.fromisoformat(datum), saetze_pro_training.get(tid, ()), tid)
                 for tid, datum in training_rows)
