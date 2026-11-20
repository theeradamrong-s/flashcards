from datetime import date, timedelta


def setup_deck_with_card(client, headers):
    deck = client.post("/decks", json={"name": "N5"}, headers=headers).json()
    card = client.post(
        f"/decks/{deck['id']}/cards", json={"front": "ねこ", "back": "cat"}, headers=headers
    ).json()
    return deck, card


def test_new_cards_are_due(client, headers):
    deck, card = setup_deck_with_card(client, headers)
    due = client.get(f"/decks/{deck['id']}/due", headers=headers).json()
    assert [c["id"] for c in due] == [card["id"]]


def test_good_review_schedules_tomorrow_and_removes_from_due(client, headers):
    deck, card = setup_deck_with_card(client, headers)
    res = client.post(f"/cards/{card['id']}/review", json={"quality": 4}, headers=headers)
    assert res.status_code == 200
    assert res.json()["repetitions"] == 1
    assert res.json()["due_date"] == (date.today() + timedelta(days=1)).isoformat()
    assert client.get(f"/decks/{deck['id']}/due", headers=headers).json() == []


def test_review_quality_must_be_0_to_5(client, headers):
    _, card = setup_deck_with_card(client, headers)
    res = client.post(f"/cards/{card['id']}/review", json={"quality": 9}, headers=headers)
    assert res.status_code == 422
