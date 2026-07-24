-- Supabase PostgreSQL Schema for MoleculeIQ Users
-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard/project/tlxyazbunhlnzjmwyqjw/sql)

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    picture TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_google_id ON public.users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- Disable RLS so backend FastAPI database operations can read/write users table
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
