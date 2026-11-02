from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notes.models import Note
from app.modules.notes.schemas import NoteCreate


async def list_notes(session: AsyncSession) -> list[Note]:
    result = await session.scalars(select(Note).order_by(Note.id.desc()))
    return list(result)


async def create_note(session: AsyncSession, payload: NoteCreate) -> Note:
    note = Note(title=payload.title, content=payload.content)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note
