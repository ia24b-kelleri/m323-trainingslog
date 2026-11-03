import sqlite3
from datetime import date
from pathlib import Path

from app.models import Satz, Training

_SCHEMA = """
CREATE TABLE IF NOT EXISTS training (
    id    INTEGER PRIMARY KEY,
    datum TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS satz (
    id           INTEGER PRIMARY KEY,
    training_id  INTEGER REFERENCES training(id),
    uebung       TEXT NOT NULL,
    gewicht      REAL NOT NULL,
    wiederholungen INTEGER NOT NULL
);
"""


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(_SCHEMA)


def speichere_training(db_path: str, training: Training) -> int:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO training (datum) VALUES (?)",
            (training.datum.isoformat(),),
        )
        training_id = cursor.lastrowid
        for satz in training.saetze:
            conn.execute(
                "INSERT INTO satz (training_id, uebung, gewicht, wiederholungen) VALUES (?, ?, ?, ?)",
                (training_id, satz.uebung, satz.gewicht, satz.wiederholungen),
            )
        return training_id


def lade_trainings(db_path: str) -> tuple[Training, ...]:
    with sqlite3.connect(db_path) as conn:
        trainings_rows = conn.execute(
            "SELECT id, datum FROM training ORDER BY datum"
        ).fetchall()
        satz_rows = conn.execute(
            "SELECT training_id, uebung, gewicht, wiederholungen FROM satz"
        ).fetchall()

    saetze_pro_training: dict[int, list[Satz]] = {}
    for training_id, uebung, gewicht, wdh in satz_rows:
        saetze_pro_training.setdefault(training_id, []).append(
            Satz(uebung=uebung, gewicht=gewicht, wiederholungen=wdh)
        )

    result = []
    for training_id, datum_str in trainings_rows:
        saetze = tuple(saetze_pro_training.get(training_id, []))
        result.append(Training(datum=date.fromisoformat(datum_str), saetze=saetze))

    return tuple(result)
