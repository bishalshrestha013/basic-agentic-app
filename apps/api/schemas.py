"""Pydantic request/response models for the HTTP API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


class ExpenseOut(BaseModel):
    id: int
    amount: float
    description: str | None
    category: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryTotal(BaseModel):
    category: str
    total: float


class ExpenseSummary(BaseModel):
    today: float
    this_month: float
    all_time: float
    by_category: list[CategoryTotal]
