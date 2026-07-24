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

-- Enable RLS and add a permissive policy for public/anon access
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all operations for anon" ON public.users;

CREATE POLICY "Allow all operations for anon"
ON public.users
FOR ALL
TO public
USING (true)
WITH CHECK (true);
