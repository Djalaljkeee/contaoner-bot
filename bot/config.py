from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    db_url: str = Field(default="sqlite+aiosqlite:///./data/bot.db", alias="DB_URL")
    managers_chat_id: int = Field(alias="MANAGERS_CHAT_ID")
    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_IDS")

    company_name: str = Field(default="КОНТЕЙНЕР 24", alias="COMPANY_NAME")
    company_phone: str = Field(default="+7 966 888-12-22", alias="COMPANY_PHONE")
    company_phone2: str = Field(default="+7 965 555-33-66", alias="COMPANY_PHONE2")
    company_email: str = Field(default="petrix.fin@mail.ru", alias="COMPANY_EMAIL")
    company_site: str = Field(default="https://konteiner24.ru", alias="COMPANY_SITE")
    company_address_base: str = Field(
        default="Москва, ул. Котляковская, 6 (база отгрузки)",
        alias="COMPANY_ADDRESS_BASE",
    )
    company_address_office: str = Field(
        default="Москва, Каширское шоссе, 61 к3а (офис)",
        alias="COMPANY_ADDRESS_OFFICE",
    )

    delivery_rate_per_km: int = Field(default=55, alias="DELIVERY_RATE_PER_KM")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _split_admin_ids(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v


settings = Settings()
