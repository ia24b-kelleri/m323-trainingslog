"""Datenbank-Zugriff (SQLite). Alle Funktionen bekommen den Pfad als Parameter.

Hinweis: Das sind bewusst *Prozeduren* mit Seiteneffekten (Datei/DB).
Die Business-Logik liegt als pure functions in app/services/.
"""
import sqlite3
from contextlib import closing
from datetime import date
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

    STAND VORHER (für D1): imperatives Gruppieren mit setdefault + append
    in einer for-Schleife, danach Liste mutieren (sort).
    """
    with closing(sqlite3.connect(db_path)) as con:
        training_rows = con.execute("SELECT id, datum FROM training").fetchall()
        satz_rows = con.execute(
            "SELECT training_id, uebung, gewicht, wiederholungen FROM satz ORDER BY id"
        ).fetchall()

    saetze_pro_training = {}
    for training_id, uebung, gewicht, wiederholungen in satz_rows:
        saetze_pro_training.setdefault(training_id, []).append(
            Satz(uebung, gewicht, wiederholungen))

    trainings = []
    for training_id, datum in training_rows:
        saetze = tuple(saetze_pro_training.get(training_id, []))
        trainings.append(Training(date.fromisoformat(datum), saetze, training_id))

    trainings.sort(key=lambda t: (t.datum, t.id))
    return tuple(trainings)
