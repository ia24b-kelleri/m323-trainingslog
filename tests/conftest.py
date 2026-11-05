from datetime import date

import pytest

from app import create_app
from app.models import Satz, Training


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def beispiel_trainings() -> tuple[Training, ...]:
    return (
        Training(date(2026, 10, 26), (Satz("Bankdrücken", 80.0, 8), Satz("Kniebeugen", 100.0, 5)), 1),
        Training(date(2026, 10, 29), (Satz("Bankdrücken", 82.5, 6),), 2),
        Training(date(2026, 11, 2), (Satz("Kreuzheben", 140.0, 3), Satz("Bankdrücken", 85.0, 5)), 3),
    )
