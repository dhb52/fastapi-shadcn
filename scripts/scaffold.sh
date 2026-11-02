#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-}"
STYLE="sequential"

if [[ -z "$TARGET" ]]; then
  echo "usage: $0 <target-dir> [--rev-id-style sequential|random]" >&2
  exit 1
fi

shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --rev-id-style)
      STYLE="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ "$STYLE" != "sequential" && "$STYLE" != "random" ]]; then
  echo "--rev-id-style must be sequential or random" >&2
  exit 1
fi

if [[ -e "$TARGET" && -n "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
  echo "target is not empty: $TARGET" >&2
  exit 1
fi

mkdir -p "$TARGET"
cp -R "$ROOT/assets/scaffold/." "$TARGET/"

if [[ "$STYLE" == "random" ]]; then
  python3 - "$TARGET/backend/alembic.ini" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
text = text.replace("rev_id_style = sequential", "rev_id_style = random")
text = text.replace(
    "file_template = %%(rev)s_%%(slug)s",
    "file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s",
)
path.write_text(text)
PY
fi

if [[ ! -d "$TARGET/.git" ]]; then
  git -C "$TARGET" init -q
fi

(cd "$TARGET/backend" && uv sync)
(cd "$TARGET/backend" && uv run alembic revision --autogenerate -m "initial schema")
(cd "$TARGET/backend" && uv run alembic upgrade head)

if command -v bun >/dev/null 2>&1; then
  (cd "$TARGET/frontend" && bun install)
  FRONTEND_DEV="bun run dev"
elif command -v pnpm >/dev/null 2>&1; then
  (cd "$TARGET/frontend" && pnpm install)
  FRONTEND_DEV="pnpm dev"
else
  (cd "$TARGET/frontend" && npm install)
  FRONTEND_DEV="npm run dev"
fi

(cd "$TARGET/backend" && uv run pre-commit install)

echo
echo "Project created at $TARGET"
echo "Backend:  cd $TARGET/backend && uv run fastapi dev"
echo "Frontend: cd $TARGET/frontend && $FRONTEND_DEV"
echo "Revision style: $STYLE"
ls "$TARGET/backend/alembic/versions"
