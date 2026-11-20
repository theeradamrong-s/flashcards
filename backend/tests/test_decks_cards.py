from conftest import auth_headers


def make_deck(client, headers, name="DSA terms"):
    return client.post("/decks", json={"name": name}, headers=headers).json()


def make_card(client, headers, deck_id, front="Q", back="A"):
    return client.post(
        f"/decks/{deck_id}/cards", json={"front": front, "back": back}, headers=headers
    ).json()


def test_deck_crud(client, headers):
    res = client.post("/decks", json={"name": "DSA", "description": "midterm"}, headers=headers)
    assert res.status_code == 201
    deck_id = res.json()["id"]

    assert client.get(f"/decks/{deck_id}", headers=headers).json()["name"] == "DSA"

    res = client.patch(f"/decks/{deck_id}", json={"name": "DSA final"}, headers=headers)
    assert res.json()["name"] == "DSA final"
    assert res.json()["description"] == "midterm"     # untouched by the partial update

    assert client.delete(f"/decks/{deck_id}", headers=headers).status_code == 200
    assert client.get(f"/decks/{deck_id}", headers=headers).status_code == 404


def test_deck_list_shows_card_and_due_counts(client, headers):
    deck = make_deck(client, headers)
    make_card(client, headers, deck["id"])
    make_card(client, headers, deck["id"])
    [summary] = client.get("/decks", headers=headers).json()
    assert summary["card_count"] == 2
    assert summary["due_count"] == 2                   # new cards are due today


def test_card_crud(client, headers):
    deck = make_deck(client, headers)
    card = make_card(client, headers, deck["id"], front="ねこ", back="dog")

    res = client.patch(f"/cards/{card['id']}", json={"back": "cat"}, headers=headers)
    assert res.json()["back"] == "cat"
    assert res.json()["front"] == "ねこ"

    assert len(client.get(f"/decks/{deck['id']}/cards", headers=headers).json()) == 1
    assert client.delete(f"/cards/{card['id']}", headers=headers).status_code == 200
    assert client.get(f"/decks/{deck['id']}/cards", headers=headers).json() == []


def test_deleting_a_deck_deletes_its_cards(client, headers):
    deck = make_deck(client, headers)
    card = make_card(client, headers, deck["id"])
    client.delete(f"/decks/{deck['id']}", headers=headers)
    assert client.patch(f"/cards/{card['id']}", json={"back": "x"}, headers=headers).status_code == 404


def test_missing_deck_and_card_return_404(client, headers):
    assert client.get("/decks/99", headers=headers).status_code == 404
    assert client.post("/decks/99/cards", json={"front": "Q", "back": "A"}, headers=headers).status_code == 404
    assert client.patch("/cards/99", json={"back": "x"}, headers=headers).status_code == 404
    assert client.delete("/cards/99", headers=headers).status_code == 404


def test_blank_card_is_rejected(client, headers):
    deck = make_deck(client, headers)
    res = client.post(f"/decks/{deck['id']}/cards", json={"front": "", "back": "A"}, headers=headers)
    assert res.status_code == 422


def test_users_cannot_see_or_change_each_others_decks(client, headers):
    deck = make_deck(client, headers)
    card = make_card(client, headers, deck["id"])
    bob = auth_headers(client, username="bob")

    assert client.get("/decks", headers=bob).json() == []
    assert client.get(f"/decks/{deck['id']}", headers=bob).status_code == 404
    assert client.delete(f"/decks/{deck['id']}", headers=bob).status_code == 404
    assert client.post(f"/decks/{deck['id']}/cards", json={"front": "Q", "back": "A"}, headers=bob).status_code == 404
    assert client.patch(f"/cards/{card['id']}", json={"back": "hacked"}, headers=bob).status_code == 404
    assert client.post(f"/cards/{card['id']}/review", json={"quality": 5}, headers=bob).status_code == 404
