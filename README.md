# FastAPI + shadcn Skill

这是一个 Agent Skill，不是可直接运行的应用。它把 FastAPI + React/shadcn 项目的创建和扩展流程交给 Agent 执行：模块化异步后端、Alembic 迁移、slowapi 限流、图形验证码、SQLite/PostgreSQL 切换、可选 Celery、Docker 和根级 pre-commit。

Agent 的执行流程在 [SKILL.md](SKILL.md)，扩展配方在 [references/](references/)，可运行模板在 [assets/scaffold/](assets/scaffold/)。

## 安装

需要 Node.js 22.20 或更高版本。在项目根目录运行：

```bash
npx skills add dhb52/fastapi-shadcn
```

按提示选择 Agent 和安装范围。默认安装到当前项目；安装到用户目录、供所有项目使用：

```bash
npx skills add dhb52/fastapi-shadcn -g
```

更新和卸载：

```bash
npx skills update fastapi-shadcn
npx skills remove fastapi-shadcn
```

没有 Node.js 时，可以直接克隆到通用技能目录：

```bash
git clone git@github.com:dhb52/fastapi-shadcn.git ~/.agents/skills/fastapi-shadcn
```

其他 Agent 使用各自的技能目录，把目标路径换成对应目录即可。

## 使用

在对话中直接描述任务，例如“用 FastAPI + shadcn 创建一个项目”。Agent 会按 [SKILL.md](SKILL.md) 的流程确定技术选型、脚手架、实现和验收。

也可以手动运行脚手架：

```bash
./scripts/scaffold.sh ../my-app --rev-id-style sequential
```

`--rev-id-style random` 改用 12 位随机 revision ID。

脚手架需要：

- Python 3.12 和 uv
- Git
- bun、pnpm 或 npm（按此顺序检测）

## 生成的项目

- `backend/`：FastAPI + async SQLAlchemy 2.1 + Alembic；开发用 SQLite，部署用 PostgreSQL
- `frontend/`：React 19 + Vite 8 + Tailwind v4 + shadcn/ui + i18next
- slowapi 限流、图形验证码（默认关闭）、可选 Celery worker
- 根级 `.pre-commit-config.yaml`：ruff、mypy、Biome、TypeScript
- `compose.yaml`：本地 PostgreSQL 和 Redis

默认不生成登录/注册流程，只提供验证码模块，接入方式见 [references/backend.md](references/backend.md)。

项目的启动、迁移、Docker 和验收命令见 [assets/scaffold/README.md](assets/scaffold/README.md)。

## 目录

```text
SKILL.md              Agent 工作流与硬性规则
references/           后端、前端、工程、布局、assistant-ui 配方
scripts/scaffold.sh   项目脚手架
assets/scaffold/      完整项目模板
```

## 文档

| 文件 | 内容 |
| --- | --- |
| [SKILL.md](SKILL.md) | 默认技术栈、创建与扩展流程、验收标准 |
| [references/backend.md](references/backend.md) | 功能模块、迁移、限流、验证码、Celery、Docker |
| [references/frontend.md](references/frontend.md) | 包管理器、shadcn、API 客户端、i18n、Biome |
| [references/engineering.md](references/engineering.md) | monorepo、pre-commit、gitignore |
| [references/layout.md](references/layout.md) | 模板选型与目录决策 |
| [references/assistant-ui.md](references/assistant-ui.md) | 可选 AI 聊天界面 |
