-- Миграция для konteiner24.ru — новая схема БД.
-- Применяется поверх 001_init.sql (или вместо него на новой БД).
-- Бот создаёт таблицы автоматически через SQLAlchemy; этот файл — для ручного контроля.

CREATE EXTENSION IF NOT EXISTS citext;

-- Enums
CREATE TYPE product_type      AS ENUM ('house', 'office');
CREATE TYPE container_spec    AS ENUM ('20ft', '40ft', '2x40ft', '3x40ft');
CREATE TYPE badge_type        AS ENUM ('hit', 'new', 'premium');
CREATE TYPE calc_option_group AS ENUM ('module', 'insulation', 'foundation', 'interior', 'windows');
CREATE TYPE lead_type         AS ENUM ('regular', 'preorder', 'calculator');
CREATE TYPE lead_status       AS ENUM ('new', 'in_progress', 'done', 'rejected');
CREATE TYPE lead_source       AS ENUM ('main_menu', 'product_card', 'calculator', 'contacts');
CREATE TYPE admin_role        AS ENUM ('admin', 'manager');
CREATE TYPE broadcast_status  AS ENUM ('draft', 'sending', 'sent', 'failed');

-- Каталог
CREATE TABLE products (
    id             SERIAL PRIMARY KEY,
    type           product_type   NOT NULL,
    container_spec container_spec NOT NULL,
    title          VARCHAR(255)   NOT NULL,
    area_m2        NUMERIC(8,2)   CHECK (area_m2 IS NULL OR area_m2 > 0),
    price_from     NUMERIC(12,2)  CHECK (price_from IS NULL OR price_from >= 0),
    build_days     INT            CHECK (build_days IS NULL OR build_days > 0),
    badge          badge_type,
    description    TEXT,
    sort_order     INT            NOT NULL DEFAULT 0,
    is_active      BOOLEAN        NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_products_type_spec ON products (type, container_spec, is_active, sort_order);

CREATE TABLE product_photos (
    id         SERIAL PRIMARY KEY,
    product_id INT          NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    file_id    VARCHAR(512),
    local_path VARCHAR(512),
    source_url TEXT,
    is_cover   BOOLEAN      NOT NULL DEFAULT FALSE,
    sort_order INT          NOT NULL DEFAULT 0,
    CHECK (file_id IS NOT NULL OR local_path IS NOT NULL OR source_url IS NOT NULL)
);
CREATE INDEX idx_photos_product ON product_photos (product_id, sort_order);

-- Калькулятор
CREATE TABLE calc_options (
    id          SERIAL PRIMARY KEY,
    "group"     calc_option_group NOT NULL,
    title       VARCHAR(255)      NOT NULL,
    price_delta NUMERIC(12,2)     NOT NULL DEFAULT 0,
    area_m2     NUMERIC(8,2),
    sort_order  INT               NOT NULL DEFAULT 0,
    is_active   BOOLEAN           NOT NULL DEFAULT TRUE
);
CREATE INDEX idx_calc_opts_group ON calc_options ("group", is_active, sort_order);

-- Доставка
CREATE TABLE delivery_cities (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(255) NOT NULL,
    distance_km  INT          NOT NULL,
    sort_order   INT          NOT NULL DEFAULT 0
);

-- Пользователи
CREATE TABLE users (
    id            BIGINT PRIMARY KEY,
    username      VARCHAR(64),
    full_name     VARCHAR(255),
    phone         VARCHAR(32),
    is_subscribed BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Администраторы
CREATE TABLE admins (
    id         BIGINT PRIMARY KEY,
    full_name  VARCHAR(255) NOT NULL,
    role       admin_role   NOT NULL,
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE
);

-- Заявки
CREATE TABLE leads (
    id          SERIAL PRIMARY KEY,
    user_id     BIGINT      NOT NULL REFERENCES users(id)    ON DELETE RESTRICT,
    product_id  INT                  REFERENCES products(id) ON DELETE SET NULL,
    manager_id  BIGINT               REFERENCES admins(id)   ON DELETE SET NULL,
    type        lead_type   NOT NULL DEFAULT 'regular',
    name        VARCHAR(255) NOT NULL,
    phone       VARCHAR(32)  NOT NULL,
    message     TEXT,
    calc_config JSONB,
    status      lead_status  NOT NULL DEFAULT 'new',
    source      lead_source  NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_leads_status_created ON leads (status, created_at DESC);
CREATE INDEX idx_leads_user           ON leads (user_id);
CREATE INDEX idx_leads_manager        ON leads (manager_id) WHERE manager_id IS NOT NULL;

-- FAQ
CREATE TABLE faq (
    id         SERIAL PRIMARY KEY,
    question   VARCHAR(500) NOT NULL,
    answer     TEXT         NOT NULL,
    sort_order INT          NOT NULL DEFAULT 0,
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE
);

-- Рассылки
CREATE TABLE broadcasts (
    id            SERIAL PRIMARY KEY,
    admin_id      BIGINT           NOT NULL REFERENCES admins(id) ON DELETE RESTRICT,
    text          TEXT             NOT NULL,
    photo_file_id VARCHAR(512),
    status        broadcast_status NOT NULL DEFAULT 'draft',
    created_at    TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    sent_at       TIMESTAMPTZ
);
