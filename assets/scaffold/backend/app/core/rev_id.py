import secrets
from typing import Any

from alembic.script import ScriptDirectory

MAX_SEQUENTIAL_REV_ID = 999_999


def next_sequential_rev_id(script: ScriptDirectory) -> str:
    numbers: list[int] = []
    for revision in script.walk_revisions():
        value = revision.revision
        if isinstance(value, str) and value.isdigit() and len(value) <= 6:
            numbers.append(int(value))
    next_id = max(numbers, default=0) + 1
    if next_id > MAX_SEQUENTIAL_REV_ID:
        raise ValueError("Sequential revision id space exhausted; switch rev_id_style to random")
    return f"{next_id:06d}"


def assign_rev_id(context: Any, revision: Any, directives: list[Any]) -> None:
    if not directives:
        return
    cmd_opts = getattr(context.config, "cmd_opts", None)
    if getattr(cmd_opts, "rev_id", None):
        return
    style = (context.config.get_main_option("rev_id_style") or "sequential").strip().lower()
    script = directives[0]
    if style == "sequential":
        script.rev_id = next_sequential_rev_id(ScriptDirectory.from_config(context.config))
    elif style == "random":
        script.rev_id = secrets.token_hex(6)
    else:
        raise ValueError(f"Unknown rev_id_style: {style!r}")
