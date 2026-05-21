# Telegram-бот «ИЗ-КОНТЕЙНЕРОВ.РФ» — MVP

Бот для приёма заявок и показа каталога модульных решений из морских контейнеров.

## Состав MVP

- Главное меню: Каталог, Оставить заявку, О компании, Контакты.
- Каталог: 7 разделов (6 продуктовых + «Разное»). На старте засеяны 8 моделей Skandy House с реальными фото из исходников сайта.
- Сценарий «Оставить заявку»: имя → телефон (контакт или ручной ввод) → сообщение (опционально) → подтверждение.
- Уведомление в общий чат менеджеров с кнопкой «Взять в работу» — первый нажавший фиксируется.
- Хранение: PostgreSQL в проде (через docker compose), SQLite — для локальной разработки.

## Деплой на VPS (Ubuntu + Docker)

Образ собирается GitHub Actions при пуше в `main` и публикуется в GHCR:
`ghcr.io/djalaljkeee/contaoner-bot:latest`.
На VPS только `pull` — без локальной сборки.

### Один раз на сервере

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
# перелогиниться или: newgrp docker
```

### Первый деплой

```bash
# 1. Склонировать репозиторий (нужен только compose + .env, не код)
git clone https://github.com/djalaljkeee/<repo>.git
cd <repo>

# 2. Настроить .env
cp .env.example .env
nano .env
#   BOT_TOKEN=<токен от @BotFather>
#   MANAGERS_CHAT_ID=<id группы менеджеров>
#   ADMIN_IDS=<tg_id через запятую — кто может "Взять в работу">
#   POSTGRES_PASSWORD=<надёжный пароль>

# 3. Подтянуть образ и поднять
docker compose pull
docker compose up -d

# 4. Смотреть логи
docker compose logs -f bot
```

При первом старте `bot` прогонит `python -m scripts.seed` (идемпотентно), затем запустит polling.

### Обновление

После очередного пуша в `main` GHA опубликует новый `:latest`:

```bash
git pull          # подтянуть обновлённый docker-compose.yml, если менялся
docker compose pull
docker compose up -d
```

Можно зафиксировать версию через тег. В `.env`:
```
BOT_IMAGE_TAG=v1.2.3
```
Тогда `docker compose pull` будет тянуть строго `ghcr.io/djalaljkeee/contaoner-bot:v1.2.3`.

### Если пакет приватный

GHCR-пакеты по умолчанию приватные. На странице пакета в GitHub:
**Package settings → Danger Zone → Change visibility → Public**.

Либо оставить приватным и логиниться на VPS:
```bash
# создать Personal Access Token (classic) с правом read:packages
echo <TOKEN> | docker login ghcr.io -u djalaljkeee --password-stdin
```

### Как узнать MANAGERS_CHAT_ID

1. Создать в Telegram группу менеджеров, добавить туда бота с правами писать.
2. Отправить в группу любое сообщение через [@RawDataBot](https://t.me/RawDataBot) или временно добавить логирование в боте.
3. `chat.id` отрицательный для групп (для супергрупп — длинный, начинается с `-100`).

### Как узнать свой ADMIN_IDS

Написать боту `/start` от своего аккаунта, посмотреть в логи (`docker compose logs bot`) — там будет `from_user.id`. Либо использовать [@userinfobot](https://t.me/userinfobot).

## Запуск локально без Docker (для разработки)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # БОТ_ТОКЕН обязателен, остальное опционально
python -m scripts.seed
python -m bot
```

По умолчанию используется SQLite (`./data/bot.db`) — Postgres не нужен.

## Структура

```
bot_mvp/
├── bot/                — код бота (aiogram 3)
│   ├── handlers/       — start, catalog, lead, about
│   ├── keyboards/      — клавиатуры
│   ├── services/       — catalog, leads, users, notifications
│   ├── states/         — FSM состояния
│   ├── db/             — модели и подключение
│   ├── utils/          — phone normalization
│   ├── config.py
│   └── __main__.py
├── scripts/seed.py     — идемпотентное наполнение каталога
├── migrations/         — DDL для PostgreSQL (опционально, бот сам создаёт таблицы)
├── data/photos/        — локальные фото из исходников сайта
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Полезные команды Docker

```bash
docker compose ps                       # статус
docker compose logs -f bot              # логи бота
docker compose logs -f postgres         # логи БД
docker compose exec postgres psql -U bot containers  # SQL-консоль
docker compose exec bot python -m scripts.seed       # перезасев
docker compose down                     # стоп (данные сохранены в томе)
docker compose down -v                  # стоп + удалить данные БД
```

## Что вне MVP

- Админ-панель: каталог наполняется через `scripts/seed.py` или прямым SQL.
- Портфолио (`kind='case'`) — таблицы и сервисы готовы, в роутерах не подключены.
- FAQ, рассылки — таблицы есть, бот не использует.
- Кэширование `file_id` после первой отправки — реализовано в `services/catalog.cache_photo_file_id`, проверяется только в проде.
- Multi-arch образы (arm64) — пока собирается только `linux/amd64`. Если VPS на ARM, добавить `platforms: linux/amd64,linux/arm64` в `.github/workflows/docker.yml`.
