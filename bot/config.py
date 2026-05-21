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

    company_phone: str = Field(default="+7 985 888-58-86", alias="COMPANY_PHONE")
    company_email: str = Field(default="9858885886@mail.ru", alias="COMPANY_EMAIL")
    company_site: str = Field(default="https://из-контейнеров.рф", alias="COMPANY_SITE")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _split_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v


settings = Settings()
