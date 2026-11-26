from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from dotenv import load_dotenv
from fastapi import FastAPI

from app import api
from app.settings import Settings
from app.wiring import SystemPrompt, get_all_providers

load_dotenv()


def read_prompt() -> str:
    file = Path("prompt.txt")
    return file.read_text(encoding="utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()


def create_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(api.router)
    setup_dishka(container, app)
    return app


def create_container(settings: Settings, prompt: str) -> AsyncContainer:
    return make_async_container(
        *get_all_providers(),
        context={Settings: settings, SystemPrompt: prompt},
    )


def main() -> FastAPI:
    settings = Settings()
    prompt = read_prompt()
    return create_app(create_container(settings, prompt))
