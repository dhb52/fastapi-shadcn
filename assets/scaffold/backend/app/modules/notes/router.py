from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.modules.notes.schemas import NoteCreate, NoteRead
from app.modules.notes.service import create_note, list_notes

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteRead])
async def read_notes(session: SessionDep) -> list[NoteRead]:
    notes = await list_notes(session)
    return [NoteRead.model_validate(note) for note in notes]


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def add_note(payload: NoteCreate, session: SessionDep) -> NoteRead:
    note = await create_note(session, payload)
    return NoteRead.model_validate(note)
