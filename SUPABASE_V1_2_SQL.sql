-- Badminton Vinh Production Ready v1.2 Cloud Login / Snapshot Sync
create extension if not exists pgcrypto;

create table if not exists badminton_snapshots (
  id uuid primary key default gen_random_uuid(),
  space text not null,
  payload jsonb not null,
  created_at timestamptz default now()
);

create index if not exists badminton_snapshots_space_created_idx
on badminton_snapshots(space, created_at desc);
