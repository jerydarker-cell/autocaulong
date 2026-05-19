create table if not exists public.badminton_sync_snapshots (
  id text primary key,
  space text not null,
  app_name text,
  app_version text,
  snapshot_json jsonb not null,
  created_at timestamptz default now()
);
create index if not exists badminton_sync_snapshots_space_created_idx
on public.badminton_sync_snapshots (space, created_at desc);
