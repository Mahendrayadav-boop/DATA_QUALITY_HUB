from typing import Protocol

from .config import settings


class IntegrationAdapter(Protocol):
    async def sync(self) -> dict: ...


class DemoAdapter:
    def __init__(self, provider: str):
        self.provider = provider

    async def sync(self) -> dict:
        return {"provider": self.provider, "status": "demo_synced", "items": 3}


class CollibraAdapter:
    async def sync(self) -> dict:
        if not settings.collibra_base_url:
            raise ValueError("Collibra integration is not configured")
        return {"provider": "collibra", "status": "connected", "items": 0}


class SodaAdapter:
    async def sync(self) -> dict:
        if not settings.soda_api_url or not settings.soda_api_key:
            raise ValueError("Soda integration is not configured")
        return {"provider": "soda", "status": "connected", "items": 0}


class SnowflakeAdapter:
    async def sync(self) -> dict:
        required = [settings.snowflake_account, settings.snowflake_user, settings.snowflake_password]
        if not all(required):
            raise ValueError("Snowflake integration is not configured")
        return {"provider": "snowflake", "status": "connected", "items": 0}


ADAPTERS = {
    "collibra": CollibraAdapter,
    "soda": SodaAdapter,
    "snowflake": SnowflakeAdapter,
}


def get_adapter(provider: str) -> IntegrationAdapter:
    if provider not in ADAPTERS:
        raise KeyError("Unknown integration provider")
    if settings.demo_mode:
        return DemoAdapter(provider)
    return ADAPTERS[provider]()
