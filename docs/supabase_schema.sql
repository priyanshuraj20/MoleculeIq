-- ============================================================
-- MoleculeIQ — Supabase Database Schema
-- Run this entire block in the Supabase SQL Editor.
-- ============================================================


-- ============================================================
-- TABLE 1: iqvia_sales
--
-- Purpose: Mock market intelligence data (representative of
--          real IQVIA MIDAS dataset structure).
--          Queried by the Market Insights Agent.
--
-- Why each field exists:
--   id               — UUID primary key. Avoids sequential int IDs
--                      leaking row count to clients.
--   molecule_name    — The API/drug name being researched. Indexed
--                      because every query filters by this.
--   year             — Year of market data. Allows trend analysis.
--   region           — Geographic split (Global, US, EU, etc.).
--                      Real market reports are always region-split.
--   therapeutic_area — The disease/condition category. Helps agents
--                      understand the competitive context.
--   market_size_usd_mn— Market size in USD millions. The core
--                       commercial metric decision-makers need.
--   cagr_percent     — 5-year compound annual growth rate.
--                      High CAGR = attractive market.
--   competitor_count — Number of competing products in this segment.
--   data_source      — Always labeled as mock for transparency.
--   created_at       — Audit timestamp.
-- ============================================================

CREATE TABLE IF NOT EXISTS iqvia_sales (
    id                  UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    molecule_name       VARCHAR(150)    NOT NULL,
    year                INTEGER         NOT NULL CHECK (year >= 2000 AND year <= 2035),
    region              VARCHAR(100)    NOT NULL,
    therapeutic_area    VARCHAR(150)    NOT NULL,
    market_size_usd_mn  DECIMAL(12, 2)  NOT NULL CHECK (market_size_usd_mn >= 0),
    cagr_percent        DECIMAL(5, 2),
    competitor_count    INTEGER         DEFAULT 0 CHECK (competitor_count >= 0),
    data_source         VARCHAR(150)    DEFAULT 'IQVIA MIDAS (mock)',
    created_at          TIMESTAMPTZ     DEFAULT NOW()
);

-- Index for fast molecule lookups (primary query pattern)
CREATE INDEX IF NOT EXISTS idx_iqvia_molecule
    ON iqvia_sales (molecule_name);

-- Index for molecule + year combined queries (trend analysis)
CREATE INDEX IF NOT EXISTS idx_iqvia_molecule_year
    ON iqvia_sales (molecule_name, year);


-- ============================================================
-- TABLE 2: patents
--
-- Purpose: Mock patent landscape data (representative of
--          USPTO / EPO / national filing databases).
--          Queried by the Patent Landscape Agent.
--
-- Why each field exists:
--   id              — UUID primary key.
--   molecule_name   — Indexed. Every query filters by this.
--   patent_number   — Actual filing reference (e.g., US10123456).
--                     Allows source citation in the report.
--   jurisdiction    — Country/region code (US, EU, IN, JP, CN).
--                     FTO analysis is always jurisdiction-specific.
--   filing_date     — When the application was filed.
--   expiry_date     — Critical: determines when market becomes open.
--                     20 years from filing is the standard term.
--   status          — Active | Expired | Pending. Core FTO signal.
--   patent_type     — Composition of Matter / Formulation /
--                     Method of Use. Affects FTO risk level.
--   assignee        — Who holds the patent. Competitive intelligence.
--   fto_status      — Freedom-to-Operate pre-assessment:
--                     Free to Operate | At Risk | Blocked.
--   data_source     — Source label for citation.
--   created_at      — Audit timestamp.
-- ============================================================

