"""Erzeugt realistische Fake-Trainings in der Datenbank.

    python scripts/seed.py                      # 500 Trainings dazu
    python scripts/seed.py --anzahl 200 --reset # DB leeren, 200 neue
"""
import argparse
import random
import sys
from datetime import date, timedelta
from pathlib import Path

PROJEKT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJEKT))

from app.db import init_db, loesche_alle, speichere_trainings  # noqa: E402
from app.models import Satz, Training  # noqa: E402

# Übung -> (Startgewicht kg, Zuwachs kg über den ganzen Zeitraum, Wdh-Bereich)
UEBUNGEN = {
    "Bankdrücken": (60, 25, (5, 10)),
    "Kniebeugen": (80, 40, (5, 8)),
    "Kreuzheben": (100, 45, (3, 6)),
    "Rudern": (55, 20, (8, 12)),
    "Schulterdrücken": (35, 15, (6, 10)),
    "Klimmzüge": (0, 15, (5, 10)),          # Zusatzgewicht
    "Dips": (0, 20, (6, 12)),               # Zusatzgewicht
    "Latzug": (50, 20, (8, 12)),
    "Beinpresse": (120, 60, (8, 12)),
    "Bizepscurls": (12, 6, (8, 12)),
    "Trizepsdrücken": (20, 10, (10, 15)),
    "Ausfallschritte": (20, 15, (8, 12)),
}


def runde_auf_2_5(kg: float) -> float:
    return max(0.0, round(kg / 2.5) * 2.5)


def erzeuge_trainings(anzahl: int, seed: int = 42, ende: date | None = None) -> tuple[Training, ...]:
    zufall = random.Random(seed)
    ende = ende or date.today()
    start = ende - timedelta(days=round(anzahl * 2.3))
    trainings = []
    for i in range(anzahl):
        fortschritt = i / max(anzahl - 1, 1)
        datum = start + timedelta(days=round(i * 2.3))
        saetze = []
        for uebung in zufall.sample(sorted(UEBUNGEN), k=zufall.randint(3, 5)):
            basis, zuwachs, (wmin, wmax) = UEBUNGEN[uebung]
            gewicht = runde_auf_2_5(basis + zuwachs * fortschritt + zufall.uniform(-5, 5))
            for _ in range(zufall.randint(3, 4)):
                saetze.append(Satz(uebung, gewicht, zufall.randint(wmin, wmax)))
        trainings.append(Training(datum, tuple(saetze)))
    return tuple(trainings)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fake-Trainings erzeugen")
    parser.add_argument("--anzahl", type=int, default=500)
    parser.add_argument("--reset", action="store_true", help="DB vorher leeren")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--db", default=str(PROJEKT / "instance" / "trainingslog.db"))
    args = parser.parse_args()

    init_db(args.db)
    if args.reset:
        loesche_alle(args.db)
    trainings = erzeuge_trainings(args.anzahl, args.seed)
    speichere_trainings(args.db, trainings)
    print(f"{len(trainings)} Trainings mit {sum(len(t.saetze) for t in trainings)} Sätzen "
          f"in {args.db} gespeichert.")


if __name__ == "__main__":
    main()
