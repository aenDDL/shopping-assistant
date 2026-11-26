from dataclasses import dataclass
from typing import Protocol

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from pydantic import BaseModel, Field
from pydantic_ai import RunContext

router = APIRouter(route_class=DishkaRoute)


class Database(Protocol):
    async def get_quantity(self, product_id: str) -> int: ...


class RunAgentFn(Protocol):
    async def __call__(self, question: str) -> str: ...


@dataclass
class AgentDeps:
    db: Database


class AgentOutput(BaseModel):
    available: bool
    product_id: str | None = None
    quantity: int
    confidence: float = Field(ge=0, le=1)


async def get_quantity(ctx: RunContext[AgentDeps], product_id: str) -> int:
    return await ctx.deps.db.get_quantity(product_id)


@router.get("/ai/{content}", response_model=AgentOutput)
async def handle_to_ai(run_agent: FromDishka[RunAgentFn], content: str):
    return await run_agent(content)
