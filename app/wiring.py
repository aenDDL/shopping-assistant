from typing import NewType

from dishka import Provider, Scope, from_context, provide
from pydantic_ai import Agent

from app.api import AgentDeps, AgentOutput, RunAgentFn, get_quantity
from app.settings import Settings

SystemPrompt = NewType("SystemPrompt", str)


class RepositoryPlaceholder:
    async def get_quantity(self, product_id: str) -> int:  # ruff: ignore[unused-method-argument]
        return 5


class AgentProvider(Provider):
    scope = Scope.APP
    prompt = from_context(SystemPrompt)
    settings = from_context(Settings)

    @provide
    def wire_agent(
        self,
        prompt: SystemPrompt,
        s: Settings,
    ) -> Agent[AgentDeps, AgentOutput]:
        return Agent(
            s.llm_model,
            deps_type=AgentDeps,
            output_type=AgentOutput,
            system_prompt=prompt,
            tools=[get_quantity],
        )

    @provide(scope=Scope.REQUEST)
    async def wire_deps(self) -> AgentDeps:
        return AgentDeps(db=RepositoryPlaceholder())

    @provide(scope=Scope.REQUEST)
    def wire_run_agent(
        self,
        agent: Agent[AgentDeps, AgentOutput],
        deps: AgentDeps,
    ) -> RunAgentFn:
        async def run(text: str) -> str:
            result = await agent.run(text, deps=deps)
            return result.output

        return run


def get_all_providers() -> frozenset[Provider]:
    return frozenset({AgentProvider()})
