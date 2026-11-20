def test_register_and_login(client):
    res = client.post("/auth/register", json={"username": "Alice", "password": "secret12"})
    assert res.status_code == 201
    assert res.json()["username"] == "alice"          # stored in lowercase
    assert "password" not in res.json()
    assert "password_hash" not in res.json()

    res = client.post("/auth/login", json={"username": "alice", "password": "secret12"})
    assert res.status_code == 200
    token = res.json()["access_token"]

    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.json()["username"] == "alice"


def test_duplicate_username_is_rejected(client):
    client.post("/auth/register", json={"username": "alice", "password": "secret12"})
    res = client.post("/auth/register", json={"username": "ALICE", "password": "other123"})
    assert res.status_code == 409


def test_short_password_is_rejected(client):
    res = client.post("/auth/register", json={"username": "alice", "password": "123"})
    assert res.status_code == 422


def test_wrong_password_and_unknown_user_get_same_error(client):
    client.post("/auth/register", json={"username": "alice", "password": "secret12"})
    wrong = client.post("/auth/login", json={"username": "alice", "password": "nope1234"})
    unknown = client.post("/auth/login", json={"username": "bob", "password": "secret12"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_endpoints_need_login(client):
    assert client.get("/decks").status_code == 401
    assert client.get("/decks", headers={"Authorization": "Bearer garbage"}).status_code == 401
