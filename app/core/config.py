"""Configurações da aplicação lidas de variáveis de ambiente."""
import os
from dataclasses import dataclass, field


def _ler_origens_cors() -> list[str]:
    valor = os.getenv("CORS_ORIGINS", "*")
    return [origem.strip() for origem in valor.split(",") if origem.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Alerta Córrego API"
    app_version: str = "1.0.0"
    # SQLite por padrão; troque por PostgreSQL via DATABASE_URL, ex.:
    # postgresql+psycopg2://alerta:alerta@localhost:5432/alerta_corrego
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./alerta_corrego.db")
    )
    cors_origins: list[str] = field(default_factory=_ler_origens_cors)
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


settings = Settings()
