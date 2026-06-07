from dataclasses import dataclass


@dataclass
class Project:
    id: int
    title: str
    size: str
    price: int
    description: str
    image_url: str


PROJECTS: list[Project] = [
    Project(
        id=1,
        title="Офис продаж 6×2.4 м",
        size="20 футов",
        price=215_000,
        description="Хит продаж! Готовый офис продаж из морского контейнера 20 футов. "
                    "Утепление 100 мм, внутренняя отделка, электрика под ключ.",
        image_url="https://konteiner24.ru/upload/iblock/1a8/1a8b99694.png",
    ),
    Project(
        id=2,
        title="Жилой модуль 12×2.4 м (Глэмпинг)",
        size="40 футов",
        price=360_000,
        description="Премиум жилой модуль для глэмпинга из контейнера 40 футов. "
                    "Панорамное остекление, дизайнерская отделка, полный комплект.",
        image_url="https://konteiner24.ru/upload/iblock/11d/11d9eb688.png",
    ),
    Project(
        id=3,
        title="Модульный дом с открытой террасой",
        size="40 футов",
        price=285_000,
        description="Модульный дом из контейнера 40 футов с просторной открытой террасой. "
                    "Идеально для загородного отдыха и постоянного проживания.",
        image_url="https://konteiner24.ru/upload/iblock/1be/1be5475a3.png",
    ),
    Project(
        id=4,
        title="Жилой модуль-студия 6×2.4 м",
        size="20 футов",
        price=168_000,
        description="Хит продаж! Компактная студия из контейнера 20 футов. "
                    "Базовая комплектация, быстрый монтаж от 7 дней. Старт от 168 000 ₽.",
        image_url="https://konteiner24.ru/upload/iblock/196/1962ca96f.png",
    ),
    Project(
        id=5,
        title="Премиум модуль с панорамным фасадом",
        size="20 футов",
        price=320_000,
        description="Премиальное решение с большим панорамным фасадом. "
                    "Стильный дизайн, высококачественные материалы отделки.",
        image_url="https://konteiner24.ru/upload/iblock/1df/1dfceec2e.png",
    ),
    Project(
        id=6,
        title="Лесной модуль с крытой верандой",
        size="20 футов",
        price=245_000,
        description="Уютный модуль с крытой верандой для отдыха на природе. "
                    "Деревянная отделка фасада, теплоизоляция 150 мм.",
        image_url="https://konteiner24.ru/upload/iblock/1f5/1f56d530c.png",
    ),
]
