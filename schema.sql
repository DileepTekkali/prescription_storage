create extension if not exists pgcrypto;

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  username text not null,
  age integer not null check (age > 0),
  password_hash text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.prescriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  prescription_date date not null,
  image_path text not null,
  image_url text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_prescriptions_date
  on public.prescriptions (prescription_date desc);

insert into storage.buckets (id, name, public)
values ('prescriptions', 'prescriptions', true)
on conflict (id) do nothing;
