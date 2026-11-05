"""Performance-Messung für D1A (vorher/nachher).

    python scripts/messung.py --ausgabe docs/messung_vorher.txt
    ... refactoring ...
    python scripts/messung.py --ausgabe docs/messung_nachher.txt

Misst lade_trainings und bestenliste mit 500, 2000 und 5000 Trainings
in einer temporären DB (deine echte DB wird nicht angefasst).
"""
import argparse
import platform
import sys
import tempfile
import timeit
from pathlib import Path

PROJEKT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJEKT))

from app.db import init_db, lade_trainings, speichere_trainings  # noqa: E402
from app.services.bestenliste import bestenliste  # noqa: E402
from scripts.seed import erzeuge_trainings  # noqa: E402

GROESSEN = (500, 2000, 5000)
WIEDERHOLUNGEN = 5


def miss(funktion, wiederholungen: int = WIEDERHOLUNGEN) -> float:
    """Bester Wert aus mehreren Läufen in Millisekunden (robust gegen Ausreisser)."""
    return min(timeit.repeat(funktion, number=1, repeat=wiederholungen)) * 1000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ausgabe", default=None, help="Ergebnis zusätzlich in Datei speichern")
    args = parser.parse_args()

    zeilen = [f"Messung Trainingslog – Python {platform.python_version()}, {platform.system()}",
              f"Bester von {WIEDERHOLUNGEN} Läufen, Angaben in ms",
              "",
              f"{'Trainings':>10} {'Sätze':>8} {'lade_trainings':>16} {'bestenliste':>13}"]
    with tempfile.TemporaryDirectory() as ordner:
        for n in GROESSEN:
            db = str(Path(ordner) / f"mess_{n}.db")
            init_db(db)
            speichere_trainings(db, erzeuge_trainings(n, seed=1))
            trainings = lade_trainings(db)
            saetze = sum(len(t.saetze) for t in trainings)
            t_laden = miss(lambda: lade_trainings(db))
            t_beste = miss(lambda: bestenliste(trainings))
            zeilen.append(f"{n:>10} {saetze:>8} {t_laden:>16.1f} {t_beste:>13.1f}")

    text = "\n".join(zeilen)
    print(text)
    if args.ausgabe:
        Path(args.ausgabe).write_text(text + "\n", encoding="utf-8")
        print(f"\nGespeichert in {args.ausgabe}")


if __name__ == "__main__":
    main()
