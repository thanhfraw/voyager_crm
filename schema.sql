-- ============================================================
-- Customer App - Supabase Schema
-- Run this in Supabase > SQL Editor
-- ============================================================

-- ── Lookup tables ──────────────────────────────────────────
CREATE TABLE customer_types (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);
CREATE TABLE enterprise_types (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);
CREATE TABLE industries (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);
CREATE TABLE nationalities (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- ── Users ──────────────────────────────────────────────────
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name     VARCHAR(255),
    role          VARCHAR(20) NOT NULL DEFAULT 'viewer'
                  CHECK (role IN ('admin', 'editor', 'viewer')),
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ── Customers ──────────────────────────────────────────────
CREATE TABLE customers (
    id                 SERIAL PRIMARY KEY,
    customer_id        VARCHAR(20) UNIQUE NOT NULL,
    short_name         VARCHAR(100),
    cust_key_code      VARCHAR(100),
    name_en            VARCHAR(255),
    name_vn            VARCHAR(255),
    tax_code           VARCHAR(50),
    customer_type_id   INT REFERENCES customer_types(id),
    enterprise_type_id INT REFERENCES enterprise_types(id),
    industry_id        INT REFERENCES industries(id),
    nationality_id     INT REFERENCES nationalities(id),
    phone              VARCHAR(100),
    email              VARCHAR(255),
    status             VARCHAR(50),
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);

-- ── Customer history (version control per record) ──────────
CREATE TABLE customer_history (
    id          SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    action      VARCHAR(20) NOT NULL CHECK (action IN ('CREATE', 'UPDATE', 'DELETE')),
    changed_by  INT REFERENCES users(id),
    changed_at  TIMESTAMPTZ DEFAULT NOW(),
    old_data    JSONB,
    new_data    JSONB
);

-- ── Import logs ────────────────────────────────────────────
CREATE TABLE import_logs (
    id            SERIAL PRIMARY KEY,
    filename      VARCHAR(255),
    imported_by   INT REFERENCES users(id),
    row_count     INT DEFAULT 0,
    success_count INT DEFAULT 0,
    error_count   INT DEFAULT 0,
    errors        JSONB,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ── Auto-update updated_at trigger ────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER customers_updated_at
BEFORE UPDATE ON customers
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── Seed lookup data ───────────────────────────────────────
INSERT INTO customer_types (name) VALUES ('Trading'),('Manufacturing'),('Service'),('Individual');
INSERT INTO enterprise_types (name) VALUES ('LLC'),('JSC'),('Sole Proprietorship'),('Partnership');
INSERT INTO industries (name) VALUES ('Trading'),('Technology'),('Manufacturing'),('Construction'),('Finance');
INSERT INTO nationalities (name) VALUES ('Vietnam'),('England'),('USA'),('Japan'),('Korea'),('Singapore');