CREATE TABLE IF NOT EXISTS patents (
    id              UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
    molecule_name   VARCHAR(150) NOT NULL,
    patent_number   VARCHAR(60),
    jurisdiction    VARCHAR(10)  NOT NULL,
    filing_date     DATE,
    expiry_date     DATE,
    status          VARCHAR(20)  NOT NULL CHECK (status IN ('Active', 'Expired', 'Pending')),
    patent_type     VARCHAR(100),
    assignee        VARCHAR(200),
    fto_status      VARCHAR(30)  NOT NULL DEFAULT 'Free to Operate'
                                          CHECK (fto_status IN ('Free to Operate', 'At Risk', 'Blocked')),
    data_source     VARCHAR(150) DEFAULT 'USPTO / EPO (mock)',
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Index for fast molecule lookups
CREATE INDEX IF NOT EXISTS idx_patents_molecule
    ON patents (molecule_name);

-- Index for jurisdiction-filtered queries
CREATE INDEX IF NOT EXISTS idx_patents_molecule_jurisdiction
    ON patents (molecule_name, jurisdiction);


-- ============================================================
-- ROW LEVEL SECURITY
--
-- Supabase enables RLS by default. Without a read policy,
-- the anon key returns 0 rows even if data exists.
-- We enable anon read access for these mock/public tables.
-- No writes are allowed via anon key.
-- ============================================================

ALTER TABLE iqvia_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE patents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon reads on iqvia_sales"
    ON iqvia_sales FOR SELECT TO anon USING (true);

CREATE POLICY "Allow anon reads on patents"
    ON patents FOR SELECT TO anon USING (true);


-- ============================================================
-- SAMPLE DATA — iqvia_sales
-- Using well-known generic molecules: Metformin, Ibuprofen,
-- Aspirin, Atorvastatin. Numbers are representative (not real).
-- ============================================================

INSERT INTO iqvia_sales
    (molecule_name, year, region, therapeutic_area, market_size_usd_mn, cagr_percent, competitor_count)
VALUES
    -- Metformin (Type 2 Diabetes) — large established market
    ('Metformin', 2022, 'Global',        'Diabetes - Type 2',              4820.50, 6.2, 45),
    ('Metformin', 2022, 'United States', 'Diabetes - Type 2',              1850.00, 4.8, 23),
    ('Metformin', 2022, 'Europe',        'Diabetes - Type 2',              1240.30, 5.1, 18),
    ('Metformin', 2022, 'Asia Pacific',  'Diabetes - Type 2',              1420.60, 8.9, 31),
    ('Metformin', 2023, 'Global',        'Diabetes - Type 2',              5120.80, 6.2, 48),
    ('Metformin', 2023, 'United States', 'Diabetes - Type 2',              1940.50, 4.8, 25),
    ('Metformin', 2023, 'Europe',        'Diabetes - Type 2',              1310.00, 5.1, 19),

    -- Ibuprofen (NSAID Pain Management) — mature, competitive market
    ('Ibuprofen', 2022, 'Global',        'Pain Management - NSAIDs',       2340.00, 3.8, 62),
    ('Ibuprofen', 2022, 'United States', 'Pain Management - NSAIDs',        890.50, 2.9, 28),
    ('Ibuprofen', 2022, 'Europe',        'Pain Management - NSAIDs',        640.20, 3.2, 22),
    ('Ibuprofen', 2023, 'Global',        'Pain Management - NSAIDs',       2430.80, 3.8, 64),

    -- Aspirin (Cardiovascular / Antiplatelet) — slow-growth, very mature
    ('Aspirin', 2022, 'Global',          'Cardiovascular / Antiplatelet',  1560.20, 1.2, 55),
    ('Aspirin', 2022, 'United States',   'Cardiovascular / Antiplatelet',   620.00, 0.8, 22),
    ('Aspirin', 2023, 'Global',          'Cardiovascular / Antiplatelet',  1580.00, 1.2, 55),

    -- Atorvastatin (Cholesterol / Cardiovascular) — off-patent, generic
    ('Atorvastatin', 2022, 'Global',     'Cardiovascular - Statins',       4120.00, 2.1, 78),
    ('Atorvastatin', 2022, 'United States','Cardiovascular - Statins',     1640.00, 1.4, 34),
    ('Atorvastatin', 2023, 'Global',     'Cardiovascular - Statins',       4210.00, 2.1, 80);


-- ============================================================
-- SAMPLE DATA — patents
-- Realistic patent scenarios for the same test molecules.
-- Metformin: mostly expired (old molecule), some active formulation patents.
-- ============================================================

INSERT INTO patents
    (molecule_name, patent_number, jurisdiction, filing_date, expiry_date, status, patent_type, assignee, fto_status)
VALUES
    -- Metformin — original compound expired decades ago
    ('Metformin', 'US2868740',       'US', '1955-01-15', '1972-05-20', 'Expired', 'Composition of Matter',       'Aron S.A. (Historical)',          'Free to Operate'),
    ('Metformin', 'GB814978',        'GB', '1956-04-02', '1976-04-02', 'Expired', 'Composition of Matter',       'Aron S.A. (Historical)',          'Free to Operate'),
    ('Metformin', 'EP0567512',       'EU', '1992-03-10', '2012-03-10', 'Expired', 'Formulation - Extended Rel.', 'Bristol-Myers Squibb',            'Free to Operate'),
    -- Active formulation and method-of-use patents
    ('Metformin', 'US8846100',       'US', '2010-06-14', '2030-06-14', 'Active',  'Extended Release Formulation','Sun Pharmaceutical Industries',   'At Risk'),
    ('Metformin', 'IN202118044291',  'IN', '2021-09-30', '2041-09-30', 'Active',  'Method of Use - Oncology',    'CSIR India',                      'At Risk'),
    ('Metformin', 'CN112245409',     'CN', '2020-11-25', '2040-11-25', 'Pending', 'Novel Salt Form',             'Fosun Pharma',                    'Free to Operate'),
    ('Metformin', 'JP2022512345',    'JP', '2019-03-15', '2039-03-15', 'Active',  'Fixed-dose Combination',      'Takeda Pharmaceutical',           'At Risk'),

    -- Ibuprofen — original compound expired, some novel formulations active
    ('Ibuprofen', 'US3228831',       'US', '1964-01-01', '1985-01-01', 'Expired', 'Composition of Matter',       'Boots (Historical)',               'Free to Operate'),
    ('Ibuprofen', 'EP0122232',       'EU', '1983-06-22', '2003-06-22', 'Expired', 'Composition of Matter',       'Boots (Historical)',               'Free to Operate'),
    ('Ibuprofen', 'US20180185303',   'US', '2018-07-05', '2038-07-05', 'Active',  'Novel Liquid Formulation',    'Pfizer Consumer Healthcare',      'At Risk'),

    -- Aspirin — fully expired, generic everywhere
    ('Aspirin', 'DE36433',           'DE', '1897-08-10', '1917-08-10', 'Expired', 'Composition of Matter',       'Bayer AG (Historical)',            'Free to Operate'),
    ('Aspirin', 'US644077',          'US', '1898-02-27', '1918-02-27', 'Expired', 'Composition of Matter',       'Bayer AG (Historical)',            'Free to Operate'),

    -- Atorvastatin — key Lipitor patents expired, generics widespread
    ('Atorvastatin', 'US4681893',    'US', '1986-03-26', '2006-03-26', 'Expired', 'Composition of Matter',       'Warner-Lambert (Pfizer)',          'Free to Operate'),
    ('Atorvastatin', 'US5273995',    'US', '1993-11-22', '2013-11-22', 'Expired', 'Process Patent',              'Warner-Lambert (Pfizer)',          'Free to Operate'),
    ('Atorvastatin', 'US20210046050','US', '2021-02-18', '2041-02-18', 'Active',  'Novel Nano-formulation',      'Torrent Pharmaceuticals',         'At Risk');
