"""FastAPI application: CORS, startup, and chat / expense routes."""

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from agent.run import run_chat, stream_chat
from constants import ALLOWED_ORIGIN_REGEX, DEFAULT_LIST_LIMIT, MAX_LIST_LIMIT
from db import get_session, init_db
from schemas import (
    ChatRequest,
    ChatResponse,
    ExpenseOut,
    ExpenseSummary,
)
from services import expenses as expense_service


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Personal Finance Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply = run_chat(request.message, request.history)

    return ChatResponse(reply=reply)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> EventSourceResponse:
    async def event_generator() -> AsyncIterator[dict]:
        try:
            async for token in stream_chat(request.message, request.history):
                yield {"event": "token", "data": json.dumps({"token": token})}
            yield {"event": "done", "data": json.dumps({"done": True})}
        except Exception as error:  # surface failures to the client, never silently fail
            yield {"event": "error", "data": json.dumps({"error": str(error)})}

    return EventSourceResponse(event_generator())


@app.get("/expenses", response_model=list[ExpenseOut])
def get_expenses(
    limit: int = Query(DEFAULT_LIST_LIMIT, ge=1, le=MAX_LIST_LIMIT),
    session: Session = Depends(get_session),
) -> list[ExpenseOut]:
    rows = expense_service.list_expenses(session, limit=limit)

    return [ExpenseOut.model_validate(row) for row in rows]


@app.get("/expenses/summary", response_model=ExpenseSummary)
def get_expenses_summary(
    session: Session = Depends(get_session),
) -> ExpenseSummary:
    summary = expense_service.get_summary(session)

    return ExpenseSummary.model_validate(summary)
