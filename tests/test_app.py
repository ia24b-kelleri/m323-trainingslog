from app import create_app


def test_index_returns_200():
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
