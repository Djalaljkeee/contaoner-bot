from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MaxSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    max_bot_token: str = Field(alias="MAX_BOT_TOKEN")
    max_manager_id: int = Field(alias="MAX_MANAGER_ID")
    max_db_url: str = Field(
        default="sqlite+aiosqlite:///./data/max_bot.db",
        alias="MAX_DB_URL",
    )

    company_name: str = Field(default="Петрикс-Хоум", alias="MAX_COMPANY_NAME")
    company_phone: str = Field(default="8 (966) 888-12-22", alias="MAX_COMPANY_PHONE")
    company_phone2: str = Field(default="8 (965) 555-33-66", alias="MAX_COMPANY_PHONE2")
    company_email: str = Field(default="Petrix.fin@mail.ru", alias="MAX_COMPANY_EMAIL")
    company_site: str = Field(default="konteiner24.ru", alias="MAX_COMPANY_SITE")
    company_founder: str = Field(
        default="Петриков Роман Андреевич", alias="MAX_COMPANY_FOUNDER"
    )
    company_lawyer: str = Field(default="Юлия", alias="MAX_COMPANY_LAWYER")
    social_rutube: str = Field(default="RUTUBE", alias="MAX_SOCIAL_RUTUBE")
    social_vk1: str = Field(default="petrixlogistic", alias="MAX_SOCIAL_VK1")
    social_vk2: str = Field(default="petrixdm", alias="MAX_SOCIAL_VK2")
    social_dzen: str = Field(default="Дзен", alias="MAX_SOCIAL_DZEN")


max_settings = MaxSettings()
