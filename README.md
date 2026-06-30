# Personal Finance Assistant

A ChatGPT-style personal assistant that chats normally **and** tracks your
expenses. The bot reads and writes expenses through LangGraph tool calls — no
hardcoded command parsing. Expenses live in SQLite.

- **Backend:** Python, FastAPI, LangGraph, SQLAlchemy (SQLite).
- **LLM:** OpenAI `gpt-4o` via `langchain-openai` (any OpenAI-compatible
  endpoint works, e.g. OpenRouter).
- **Frontend:** Vite + React + TypeScript + Tailwind, streaming over SSE.

```
apps/
  api/                 FastAPI + LangGraph backend
    main.py            app, CORS, routes
    config.py          env loading (single source of truth)
    db.py              SQLAlchemy engine/session, init_db()
    models.py          Expense table
    schemas.py         Pydantic request/response models
    constants.py       model name, currency, limits, system prompt
    agent/
      graph.py         LangGraph agent (LLM + tools + state)
      tools.py         expense tools the agent can call
      run.py           bridge between HTTP and the graph (sync + streaming)
    services/
      expenses.py      pure DB functions (add/list/summary)
    requirements.txt
    .env.example
  web/                 Vite React-TS frontend
    .env.example
```

## Prerequisites

- Python 3.12+
- Node 20+ and npm
- An OpenAI (or OpenAI-compatible) API key

## 1. Backend

```bash
cd apps/api

# Use the repo's virtualenv (already at ../../env) or create your own:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure the API key
cp .env.example .env
# then edit .env and set OPENAI_API_KEY=...

# Run (creates expenses.db on first start)
uvicorn main:app --reload --port 8000
```

API runs at `http://localhost:8000`. Interactive docs at `/docs`.

### Endpoints

| Method | Path               | Description                                        |
| ------ | ------------------ | -------------------------------------------------- |
| POST   | `/chat`            | Run the agent, return the full reply (JSON).       |
| POST   | `/chat/stream`     | Same, streamed token-by-token over SSE.            |
| GET    | `/expenses`        | Recent expenses. `?limit=` (default 20, max 100).  |
| GET    | `/expenses/summary`| Totals: today, this_month, all_time, by_category.  |

### Environment variables (`apps/api/.env`)

| Variable          | Required | Default        | Notes                                            |
| ----------------- | -------- | -------------- | ------------------------------------------------ |
| `OPENAI_API_KEY`  | yes      | —              | OpenAI or compatible key.                        |
| `OPENAI_BASE_URL` | no       | OpenAI default | Set to e.g. `https://openrouter.ai/api/v1`.      |
| `OPENAI_MODEL`    | no       | `gpt-4o`       | On OpenRouter use `openai/gpt-4o`.               |
| `DB_PATH`         | no       | `expenses.db`  | SQLite file path.                                |

## 2. Frontend

```bash
cd apps/web
npm install --legacy-peer-deps
cp .env.example .env   # optional; defaults to http://localhost:8000

npm run dev
```

App runs at `http://localhost:5173`. Start the backend first.

> `--legacy-peer-deps` is needed only because the scaffold pins a bleeding-edge
> ESLint 10 toolchain with strict peer ranges.

### Frontend environment (`apps/web/.env`)

| Variable       | Default                 | Notes                       |
| -------------- | ----------------------- | --------------------------- |
| `VITE_API_URL` | `http://localhost:8000` | Base URL of the backend.    |

## Usage

Open the app and chat:

- "I spent ₹250 on lunch" → the agent records it and confirms the monthly total.
- "How much did I spend this month?" → answered from the summary tool.
- "Show my last 5 expenses" → lists recent rows.
- Anything non-financial is answered as a normal conversation.

The database starts empty.
