from httpx import AsyncClient


async def test_create_and_list_notes(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/notes",
        json={"title": "first", "content": "hello"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "first"
    assert created["content"] == "hello"
    assert created["id"] == 1

    list_response = await client.get("/api/v1/notes")
    assert list_response.status_code == 200
    notes = list_response.json()
    assert len(notes) == 1
    assert notes[0]["id"] == created["id"]
