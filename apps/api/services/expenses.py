"""Pure database functions for expenses. No LLM logic lives here.

These are the only functions that read or write the expenses table. The agent
tools and the HTTP routes both call through this layer.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from constants import DEFAULT_CATEGORY, DEFAULT_LIST_LIMIT, MAX_LIST_LIMIT
from models import Expense


def add_expense(
    session: Session,
    amount: float,
    description: str | None = None,
    category: str | None = None,
) -> Expense:
    """Insert one expense row and return the persisted instance."""
    expense = Expense(
        amount=amount,
        description=description,
        category=category or DEFAULT_CATEGORY,
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)

    return expense


def list_expenses(
    session: Session, limit: int = DEFAULT_LIST_LIMIT
) -> list[Expense]:
    """Return the most recent expenses, newest first."""
    safe_limit = max(1, min(limit, MAX_LIST_LIMIT))
    statement = (
        select(Expense).order_by(Expense.created_at.desc()).limit(safe_limit)
    )

    return list(session.scalars(statement).all())


def _month_start(now: datetime) -> datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _day_start(now: datetime) -> datetime:
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _sum_since(session: Session, since: datetime | None) -> float:
    statement = select(func.coalesce(func.sum(Expense.amount), 0.0))
    if since is not None:
        statement = statement.where(Expense.created_at >= since)

    return float(session.scalar(statement) or 0.0)


def get_summary(session: Session) -> dict:
    """Return today / this_month / all_time totals and a category breakdown."""
    now = datetime.now(timezone.utc)

    by_category_rows = session.execute(
        select(
            func.coalesce(Expense.category, DEFAULT_CATEGORY),
            func.coalesce(func.sum(Expense.amount), 0.0),
        ).group_by(Expense.category)
    ).all()

    by_category = [
        {"category": category, "total": float(total)}
        for category, total in by_category_rows
    ]

    return {
        "today": _sum_since(session, _day_start(now)),
        "this_month": _sum_since(session, _month_start(now)),
        "all_time": _sum_since(session, None),
        "by_category": by_category,
    }
