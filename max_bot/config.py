from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.max", env_file_encoding="utf-8", extra="ignore")

    max_bot_token: str
    db_url: str = "sqlite+aiosqlite:///./data/max_bot.db"

    # Manager notification target (MAX chat_id of the manager)
    manager_chat_id: int = 0

    company_name: str = "Петрикс-Хоум / КОНТЕЙНЕР 24"
    company_phone: str = "8 (966) 888-12-22"
    company_phone2: str = "8 (965) 555-33-66"
    company_email: str = "Petrix.fin@mail.ru"
    company_site: str = "https://konteiner24.ru"


settings = Settings()
