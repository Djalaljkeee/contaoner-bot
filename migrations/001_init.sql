-- Telegram-бот ИЗ-КОНТЕЙНЕРОВ.РФ — DDL для PostgreSQL.
-- Применить однократно после создания пустой БД.

CREATE EXTENSION IF NOT EXISTS citext;

CREATE TYPE product_kind     AS ENUM ('model', 'case');
CREATE TYPE lead_status      AS ENUM ('new', 'in_progress', 'done', 'rejected');
CREATE TYPE lead_source      AS ENUM ('main_menu', 'product_card', 'portfolio', 'contacts');
CREATE TYPE admin_role       AS ENUM ('admin', 'manager');
CREATE TYPE broadcast_status AS ENUM ('draft', 'sending', 'sent', 'failed');

CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    slug        CITEXT       NOT NULL UNIQUE,
    sort_order  INT          NOT NULL DEFAULT 0,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE
);
CREATE INDEX idx_categories_active_sort ON categories (is_active, sort_order);

CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    category_id INT          NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    kind        product_kind NOT NULL,
    title       VARCHAR(255) NOT NULL,
    area_m2     NUMERIC(8,2) CHECK (area_m2 IS NULL OR area_m2 > 0),
    price       NUMERIC(12,2) CHECK (price IS NULL OR price >= 0),
    price_note  VARCHAR(255),
    description TEXT,
    source_url  TEXT,
    sort_order  INT          NOT NULL DEFAULT 0,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_products_category_active ON products (category_id, kind, is_active, sort_order);

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
CREATE UNIQUE INDEX uniq_photo_cover_per_product
    ON product_photos (product_id) WHERE is_cover;

CREATE TABLE users (
    id            BIGINT PRIMARY KEY,
    username      VARCHAR(64),
    full_name     VARCHAR(255),
    phone         VARCHAR(32),
    is_subscribed BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_subscribed ON users (is_subscribed) WHERE is_subscribed;

CREATE TABLE admins (
    id         BIGINT PRIMARY KEY,
    full_name  VARCHAR(255) NOT NULL,
    role       admin_role   NOT NULL,
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE
);
CREATE INDEX idx_admins_role_active ON admins (role, is_active);

CREATE TABLE leads (
    id          SERIAL PRIMARY KEY,
    user_id     BIGINT       NOT NULL REFERENCES users(id)    ON DELETE RESTRICT,
    product_id  INT                   REFERENCES products(id) ON DELETE SET NULL,
    manager_id  BIGINT                REFERENCES admins(id)   ON DELETE SET NULL,
    name        VARCHAR(255) NOT NULL,
    phone       VARCHAR(32)  NOT NULL,
    message     TEXT,
    status      lead_status  NOT NULL DEFAULT 'new',
    source      lead_source  NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_leads_status_created ON leads (status, created_at DESC);
CREATE INDEX idx_leads_manager        ON leads (manager_id) WHERE manager_id IS NOT NULL;
CREATE INDEX idx_leads_user           ON leads (user_id, created_at DESC);
CREATE INDEX idx_leads_product        ON leads (product_id) WHERE product_id IS NOT NULL;

CREATE TABLE faq (
    id         SERIAL PRIMARY KEY,
    question   VARCHAR(500) NOT NULL,
    answer     TEXT         NOT NULL,
    sort_order INT          NOT NULL DEFAULT 0,
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE
);
CREATE INDEX idx_faq_active_sort ON faq (is_active, sort_order);

CREATE TABLE broadcasts (
    id            SERIAL PRIMARY KEY,
    admin_id      BIGINT           NOT NULL REFERENCES admins(id) ON DELETE RESTRICT,
    text          TEXT             NOT NULL,
    photo_file_id VARCHAR(512),
    status        broadcast_status NOT NULL DEFAULT 'draft',
    created_at    TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    sent_at       TIMESTAMPTZ
);
CREATE INDEX idx_broadcasts_status ON broadcasts (status, created_at DESC);
