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


-- Chat online ngay trang chủ
create table if not exists badminton_chat_messages (
  id uuid primary key,
  room text not null,
  user_id text,
  user_name text,
  role text,
  message text not null,
  is_deleted int default 0,
  created_at timestamptz default now()
);
create index if not exists badminton_chat_room_created_idx on badminton_chat_messages(room, created_at desc);
