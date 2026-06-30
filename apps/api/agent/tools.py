"""Expense tools the LangGraph agent can call.

Each tool opens its own short-lived session and delegates the real work to the
service layer. Tools return plain dicts so the model gets clean, structured
results to reason over.
"""

from langchain_core.tools import tool

from constants import CURRENCY_SYMBOL, DEFAULT_LIST_LIMIT
from db import SessionLocal
from services import expenses as expense_service


@tool
def add_expense(
    amount: float,
    description: str | None = None,
    category: str | None = None,
) -> dict:
    """Record a new expense for the user.

    Args:
        amount: The amount spent, in Indian rupees.
        description: A short description of what the money was spent on.
        category: A category such as food, travel, or bills. Defaults to general.
    """
    session = SessionLocal()
    try:
        expense = expense_service.add_expense(
            session, amount=amount, description=description, category=category
        )
        summary = expense_service.get_summary(session)
    finally:
        session.close()

    return {
        "status": "added",
        "id": expense.id,
        "amount": expense.amount,
        "description": expense.description,
        "category": expense.category,
        "currency": CURRENCY_SYMBOL,
        "month_total_after": summary["this_month"],
    }


@tool
def get_expense_summary() -> dict:
    """Get spending totals: today, this month, all time, and by category."""
    session = SessionLocal()
    try:
        summary = expense_service.get_summary(session)
    finally:
        session.close()

    return {"currency": CURRENCY_SYMBOL, **summary}


@tool
def list_expenses(limit: int = DEFAULT_LIST_LIMIT) -> dict:
    """List the user's most recent expenses, newest first.

    Args:
        limit: Maximum number of expenses to return.
    """
    session = SessionLocal()
    try:
        rows = expense_service.list_expenses(session, limit=limit)
        expenses = [
            {
                "id": row.id,
                "amount": row.amount,
                "description": row.description,
                "category": row.category,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
    finally:
        session.close()

    return {"currency": CURRENCY_SYMBOL, "count": len(expenses), "expenses": expenses}


TOOLS = [add_expense, get_expense_summary, list_expenses]
