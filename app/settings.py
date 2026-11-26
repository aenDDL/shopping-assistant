from dataclasses import dataclass


@dataclass
class Settings:
    llm_model: str = "xai:grok-4.6"
