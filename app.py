# -*- coding: utf-8 -*-
"""
Badminton Vinh Ultra - Streamlit one-file app
Chạy: streamlit run app.py

Ứng dụng riêng biệt cho cầu lông: đặt lịch sân, mua bán dụng cụ, đăng bán,
quản lý lịch, dashboard, thông báo, review, dữ liệu SQLite local.
"""

from __future__ import annotations

import base64
import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

APP_NAME = "Badminton Vinh AI Automation Ultra"
APP_VERSION = "5.0 AI Automation Ultra"
DB_PATH = Path("badminton_vinh_ai_automation_ultra.sqlite3")

# -----------------------------
# UI / STYLE
# -----------------------------

def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root{
          --bg:#050b12; --panel:#0d1725; --panel2:#101d2e; --line:#1f334d;
          --text:#eef7ff; --muted:#9fb3c8; --green:#22c55e; --blue:#38bdf8;
          --yellow:#f59e0b; --red:#ef4444; --purple:#8b5cf6;
        }
        .main .block-container{max-width:1120px;padding-top:1.1rem;padding-bottom:4rem;}
        h1,h2,h3{letter-spacing:-.03em;}
        .hero{
          background: radial-gradient(circle at 10% 0%, rgba(34,197,94,.26), transparent 35%),
                      radial-gradient(circle at 90% 0%, rgba(56,189,248,.18), transparent 35%),
                      linear-gradient(135deg,#07111f,#0c1b2d 65%,#08111d);
          border:1px solid rgba(94,234,212,.16); border-radius:28px; padding:22px;
          box-shadow:0 22px 60px rgba(0,0,0,.35); margin-bottom:18px;
        }
        .hero-title{font-size:2.25rem;font-weight:950;line-height:1.05;margin:0 0 .4rem 0;color:#fff;}
        .hero-sub{font-size:1rem;color:var(--muted);max-width:800px;margin:0;}
        .grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:.8rem 0;}
        .grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:.8rem 0;}
        .grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:.8rem 0;}
        .card{
          background:linear-gradient(180deg,rgba(16,29,46,.96),rgba(10,18,31,.96));
          border:1px solid var(--line); border-radius:24px; padding:16px;
          box-shadow:0 18px 36px rgba(0,0,0,.25); min-height:120px;
        }
        .card h3{margin:.2rem 0 .35rem 0;font-size:1.05rem;}
        .muted{color:var(--muted);font-size:.92rem;}
        .metric-big{font-size:1.75rem;font-weight:900;color:#fff;margin:.1rem 0;}
        .pill{display:inline-flex;align-items:center;gap:6px;padding:7px 11px;border-radius:999px;font-weight:800;font-size:.78rem;margin:3px 4px 3px 0;border:1px solid var(--line);}
        .pill.green{background:rgba(34,197,94,.12);color:#86efac;border-color:rgba(34,197,94,.28)}
        .pill.blue{background:rgba(56,189,248,.12);color:#7dd3fc;border-color:rgba(56,189,248,.28)}
        .pill.yellow{background:rgba(245,158,11,.12);color:#fcd34d;border-color:rgba(245,158,11,.28)}
        .pill.red{background:rgba(239,68,68,.12);color:#fca5a5;border-color:rgba(239,68,68,.28)}
        .pill.purple{background:rgba(139,92,246,.12);color:#c4b5fd;border-color:rgba(139,92,246,.28)}
        .court-card,.product-card,.booking-card{
          background:linear-gradient(180deg,#0e1b2b,#0b1422); border:1px solid #1e3350;
          border-radius:24px; padding:15px; margin:10px 0;
        }
        .price{font-size:1.25rem;font-weight:900;color:#86efac;}
        .cta-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;}
        .status-ok{border-left:4px solid var(--green);padding:10px 12px;background:rgba(34,197,94,.08);border-radius:12px;}
        .status-warn{border-left:4px solid var(--yellow);padding:10px 12px;background:rgba(245,158,11,.08);border-radius:12px;}
        .status-bad{border-left:4px solid var(--red);padding:10px 12px;background:rgba(239,68,68,.08);border-radius:12px;}
        .pro-badge{display:inline-flex;align-items:center;gap:7px;padding:8px 12px;border-radius:999px;background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.28);color:#bbf7d0;font-weight:900;font-size:.8rem;margin:3px}.pro-panel{background:linear-gradient(180deg,#0b1628,#09111f);border:1px solid #213855;border-radius:24px;padding:16px;margin:10px 0;box-shadow:0 16px 38px rgba(0,0,0,.24)}.timeline{border-left:3px solid #22c55e;padding-left:14px;margin:10px 0}.timeline-item{margin:12px 0;padding:10px;border-radius:14px;background:#0d1725;border:1px solid #1e3350}.rank{font-size:1.15rem;font-weight:950;color:#86efac}.mobile-nav-note{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);z-index:999;
          background:rgba(8,15,28,.92);border:1px solid #24405f;border-radius:999px;padding:8px 14px;color:#dbeafe;font-size:.8rem;backdrop-filter:blur(8px);}
        .badminton-svg{border-radius:24px;overflow:hidden;border:1px solid #1e3350;margin:.5rem 0;}
        .stButton>button{border-radius:16px!important;min-height:42px;font-weight:850!important;border:1px solid #24405f!important;background:#10233a!important;color:#eef7ff!important;}
        .stButton>button:hover{border-color:#22c55e!important;color:#86efac!important;}
        div[data-testid="stExpander"]{border:1px solid #1f334d!important;border-radius:18px!important;background:#0b1422!important;}
        .owner-chip{display:inline-flex;padding:8px 12px;border-radius:14px;background:#0f2438;border:1px solid #315173;color:#dbeafe;font-weight:900;margin:4px}.ai-ultra{background:linear-gradient(135deg,rgba(34,197,94,.18),rgba(56,189,248,.10));border:1px solid rgba(94,234,212,.28);border-radius:26px;padding:16px;margin:10px 0;box-shadow:0 18px 45px rgba(0,0,0,.28)}.automation-step{border-left:4px solid #38bdf8;background:#081423;border-radius:16px;padding:12px;margin:8px 0}.agent-card{background:linear-gradient(180deg,#0b1f2d,#08131f);border:1px solid #244b68;border-radius:22px;padding:14px;margin:8px 0}.qr-box{font-family:monospace;border:2px dashed #22c55e;border-radius:22px;padding:16px;background:#07111f;text-align:center;font-size:1.2rem;color:#86efac}.heat-cell{border-radius:12px;padding:10px;text-align:center;border:1px solid #1f334d;background:#0d1725}.heat-hot{background:rgba(34,197,94,.18)}.heat-mid{background:rgba(245,158,11,.14)}.heat-low{background:rgba(56,189,248,.10)}.crm-row{background:#0b1422;border:1px solid #1e3350;border-radius:18px;padding:12px;margin:8px 0}.deal-card{background:linear-gradient(135deg,#102a1f,#0b1628);border:1px solid #276749;border-radius:22px;padding:14px;margin:8px 0}
        @media(max-width:850px){
          .main .block-container{padding-left:.75rem;padding-right:.75rem;padding-top:.75rem;}
          .hero{padding:16px;border-radius:22px}.hero-title{font-size:1.65rem}
          .grid,.grid2,.grid3{grid-template-columns:1fr;gap:8px}.card{min-height:auto;padding:13px;border-radius:20px}
          .metric-big{font-size:1.35rem}.pill{font-size:.74rem;padding:6px 9px}
          .court-card,.product-card,.booking-card{border-radius:20px;padding:12px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-title">{title}</div>
          <p class="hero-sub">{subtitle}</p>
          <div style="margin-top:12px">
            <span class="pill green">🏸 Cầu lông TP Vinh</span>
            <span class="pill blue">📅 Đặt sân</span>
            <span class="pill yellow">🛒 Mua bán dụng cụ</span>
            <span class="pill purple">📱 Mobile first</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(icon: str, title: str, body: str, tag: str = "") -> None:
    tag_html = f'<span class="pill blue">{tag}</span>' if tag else ""
    st.markdown(
        f"""
        <div class="card">
          <div style="font-size:1.8rem">{icon}</div>
          <h3>{title}</h3>
          <div class="muted">{body}</div>
          <div style="margin-top:8px">{tag_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, value: Any, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="card">
          <div class="muted">{title}</div>
          <div class="metric-big">{value}</div>
          <div class="muted">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badminton_visual() -> None:
    st.markdown(
        """
        <div class="badminton-svg">
        <svg viewBox="0 0 900 300" width="100%" height="220" preserveAspectRatio="none">
          <defs>
            <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#07111f"/><stop offset="1" stop-color="#0d2a1b"/>
            </linearGradient>
            <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          </defs>
          <rect width="900" height="300" fill="url(#g)"/>
          <rect x="80" y="45" width="740" height="210" rx="18" fill="#0b7a45" stroke="#a7f3d0" stroke-width="4" opacity=".95"/>
          <line x1="450" y1="45" x2="450" y2="255" stroke="#d1fae5" stroke-width="4"/>
          <line x1="80" y1="150" x2="820" y2="150" stroke="#d1fae5" stroke-width="3" opacity=".8"/>
          <line x1="230" y1="45" x2="230" y2="255" stroke="#d1fae5" stroke-width="3" opacity=".8"/>
          <line x1="670" y1="45" x2="670" y2="255" stroke="#d1fae5" stroke-width="3" opacity=".8"/>
          <line x1="80" y1="100" x2="820" y2="100" stroke="#d1fae5" stroke-width="2" opacity=".5"/>
          <line x1="80" y1="200" x2="820" y2="200" stroke="#d1fae5" stroke-width="2" opacity=".5"/>
          <rect x="438" y="40" width="24" height="220" rx="8" fill="#111827" opacity=".7"/>
          <circle cx="285" cy="138" r="18" fill="#f59e0b" filter="url(#glow)">
             <animate attributeName="cx" values="285;610;285" dur="3s" repeatCount="indefinite"/>
             <animate attributeName="cy" values="138;112;138" dur="3s" repeatCount="indefinite"/>
          </circle>
          <text x="120" y="30" fill="#eafff4" font-size="22" font-weight="800">Badminton Vinh Ultra</text>
          <text x="120" y="285" fill="#bbf7d0" font-size="16">Đặt sân · Mua bán · Lịch đấu · Cộng đồng</text>
        </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# DATABASE
# -----------------------------

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = connect()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users(
            id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT, role TEXT DEFAULT 'player', created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS courts(
            id TEXT PRIMARY KEY, name TEXT, area TEXT, address TEXT, phone TEXT, price INTEGER,
            rating REAL, features TEXT, open_time TEXT, close_time TEXT, status TEXT DEFAULT 'active'
        );
        CREATE TABLE IF NOT EXISTS bookings(
            id TEXT PRIMARY KEY, user_id TEXT, court_id TEXT, booking_date TEXT, start_time TEXT, duration INTEGER,
            players INTEGER, note TEXT, status TEXT, total INTEGER, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS products(
            id TEXT PRIMARY KEY, seller_id TEXT, title TEXT, category TEXT, condition TEXT, price INTEGER,
            description TEXT, area TEXT, phone TEXT, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS orders(
            id TEXT PRIMARY KEY, buyer_id TEXT, product_id TEXT, quantity INTEGER, total INTEGER, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS reviews(
            id TEXT PRIMARY KEY, user_id TEXT, target_type TEXT, target_id TEXT, rating INTEGER, comment TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS notifications(
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, body TEXT, kind TEXT, is_read INTEGER DEFAULT 0, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS favorites(
            id TEXT PRIMARY KEY, user_id TEXT, target_type TEXT, target_id TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS coaches(
            id TEXT PRIMARY KEY, name TEXT, level TEXT, area TEXT, phone TEXT, price INTEGER, rating REAL, bio TEXT, available TEXT
        );
        CREATE TABLE IF NOT EXISTS tournaments(
            id TEXT PRIMARY KEY, title TEXT, area TEXT, event_date TEXT, level TEXT, fee INTEGER, prize TEXT, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS tournament_registrations(
            id TEXT PRIMARY KEY, tournament_id TEXT, user_id TEXT, partner_name TEXT, phone TEXT, note TEXT, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS training_plans(
            id TEXT PRIMARY KEY, user_id TEXT, goal TEXT, level TEXT, days_per_week INTEGER, plan_json TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS memberships(
            id TEXT PRIMARY KEY, user_id TEXT, package_name TEXT, court_id TEXT, sessions INTEGER, used_sessions INTEGER, price INTEGER, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS checkins(
            id TEXT PRIMARY KEY, user_id TEXT, booking_id TEXT, court_id TEXT, note TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS feedback(
            id TEXT PRIMARY KEY, user_id TEXT, category TEXT, message TEXT, status TEXT, created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS wallet_transactions(
            id TEXT PRIMARY KEY, user_id TEXT, amount INTEGER, points INTEGER, kind TEXT, note TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS court_owner_notes(
            id TEXT PRIMARY KEY, court_id TEXT, title TEXT, note TEXT, priority TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS coupons(
            id TEXT PRIMARY KEY, code TEXT, title TEXT, discount INTEGER, min_total INTEGER, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS club_posts(
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, body TEXT, category TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS equipment_rentals(
            id TEXT PRIMARY KEY, user_id TEXT, court_id TEXT, item TEXT, price INTEGER, status TEXT, created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS ai_automation_tasks(
            id TEXT PRIMARY KEY, title TEXT, category TEXT, priority TEXT, status TEXT, due_date TEXT, detail TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_campaigns(
            id TEXT PRIMARY KEY, title TEXT, target TEXT, channel TEXT, message TEXT, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_rules(
            id TEXT PRIMARY KEY, name TEXT, trigger_name TEXT, action_text TEXT, is_enabled INTEGER DEFAULT 1, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_logs(
            id TEXT PRIMARY KEY, kind TEXT, message TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_playbooks(
            id TEXT PRIMARY KEY, title TEXT, area TEXT, goal TEXT, steps TEXT, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_scheduled_actions(
            id TEXT PRIMARY KEY, action_name TEXT, target TEXT, cadence TEXT, next_run TEXT, status TEXT, detail TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS ai_experiments(
            id TEXT PRIMARY KEY, title TEXT, hypothesis TEXT, metric TEXT, result TEXT, status TEXT, created_at TEXT
        );
        """
    )
    conn.commit()
    seed_data(conn)
    conn.close()


def row_count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]


def seed_data(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    if row_count(conn, "courts") == 0:
        courts = [
            ("court_1", "Sân Cầu Lông Trung Tâm Vinh", "Trung tâm", "TP Vinh, Nghệ An", "0912 000 111", 90000, 4.8, "Sân thảm, gửi xe, nước uống, thuê vợt", "05:00", "23:00", "active"),
            ("court_2", "Badminton Club Lê Mao", "Lê Mao", "Khu vực Lê Mao, TP Vinh", "0912 000 222", 80000, 4.6, "Sân đôi, đèn LED, phòng thay đồ", "05:30", "22:30", "active"),
            ("court_3", "Sân Cầu Lông Quán Bàu", "Quán Bàu", "Quán Bàu, TP Vinh", "0912 000 333", 70000, 4.5, "Giá tốt, gần khu dân cư, bán cầu", "06:00", "22:00", "active"),
            ("court_4", "Vinh Pro Badminton Arena", "Hưng Dũng", "Hưng Dũng, TP Vinh", "0912 000 444", 120000, 4.9, "Sân chuẩn, camera, đặt lịch online", "05:00", "24:00", "active"),
            ("court_5", "Sân Sinh Viên Vinh", "Bến Thủy", "Bến Thủy, TP Vinh", "0912 000 555", 60000, 4.3, "Giá mềm, nhóm sinh viên, thuê theo giờ", "06:00", "22:00", "active"),
        ]
        cur.executemany("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?)", courts)
    if row_count(conn, "products") == 0:
        products = [
            ("prod_1", "system", "Vợt Yonex Astrox 88D cũ đẹp", "Vợt", "Đã dùng", 1850000, "Vợt công mạnh, phù hợp người chơi trung bình-khá.", "Trung tâm", "0912 888 111", "available", datetime.now().isoformat()),
            ("prod_2", "system", "Giày cầu lông Victor A970 size 41", "Giày", "Mới 90%", 1250000, "Đế bám tốt, form chắc chân.", "Lê Mao", "0912 888 222", "available", datetime.now().isoformat()),
            ("prod_3", "system", "Ống cầu lông Hải Yến loại tập", "Cầu", "Mới", 180000, "Phù hợp luyện tập hàng ngày.", "Quán Bàu", "0912 888 333", "available", datetime.now().isoformat()),
            ("prod_4", "system", "Túi vợt Lining 2 ngăn", "Phụ kiện", "Đã dùng", 450000, "Gọn, đẹp, còn tốt.", "Hưng Dũng", "0912 888 444", "available", datetime.now().isoformat()),
        ]
        cur.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)", products)
    if row_count(conn, "coaches") == 0:
        coaches = [
            ("coach_1", "HLV Minh Đức", "Cơ bản - Trung bình", "Trung tâm", "0905 111 222", 220000, 4.9, "Sửa kỹ thuật tay, bộ chân, phát cầu và chiến thuật đôi.", "Tối 18:00-21:00"),
            ("coach_2", "HLV Thu Trang", "Người mới - Nữ", "Hưng Dũng", "0905 333 444", 200000, 4.8, "Dạy nhập môn nhẹ nhàng, giáo án dễ hiểu, phù hợp người mới.", "Sáng và cuối tuần"),
            ("coach_3", "HLV Anh Quân", "Khá - Nâng cao", "Bến Thủy", "0905 555 666", 280000, 4.9, "Tập tốc độ, di chuyển, phản tạt, đập cầu và thi đấu.", "Theo lịch hẹn"),
        ]
        cur.executemany("INSERT INTO coaches VALUES (?,?,?,?,?,?,?,?,?)", coaches)
    if row_count(conn, "tournaments") == 0:
        tournaments = [
            ("tour_1", "Vinh Friendly Cup cuối tuần", "Trung tâm", (date.today()+timedelta(days=7)).isoformat(), "Trung bình", 120000, "Cúp + quà tài trợ", "open", datetime.now().isoformat()),
            ("tour_2", "Giải đôi nam nữ giao lưu", "Hưng Dũng", (date.today()+timedelta(days=14)).isoformat(), "Giao lưu vui", 100000, "Huy chương + voucher sân", "open", datetime.now().isoformat()),
            ("tour_3", "Pro Challenge Vinh", "Bến Thủy", (date.today()+timedelta(days=21)).isoformat(), "Khá - Nâng cao", 180000, "Tiền thưởng + cúp", "open", datetime.now().isoformat()),
        ]
        cur.executemany("INSERT INTO tournaments VALUES (?,?,?,?,?,?,?,?,?)", tournaments)

    if row_count(conn, "coupons") == 0:
        coupons = [
            ("cp_1", "VINH10", "Giảm 10k đặt sân giờ thấp điểm", 10000, 70000, "active", datetime.now().isoformat()),
            ("cp_2", "NEWBIE20", "Ưu đãi người mới", 20000, 100000, "active", datetime.now().isoformat()),
            ("cp_3", "CLB50", "Combo nhóm/CLB", 50000, 400000, "active", datetime.now().isoformat()),
        ]
        cur.executemany("INSERT INTO coupons VALUES (?,?,?,?,?,?,?)", coupons)
    conn.commit()


def q(sql: str, params: Tuple = ()) -> List[sqlite3.Row]:
    conn = connect()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def execute(sql: str, params: Tuple = ()) -> None:
    conn = connect()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")

# -----------------------------
# SESSION / USER
# -----------------------------

def ensure_session() -> None:
    if "user_id" not in st.session_state:
        st.session_state.user_id = "guest"
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Khách"
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "light_mode" not in st.session_state:
        st.session_state.light_mode = False


def login_panel() -> None:
    with st.sidebar:
        st.markdown(f"### 🏸 {APP_NAME}")
        st.caption(APP_VERSION)
        st.divider()
        st.markdown("#### 👤 Hồ sơ nhanh")
        name = st.text_input("Tên người dùng", value=st.session_state.get("user_name", "Khách"))
        phone = st.text_input("Số điện thoại", value="")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Đăng nhập", use_container_width=True):
                user_id = "user_" + str(abs(hash((name, phone))) % 10_000_000)
                st.session_state.user_id = user_id
                st.session_state.user_name = name or "Người chơi"
                execute(
                    "INSERT OR REPLACE INTO users(id,name,phone,role,created_at) VALUES (?,?,?,?,?)",
                    (user_id, st.session_state.user_name, phone, "player", now()),
                )
                notify(user_id, "Đăng nhập thành công", "Chào mừng bạn đến Badminton Vinh Ultra.", "system")
                st.success("Đã lưu hồ sơ")
        with col2:
            if st.button("Khách", use_container_width=True):
                st.session_state.user_id = "guest"
                st.session_state.user_name = "Khách"
                st.info("Đang dùng chế độ khách")
        st.toggle("⚡ Chế độ nhẹ/mobile", key="light_mode")
        st.caption("Dữ liệu bản demo lưu SQLite trên server/local.")

# -----------------------------
# BUSINESS LOGIC
# -----------------------------

def notify(user_id: str, title: str, body: str, kind: str = "info") -> None:
    execute(
        "INSERT INTO notifications VALUES (?,?,?,?,?,?,?)",
        (str(uuid.uuid4()), user_id, title, body, kind, 0, now()),
    )


def get_court(court_id: str) -> Optional[sqlite3.Row]:
    rows = q("SELECT * FROM courts WHERE id=?", (court_id,))
    return rows[0] if rows else None


def court_is_available(court_id: str, bdate: str, start_time: str, duration: int) -> bool:
    bookings = q(
        "SELECT * FROM bookings WHERE court_id=? AND booking_date=? AND status IN ('pending','confirmed')",
        (court_id, bdate),
    )
    new_start = datetime.strptime(start_time, "%H:%M")
    new_end = new_start + timedelta(hours=duration)
    for b in bookings:
        old_start = datetime.strptime(b["start_time"], "%H:%M")
        old_end = old_start + timedelta(hours=int(b["duration"]))
        if max(new_start, old_start) < min(new_end, old_end):
            return False
    return True


def create_booking(user_id: str, court_id: str, bdate: str, start_time: str, duration: int, players: int, note: str) -> Tuple[bool, str]:
    court = get_court(court_id)
    if not court:
        return False, "Không tìm thấy sân."
    if not court_is_available(court_id, bdate, start_time, duration):
        return False, "Khung giờ này đã có người đặt. Bạn chọn giờ khác nhé."
    total = int(court["price"]) * int(duration)
    booking_id = "book_" + str(uuid.uuid4())[:8]
    execute(
        "INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (booking_id, user_id, court_id, bdate, start_time, duration, players, note, "confirmed", total, now()),
    )
    notify(user_id, "Đặt sân thành công", f"Bạn đã đặt {court['name']} lúc {start_time} ngày {bdate}.", "booking")
    return True, booking_id


def vnd(n: Any) -> str:
    try:
        return f"{int(n):,}đ".replace(",", ".")
    except Exception:
        return str(n)

# -----------------------------
# PAGES
# -----------------------------

def page_home() -> None:
    hero("🏸 Badminton Vinh AI Automation Ultra", "Nền tảng cầu lông AI tự động hóa cho TP Vinh: đặt sân, mua bán, tìm kèo, HLV, giải đấu, hội viên, CRM, vận hành sân, marketing và gợi ý tăng trưởng không tốn API mặc định.")
    badminton_visual()
    courts = q("SELECT COUNT(*) c FROM courts WHERE status='active'")[0]["c"]
    products = q("SELECT COUNT(*) c FROM products WHERE status='available'")[0]["c"]
    bookings = q("SELECT COUNT(*) c FROM bookings")[0]["c"]
    users = q("SELECT COUNT(*) c FROM users")[0]["c"]
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Sân đang mở", courts, "TP Vinh")
    with c2: metric_card("Tin mua bán", products, "dụng cụ")
    with c3: metric_card("Lượt đặt sân", bookings, "trong app")
    with c4: metric_card("Người dùng", users, "hồ sơ")

    st.markdown("### 🚀 Chức năng chính")
    st.markdown('<div class="grid">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    features = [
        ("📅", "Đặt lịch sân", "Tìm sân theo khu vực, giá, giờ mở cửa và đặt lịch nhanh.", "Booking"),
        ("🛒", "Mua dụng cụ", "Vợt, giày, cầu, túi, phụ kiện cầu lông tại Vinh.", "Market"),
        ("➕", "Đăng bán", "Đăng tin bán đồ cầu lông với ảnh mô tả, giá, số điện thoại.", "Seller"),
        ("👥", "Tìm kèo", "Tìm người chơi cùng trình độ, khu vực, khung giờ.", "Community"),
    ]
    for i, f in enumerate(features):
        with cols[i]: card(*f)

    st.markdown("### 🧠 Gợi ý chuyên gia")
    st.info("Muốn app dùng thật tốt: hãy cập nhật danh sách sân thật tại TP Vinh, thêm giá giờ vàng/giờ thấp điểm, và bật nhắc lịch qua Zalo/Telegram hoặc email nếu dùng production.")


def page_courts() -> None:
    st.title("📅 Đặt lịch sân cầu lông")
    st.caption("Tìm sân ở TP Vinh, xem giá, tiện ích, đặt lịch nhanh.")
    col1, col2, col3 = st.columns(3)
    with col1:
        area = st.selectbox("Khu vực", ["Tất cả", "Trung tâm", "Lê Mao", "Quán Bàu", "Hưng Dũng", "Bến Thủy"])
    with col2:
        max_price = st.slider("Giá tối đa / giờ", 50000, 150000, 120000, 10000)
    with col3:
        min_rating = st.slider("Đánh giá tối thiểu", 3.0, 5.0, 4.0, 0.1)
    sql = "SELECT * FROM courts WHERE status='active' AND price<=? AND rating>=?"
    params: List[Any] = [max_price, min_rating]
    if area != "Tất cả":
        sql += " AND area=?"
        params.append(area)
    courts = q(sql + " ORDER BY rating DESC, price ASC", tuple(params))
    for court in courts:
        st.markdown(
            f"""
            <div class="court-card">
              <div class="pill green">⭐ {court['rating']}</div><div class="pill blue">{court['area']}</div>
              <h3>🏸 {court['name']}</h3>
              <div class="muted">📍 {court['address']} · ☎️ {court['phone']}</div>
              <div class="price">{vnd(court['price'])}/giờ</div>
              <div class="muted">🕒 {court['open_time']} - {court['close_time']}</div>
              <div style="margin-top:8px"><span class="pill yellow">{court['features']}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander(f"Đặt sân: {court['name']}"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                bdate = st.date_input("Ngày", value=date.today(), min_value=date.today(), key=f"date_{court['id']}")
            with c2:
                start = st.selectbox("Giờ bắt đầu", [f"{h:02d}:00" for h in range(5, 24)], key=f"start_{court['id']}")
            with c3:
                duration = st.selectbox("Số giờ", [1, 2, 3, 4], key=f"dur_{court['id']}")
            with c4:
                players = st.number_input("Số người", 1, 12, 4, key=f"players_{court['id']}")
            note = st.text_input("Ghi chú", placeholder="VD: cần thuê 2 vợt, chơi đôi nam...", key=f"note_{court['id']}")
            total = int(court["price"]) * int(duration)
            st.success(f"Tạm tính: {vnd(total)}")
            if st.button("✅ Xác nhận đặt sân", key=f"book_{court['id']}", use_container_width=True):
                ok, msg = create_booking(st.session_state.user_id, court["id"], str(bdate), start, int(duration), int(players), note)
                if ok:
                    st.balloons()
                    st.success(f"Đặt sân thành công. Mã lịch: {msg}")
                else:
                    st.error(msg)


def page_market() -> None:
    st.title("🛒 Chợ cầu lông TP Vinh")
    st.caption("Mua bán vợt, giày, cầu, túi và phụ kiện cầu lông.")
    col1, col2, col3 = st.columns(3)
    with col1:
        cat = st.selectbox("Danh mục", ["Tất cả", "Vợt", "Giày", "Cầu", "Phụ kiện", "Áo quần", "Khác"])
    with col2:
        condition = st.selectbox("Tình trạng", ["Tất cả", "Mới", "Mới 90%", "Đã dùng", "Cần thanh lý"])
    with col3:
        budget = st.slider("Ngân sách tối đa", 100000, 5000000, 2500000, 100000)
    sql = "SELECT * FROM products WHERE status='available' AND price<=?"
    params: List[Any] = [budget]
    if cat != "Tất cả":
        sql += " AND category=?"; params.append(cat)
    if condition != "Tất cả":
        sql += " AND condition=?"; params.append(condition)
    products = q(sql + " ORDER BY created_at DESC", tuple(params))
    for p in products:
        st.markdown(
            f"""
            <div class="product-card">
              <span class="pill green">{p['category']}</span><span class="pill blue">{p['condition']}</span><span class="pill yellow">{p['area']}</span>
              <h3>🛍️ {p['title']}</h3>
              <div class="price">{vnd(p['price'])}</div>
              <div class="muted">{p['description']}</div>
              <div class="muted">☎️ {p['phone']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🛒 Thêm vào giỏ", key=f"cart_{p['id']}", use_container_width=True):
                st.session_state.cart.append(p["id"])
                st.success("Đã thêm vào giỏ")
        with c2:
            if st.button("⭐ Lưu tin", key=f"fav_{p['id']}", use_container_width=True):
                execute("INSERT INTO favorites VALUES (?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, "product", p["id"], now()))
                st.success("Đã lưu tin")
        with c3:
            st.link_button("📞 Liên hệ", f"tel:{p['phone']}", use_container_width=True)


def page_sell() -> None:
    st.title("➕ Đăng bán dụng cụ cầu lông")
    st.caption("Đăng tin bán vợt, giày, cầu, phụ kiện. Bản demo lưu dữ liệu vào SQLite.")
    with st.form("sell_form", clear_on_submit=True):
        title = st.text_input("Tên sản phẩm", placeholder="VD: Vợt Yonex Astrox 77 Pro")
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Danh mục", ["Vợt", "Giày", "Cầu", "Phụ kiện", "Áo quần", "Khác"])
            condition = st.selectbox("Tình trạng", ["Mới", "Mới 90%", "Đã dùng", "Cần thanh lý"])
            area = st.selectbox("Khu vực", ["Trung tâm", "Lê Mao", "Quán Bàu", "Hưng Dũng", "Bến Thủy", "Khác"])
        with c2:
            price = st.number_input("Giá bán", 0, 100000000, 500000, 50000)
            phone = st.text_input("Số điện thoại liên hệ")
        description = st.text_area("Mô tả", placeholder="Tình trạng, lý do bán, phụ kiện kèm theo...")
        img = st.file_uploader("Ảnh sản phẩm (demo: chưa lưu ảnh lâu dài)", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("🚀 Đăng tin bán", use_container_width=True)
    if submitted:
        if not title or not phone:
            st.error("Bạn cần nhập tên sản phẩm và số điện thoại.")
        else:
            execute(
                "INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                ("prod_" + str(uuid.uuid4())[:8], st.session_state.user_id, title, category, condition, int(price), description, area, phone, "available", now()),
            )
            notify(st.session_state.user_id, "Đăng bán thành công", f"Tin {title} đã được đăng.", "market")
            st.success("Đã đăng tin bán thành công")


def page_my_schedule() -> None:
    st.title("🗓️ Lịch của tôi")
    bookings = q(
        """
        SELECT b.*, c.name court_name, c.area, c.address, c.phone
        FROM bookings b JOIN courts c ON b.court_id=c.id
        WHERE b.user_id=? ORDER BY b.booking_date DESC, b.start_time DESC
        """,
        (st.session_state.user_id,),
    )
    if not bookings:
        st.info("Bạn chưa có lịch đặt sân nào.")
    for b in bookings:
        st.markdown(
            f"""
            <div class="booking-card">
              <span class="pill green">{b['status']}</span><span class="pill blue">{b['booking_date']} · {b['start_time']}</span>
              <h3>🏸 {b['court_name']}</h3>
              <div class="muted">📍 {b['address']} · ☎️ {b['phone']}</div>
              <div class="muted">⏱️ {b['duration']} giờ · 👥 {b['players']} người · 💰 {vnd(b['total'])}</div>
              <div class="muted">📝 {b['note'] or 'Không có ghi chú'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("❌ Hủy lịch", key=f"cancel_{b['id']}", use_container_width=True):
                execute("UPDATE bookings SET status='cancelled' WHERE id=?", (b["id"],))
                st.warning("Đã hủy lịch. Tải lại trang để cập nhật.")
        with c2:
            if st.button("🔔 Nhắc tôi", key=f"remind_{b['id']}", use_container_width=True):
                notify(st.session_state.user_id, "Nhắc lịch cầu lông", f"Bạn có lịch tại {b['court_name']} lúc {b['start_time']} ngày {b['booking_date']}", "reminder")
                st.success("Đã tạo thông báo nhắc lịch trong app")


def page_find_players() -> None:
    st.title("👥 Tìm kèo / tìm người chơi")
    st.caption("Tạo bài tìm người đánh đôi, đánh đơn, giao lưu theo trình độ và khu vực.")
    with st.form("find_players"):
        level = st.selectbox("Trình độ", ["Mới chơi", "Trung bình", "Khá", "Nâng cao", "Giao lưu vui"])
        area = st.selectbox("Khu vực muốn chơi", ["Trung tâm", "Lê Mao", "Quán Bàu", "Hưng Dũng", "Bến Thủy", "Linh hoạt"])
        play_time = st.selectbox("Khung giờ", ["Sáng sớm", "Trưa", "Chiều", "Tối", "Cuối tuần"])
        message = st.text_area("Nội dung", value="Tìm bạn đánh cầu lông giao lưu tại TP Vinh. Ưu tiên vui vẻ, đúng giờ.")
        phone = st.text_input("Số điện thoại / Zalo")
        ok = st.form_submit_button("📣 Đăng tìm kèo", use_container_width=True)
    if ok:
        if phone:
            st.success("Đã tạo bài tìm kèo demo. Bạn có thể copy nội dung đăng lên nhóm Facebook/Zalo.")
            st.code(f"Tìm người chơi cầu lông {level} tại {area}, khung giờ {play_time}. {message} Liên hệ: {phone}")
        else:
            st.error("Bạn cần nhập số liên hệ.")
    st.markdown("### Gợi ý bài đăng hay")
    st.info("Ví dụ: 'Tối nay 19h sân Hưng Dũng thiếu 1 nam trình trung bình-khá, đánh vui, chia sân/cầu đều. Ai đi được inbox/Zalo nhé.'")


def page_notifications() -> None:
    st.title("🔔 Thông báo")
    rows = q("SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 50", (st.session_state.user_id,))
    if not rows:
        st.info("Chưa có thông báo.")
    for n in rows:
        cls = "status-ok" if n["kind"] in ["booking", "market"] else "status-warn" if n["kind"] == "reminder" else "status-ok"
        st.markdown(f"<div class='{cls}'><b>{n['title']}</b><br><span class='muted'>{n['body']} · {n['created_at']}</span></div>", unsafe_allow_html=True)
    if st.button("✅ Đánh dấu đã đọc", use_container_width=True):
        execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (st.session_state.user_id,))
        st.success("Đã đánh dấu đã đọc")


def page_admin() -> None:
    st.title("👑 Admin mini dashboard")
    st.caption("Quản lý nhanh dữ liệu app. Bản demo không có phân quyền mạnh, khi deploy thật nên thêm login admin riêng.")
    tables = ["users", "courts", "bookings", "products", "orders", "reviews", "notifications", "coaches", "tournaments", "memberships", "checkins"]
    cols = st.columns(4)
    for i, t in enumerate(tables):
        with cols[i % 4]:
            metric_card(t, q(f"SELECT COUNT(*) c FROM {t}")[0]["c"], "records")
    tab1, tab2, tab3 = st.tabs(["Sân", "Đơn đặt sân", "Sản phẩm"])
    with tab1:
        st.dataframe(pd.DataFrame([dict(r) for r in q("SELECT * FROM courts")]), use_container_width=True)
        with st.expander("➕ Thêm sân mới"):
            with st.form("add_court"):
                name = st.text_input("Tên sân")
                area = st.text_input("Khu vực")
                address = st.text_input("Địa chỉ")
                phone = st.text_input("SĐT")
                price = st.number_input("Giá/giờ", 0, 1000000, 80000, 10000)
                rating = st.slider("Rating", 1.0, 5.0, 4.5, 0.1)
                features = st.text_input("Tiện ích")
                if st.form_submit_button("Thêm sân"):
                    execute("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?)", ("court_"+str(uuid.uuid4())[:8], name, area, address, phone, int(price), float(rating), features, "05:00", "23:00", "active"))
                    st.success("Đã thêm sân")
    with tab2:
        st.dataframe(pd.DataFrame([dict(r) for r in q("SELECT * FROM bookings ORDER BY created_at DESC")]), use_container_width=True)
    with tab3:
        st.dataframe(pd.DataFrame([dict(r) for r in q("SELECT * FROM products ORDER BY created_at DESC")]), use_container_width=True)


def page_health() -> None:
    st.title("🩺 App Health Check")
    checks = []
    checks.append(("Database SQLite", DB_PATH.exists(), str(DB_PATH)))
    for table in ["users", "courts", "bookings", "products", "notifications", "coaches", "tournaments", "memberships", "checkins", "feedback"]:
        try:
            count = q(f"SELECT COUNT(*) c FROM {table}")[0]["c"]
            checks.append((f"Bảng {table}", True, f"{count} records"))
        except Exception as e:
            checks.append((f"Bảng {table}", False, str(e)))
    checks.append(("Streamlit config", Path(".streamlit/config.toml").exists(), ".streamlit/config.toml"))
    checks.append(("requirements.txt", Path("requirements.txt").exists(), "requirements.txt"))
    for name, ok, info in checks:
        cls = "status-ok" if ok else "status-bad"
        icon = "✅" if ok else "❌"
        st.markdown(f"<div class='{cls}'>{icon} <b>{name}</b><br><span class='muted'>{info}</span></div>", unsafe_allow_html=True)
    st.markdown("### Checklist deploy")
    st.checkbox("Upload đủ app.py, requirements.txt, .streamlit/config.toml")
    st.checkbox("Chạy được local bằng streamlit run app.py")
    st.checkbox("Test đặt sân, đăng bán, xem lịch, thông báo")
    st.checkbox("Test trên điện thoại màn hình nhỏ")


def page_settings() -> None:
    st.title("⚙️ Cài đặt & xuất dữ liệu")
    st.markdown("### Xuất dữ liệu JSON")
    data = {}
    for table in ["users", "courts", "bookings", "products", "orders", "reviews", "notifications", "favorites", "coaches", "tournaments", "tournament_registrations", "training_plans", "memberships", "checkins", "feedback"]:
        data[table] = [dict(r) for r in q(f"SELECT * FROM {table}")]
    st.download_button("⬇️ Tải backup JSON", json.dumps(data, ensure_ascii=False, indent=2), file_name="badminton_vinh_backup.json", mime="application/json", use_container_width=True)
    st.markdown("### Reset demo")
    st.warning("Chỉ dùng khi test. Việc này xóa database local.")
    if st.button("🗑️ Xóa database demo", use_container_width=True):
        if DB_PATH.exists():
            DB_PATH.unlink()
        st.success("Đã xóa. Hãy reload app để tạo lại dữ liệu mẫu.")



def page_coaches() -> None:
    st.title("🎓 HLV & lớp học")
    st.caption("Tìm huấn luyện viên cầu lông tại TP Vinh, đặt buổi học thử và nhận giáo án phù hợp trình độ.")
    level_filter = st.selectbox("Lọc trình độ", ["Tất cả", "Người mới", "Cơ bản", "Trung bình", "Khá", "Nâng cao"])
    rows = q("SELECT * FROM coaches ORDER BY rating DESC")
    for c in rows:
        if level_filter != "Tất cả" and level_filter.lower() not in c["level"].lower():
            continue
        st.markdown(f"""
        <div class='pro-panel'>
          <div class='pro-badge'>🎓 {c['level']}</div><div class='pro-badge'>⭐ {c['rating']}</div>
          <h3>{c['name']}</h3>
          <div class='muted'>📍 {c['area']} · ☎️ {c['phone']} · ⏱️ {c['available']}</div>
          <div class='muted'>{c['bio']}</div>
          <div class='price'>{vnd(c['price'])}/buổi</div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📞 Liên hệ HLV", key=f"call_coach_{c['id']}", use_container_width=True):
                notify(st.session_state.user_id, "Liên hệ HLV", f"Bạn quan tâm {c['name']}. SĐT: {c['phone']}", "coach")
                st.success(f"Số liên hệ: {c['phone']}")
        with col2:
            if st.button("🧪 Đặt buổi học thử", key=f"trial_{c['id']}", use_container_width=True):
                notify(st.session_state.user_id, "Đăng ký học thử", f"Bạn đã yêu cầu học thử với {c['name']}", "coach")
                st.success("Đã tạo yêu cầu học thử trong thông báo.")


def generate_training_plan(goal: str, level: str, days: int) -> List[str]:
    base = [
        "Khởi động 8-10 phút: cổ tay, vai, hông, gối, cổ chân.",
        "Bộ chân 6 điểm trên sân: 4 hiệp x 45 giây.",
        "Phát cầu thấp/cao: 50 quả, ưu tiên ổn định điểm rơi.",
        "Luyện đánh cầu qua lại ổn định: 10 phút.",
        "Thả lỏng và ghi lại 1 lỗi kỹ thuật cần sửa.",
    ]
    if "giảm cân" in goal.lower():
        base.insert(2, "Cardio cầu lông: shadow footwork 8 hiệp x 30 giây.")
    if "thi đấu" in goal.lower() or level in ["Khá", "Nâng cao"]:
        base += ["Bài chiến thuật đôi: giao cầu - bắt lưới - lùi đập.", "Set đấu mô phỏng 11 điểm, ghi lại lỗi tự đánh hỏng."]
    if days >= 4:
        base += ["Một buổi riêng cho sức mạnh: squat, plank, nhảy dây, cổ tay."]
    return base


def page_training() -> None:
    st.title("🏋️ Giáo án luyện tập")
    st.caption("Tạo lộ trình tập cầu lông cá nhân theo mục tiêu, trình độ và số buổi/tuần.")
    with st.form("training_plan_form"):
        goal = st.selectbox("Mục tiêu", ["Đánh vui khỏe", "Giảm cân", "Sửa kỹ thuật", "Thi đấu phong trào", "Nâng cao tốc độ"])
        level = st.selectbox("Trình độ hiện tại", ["Mới chơi", "Cơ bản", "Trung bình", "Khá", "Nâng cao"])
        days = st.slider("Số buổi mỗi tuần", 1, 6, 3)
        ok = st.form_submit_button("✨ Tạo giáo án", use_container_width=True)
    if ok:
        plan = generate_training_plan(goal, level, days)
        execute("INSERT INTO training_plans VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, goal, level, days, json.dumps(plan, ensure_ascii=False), now()))
        st.success("Đã tạo giáo án và lưu vào hồ sơ.")
        for i, item in enumerate(plan, 1):
            st.markdown(f"<div class='timeline-item'><b>Buổi/Bước {i}</b><br><span class='muted'>{item}</span></div>", unsafe_allow_html=True)
    st.markdown("### Giáo án đã lưu gần đây")
    rows = q("SELECT * FROM training_plans WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (st.session_state.user_id,))
    for r in rows:
        st.markdown(f"<div class='pro-panel'><b>{r['goal']} · {r['level']}</b><br><span class='muted'>{r['days_per_week']} buổi/tuần · {r['created_at']}</span></div>", unsafe_allow_html=True)
        for item in json.loads(r['plan_json']):
            st.write("• " + item)


def page_tournaments() -> None:
    st.title("🏆 Giải đấu & sự kiện")
    st.caption("Tạo và đăng ký giải giao lưu cầu lông tại TP Vinh.")
    rows = q("SELECT * FROM tournaments ORDER BY event_date ASC")
    for t in rows:
        st.markdown(f"""
        <div class='pro-panel'>
          <div class='pro-badge'>🏆 {t['level']}</div><div class='pro-badge'>📍 {t['area']}</div>
          <h3>{t['title']}</h3>
          <div class='muted'>📅 {t['event_date']} · Lệ phí: {vnd(t['fee'])} · Giải thưởng: {t['prize']}</div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Đăng ký tham gia"):
            partner = st.text_input("Tên đồng đội / để trống nếu chưa có", key=f"p_{t['id']}")
            phone = st.text_input("SĐT/Zalo", key=f"ph_{t['id']}")
            note = st.text_area("Ghi chú", key=f"note_{t['id']}")
            if st.button("✅ Đăng ký giải", key=f"reg_{t['id']}", use_container_width=True):
                if not phone:
                    st.error("Bạn cần nhập số liên hệ.")
                else:
                    execute("INSERT INTO tournament_registrations VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), t['id'], st.session_state.user_id, partner, phone, note, "pending", now()))
                    notify(st.session_state.user_id, "Đăng ký giải thành công", f"Bạn đã đăng ký {t['title']}", "tournament")
                    st.success("Đã đăng ký. Ban tổ chức sẽ liên hệ xác nhận.")
    with st.expander("➕ Tạo giải/sự kiện mới"):
        with st.form("new_tournament"):
            title = st.text_input("Tên giải")
            area = st.selectbox("Khu vực", ["Trung tâm", "Lê Mao", "Quán Bàu", "Hưng Dũng", "Bến Thủy"])
            event_date = st.date_input("Ngày tổ chức", value=date.today()+timedelta(days=10))
            level = st.selectbox("Trình độ", ["Giao lưu vui", "Mới chơi", "Trung bình", "Khá - Nâng cao"])
            fee = st.number_input("Lệ phí", 0, 1000000, 100000, 10000)
            prize = st.text_input("Giải thưởng", value="Cúp + huy chương + voucher sân")
            if st.form_submit_button("Tạo giải", use_container_width=True):
                execute("INSERT INTO tournaments VALUES (?,?,?,?,?,?,?,?,?)", ("tour_"+str(uuid.uuid4())[:8], title, area, event_date.isoformat(), level, int(fee), prize, "open", now()))
                st.success("Đã tạo giải/sự kiện.")


def page_membership() -> None:
    st.title("💎 Gói hội viên & thanh toán demo")
    st.caption("Quản lý gói chơi theo buổi/tháng. Thanh toán trong bản này là demo, phù hợp để triển khai MVP.")
    packages = [
        ("Gói 5 buổi", 5, 420000, "Phù hợp người chơi 1-2 buổi/tuần"),
        ("Gói 10 buổi", 10, 790000, "Tiết kiệm hơn, ưu tiên khung giờ đẹp"),
        ("Gói CLB tháng", 16, 1150000, "Cho nhóm chơi thường xuyên"),
    ]
    courts = q("SELECT * FROM courts WHERE status='active'")
    court = st.selectbox("Chọn sân áp dụng", courts, format_func=lambda r: r['name']) if courts else None
    cols = st.columns(3)
    for i, (name, sessions, price, desc) in enumerate(packages):
        with cols[i]:
            st.markdown(f"<div class='pro-panel'><h3>{name}</h3><div class='price'>{vnd(price)}</div><div class='muted'>{sessions} buổi · {desc}</div></div>", unsafe_allow_html=True)
            if st.button("Mua gói", key=f"pkg_{i}", use_container_width=True):
                if not court:
                    st.error("Chưa có sân.")
                else:
                    execute("INSERT INTO memberships VALUES (?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, name, court['id'], sessions, 0, price, "active", now()))
                    notify(st.session_state.user_id, "Mua gói thành công", f"Bạn đã mua {name} tại {court['name']}", "membership")
                    st.success("Đã kích hoạt gói demo.")
    st.markdown("### Gói của tôi")
    rows = q("SELECT m.*, c.name court_name FROM memberships m LEFT JOIN courts c ON c.id=m.court_id WHERE m.user_id=? ORDER BY m.created_at DESC", (st.session_state.user_id,))
    for m in rows:
        remain = int(m['sessions']) - int(m['used_sessions'])
        st.markdown(f"<div class='booking-card'><b>{m['package_name']}</b><br><span class='muted'>{m['court_name']} · Còn {remain}/{m['sessions']} buổi · {m['status']}</span></div>", unsafe_allow_html=True)


def page_checkin() -> None:
    st.title("✅ Check-in sân & điểm phong độ")
    st.caption("Check-in sau khi chơi để lưu lịch sử, đánh giá phong độ và tạo thói quen tập đều.")
    bookings = q("SELECT b.*, c.name court_name FROM bookings b LEFT JOIN courts c ON c.id=b.court_id WHERE b.user_id=? AND b.status='confirmed' ORDER BY b.booking_date DESC LIMIT 20", (st.session_state.user_id,))
    if not bookings:
        st.info("Bạn chưa có lịch đặt sân để check-in.")
        return
    b = st.selectbox("Chọn lịch", bookings, format_func=lambda r: f"{r['booking_date']} {r['start_time']} · {r['court_name']}")
    note = st.text_area("Ghi chú buổi chơi", value="Hôm nay đánh ổn, cần cải thiện bộ chân và phát cầu.")
    if st.button("✅ Check-in buổi chơi", use_container_width=True):
        execute("INSERT INTO checkins VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, b['id'], b['court_id'], note, now()))
        notify(st.session_state.user_id, "Đã check-in", f"Bạn đã check-in tại {b['court_name']}", "checkin")
        st.success("Đã lưu check-in.")
    total = q("SELECT COUNT(*) c FROM checkins WHERE user_id=?", (st.session_state.user_id,))[0]['c']
    metric_card("Tổng số lần check-in", total, "buổi chơi đã lưu")


def page_pro_analytics() -> None:
    st.title("📊 Báo cáo chuyên nghiệp")
    st.caption("Báo cáo nhanh cho người chơi, chủ sân hoặc admin vận hành.")
    total_rev = q("SELECT COALESCE(SUM(total),0) s FROM bookings WHERE status='confirmed'")[0]['s']
    total_bookings = q("SELECT COUNT(*) c FROM bookings WHERE status='confirmed'")[0]['c']
    total_products = q("SELECT COUNT(*) c FROM products WHERE status='available'")[0]['c']
    total_checkins = q("SELECT COUNT(*) c FROM checkins")[0]['c']
    cols = st.columns(4)
    with cols[0]: metric_card("Doanh thu sân demo", vnd(total_rev), "confirmed")
    with cols[1]: metric_card("Lịch đã xác nhận", total_bookings, "booking")
    with cols[2]: metric_card("Tin đang bán", total_products, "market")
    with cols[3]: metric_card("Check-in", total_checkins, "buổi")
    st.markdown("### Top sân theo lịch đặt")
    rows = q("SELECT c.name, COUNT(b.id) bookings, COALESCE(SUM(b.total),0) revenue FROM courts c LEFT JOIN bookings b ON b.court_id=c.id AND b.status='confirmed' GROUP BY c.id ORDER BY bookings DESC")
    st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)
    st.markdown("### Gợi ý vận hành")
    st.markdown("<div class='status-ok'>✅ Khung giờ đẹp nên mở gói hội viên 10 buổi để tăng giữ chân khách.</div>", unsafe_allow_html=True)
    st.markdown("<div class='status-warn'>⚠️ Nếu sân ít lịch, nên tạo combo: đặt sân + thuê vợt + ống cầu.</div>", unsafe_allow_html=True)
    st.markdown("<div class='status-ok'>✅ Khuyến khích check-in để tạo cộng đồng và tăng quay lại.</div>", unsafe_allow_html=True)


def page_public_safety() -> None:
    st.title("🛡️ Điều khoản, an toàn & vận hành")
    st.markdown("""
    <div class='pro-panel'>
    <h3>Điều khoản sử dụng bản demo</h3>
    <p class='muted'>App hỗ trợ kết nối cộng đồng cầu lông TP Vinh. Thông tin sân, giá, HLV và sản phẩm trong bản mẫu cần được xác minh lại trước khi public thật.</p>
    <ul>
      <li>Không đăng bán hàng giả, hàng cấm hoặc thông tin sai sự thật.</li>
      <li>Người mua và người bán tự xác minh sản phẩm trước khi giao dịch.</li>
      <li>Đặt sân cần xác nhận lại với chủ sân nếu dùng ngoài bản demo.</li>
      <li>Số điện thoại cá nhân cần được người dùng đồng ý trước khi công khai.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    with st.form("feedback_form"):
        category = st.selectbox("Loại góp ý/lỗi", ["Lỗi app", "Sai thông tin sân", "Sản phẩm không phù hợp", "Gợi ý tính năng", "Khác"])
        message = st.text_area("Nội dung")
        if st.form_submit_button("📩 Gửi góp ý", use_container_width=True):
            execute("INSERT INTO feedback VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, category, message, "new", now()))
            st.success("Đã ghi nhận góp ý.")


def page_pro_max_center() -> None:
    st.title("🚀 Pro Max Center")
    st.caption("Trung tâm nâng cấp chuyên nghiệp: đặt sân nhanh, gợi ý combo, điểm thưởng, vận hành và tăng trưởng cộng đồng.")
    cols = st.columns(4)
    metrics = [
        ("Sân", q("SELECT COUNT(*) c FROM courts WHERE status='active'")[0]['c'], "đang mở"),
        ("Lịch xác nhận", q("SELECT COUNT(*) c FROM bookings WHERE status='confirmed'")[0]['c'], "booking"),
        ("Sản phẩm", q("SELECT COUNT(*) c FROM products WHERE status='available'")[0]['c'], "đang bán"),
        ("Hội viên", q("SELECT COUNT(*) c FROM memberships WHERE status='active'")[0]['c'], "gói"),
    ]
    for col, (t, v, c) in zip(cols, metrics):
        with col:
            metric_card(t, v, c)
    st.markdown("### 🎯 Gợi ý tăng trưởng")
    st.markdown("<div class='deal-card'><b>Combo giờ thấp điểm:</b> đặt sân + thuê vợt + ống cầu giảm 10–15% để lấp lịch trống.</div>", unsafe_allow_html=True)
    st.markdown("<div class='deal-card'><b>Nhóm cố định:</b> tạo gói CLB tháng cho nhóm chơi thứ 3/5/7 để tăng doanh thu ổn định.</div>", unsafe_allow_html=True)
    st.markdown("<div class='deal-card'><b>Cộng đồng:</b> khuyến khích check-in, review sân, tìm kèo theo trình độ để người chơi quay lại.</div>", unsafe_allow_html=True)
    st.markdown("### 🧭 Lộ trình vận hành chuyên nghiệp")
    for i, step in enumerate(["Chuẩn hóa dữ liệu sân thật", "Bật xác nhận chủ sân", "Tạo gói hội viên", "Chạy ưu đãi giờ thấp điểm", "Mở giải giao lưu cuối tuần", "Theo dõi báo cáo mỗi tuần"], 1):
        st.markdown(f"<div class='timeline-item'><b>Bước {i}:</b> {step}</div>", unsafe_allow_html=True)


def page_owner_portal() -> None:
    st.title("🏟️ Chủ sân Portal")
    st.caption("Khu vận hành dành cho chủ sân: lịch đặt, ghi chú, trạng thái sân, khung giờ nóng/lạnh.")
    courts = q("SELECT * FROM courts ORDER BY name")
    if not courts:
        st.warning("Chưa có sân.")
        return
    court = st.selectbox("Chọn sân quản lý", courts, format_func=lambda r: r['name'])
    bookings = q("SELECT * FROM bookings WHERE court_id=? ORDER BY booking_date DESC,start_time DESC", (court['id'],))
    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Tổng lịch", len(bookings), "booking")
    with col2: metric_card("Doanh thu", vnd(sum(int(b['total']) for b in bookings if b['status']=='confirmed')), "confirmed")
    with col3: metric_card("Rating", court['rating'], "sao")
    st.markdown("### 🔥 Heatmap khung giờ demo")
    hours=["05:00","06:00","07:00","17:00","18:00","19:00","20:00","21:00"]
    cols=st.columns(4)
    for i,h in enumerate(hours):
        cnt=sum(1 for b in bookings if b['start_time']==h)
        cls='heat-hot' if cnt>=3 else 'heat-mid' if cnt>=1 else 'heat-low'
        with cols[i%4]:
            st.markdown(f"<div class='heat-cell {cls}'><b>{h}</b><br>{cnt} lịch</div>", unsafe_allow_html=True)
    st.markdown("### 📝 Ghi chú vận hành")
    with st.form("owner_note"):
        title=st.text_input("Tiêu đề", value="Kiểm tra đèn sân / lưới / thảm")
        note=st.text_area("Ghi chú")
        priority=st.selectbox("Mức ưu tiên", ["Thấp","Vừa","Cao"])
        if st.form_submit_button("Lưu ghi chú", use_container_width=True):
            execute("INSERT INTO court_owner_notes VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), court['id'], title, note, priority, now()))
            st.success("Đã lưu ghi chú vận hành.")
    for n in q("SELECT * FROM court_owner_notes WHERE court_id=? ORDER BY created_at DESC LIMIT 10", (court['id'],)):
        st.markdown(f"<div class='crm-row'><span class='owner-chip'>{n['priority']}</span><b>{n['title']}</b><br><span class='muted'>{n['note']} · {n['created_at']}</span></div>", unsafe_allow_html=True)


def page_smart_booking() -> None:
    st.title("⚡ Đặt sân thông minh")
    st.caption("Gợi ý sân theo ngân sách, khu vực, giờ chơi và số người. Có combo thuê vợt/cầu demo.")
    c1,c2,c3=st.columns(3)
    with c1: area=st.selectbox("Khu vực", ["Tất cả","Trung tâm","Lê Mao","Quán Bàu","Hưng Dũng","Bến Thủy"])
    with c2: budget=st.slider("Ngân sách/giờ", 50000, 150000, 90000, 10000)
    with c3: start=st.selectbox("Giờ chơi", [f"{h:02d}:00" for h in range(5,24)])
    bdate=st.date_input("Ngày chơi", value=date.today())
    players=st.slider("Số người", 2, 16, 4)
    courts=q("SELECT * FROM courts WHERE status='active' ORDER BY rating DESC, price ASC")
    if area!='Tất cả': courts=[c for c in courts if c['area']==area]
    courts=[c for c in courts if int(c['price'])<=budget]
    st.markdown("### Gợi ý phù hợp")
    for court in courts[:5]:
        available=court_is_available(court['id'], bdate.isoformat(), start, 1)
        st.markdown(f"<div class='court-card'><h3>{court['name']}</h3><div class='muted'>📍 {court['area']} · ⭐ {court['rating']} · {court['features']}</div><div class='price'>{vnd(court['price'])}/giờ</div></div>", unsafe_allow_html=True)
        combo=st.checkbox(f"Thêm combo thuê vợt + ống cầu cho {court['name']}", key=f"combo_{court['id']}")
        extra=70000 if combo else 0
        if available:
            if st.button(f"Đặt nhanh {start} · Tổng {vnd(int(court['price'])+extra)}", key=f"quick_{court['id']}", use_container_width=True):
                ok,bid=create_booking(st.session_state.user_id, court['id'], bdate.isoformat(), start, 1, players, "Đặt sân thông minh" + (" + combo" if combo else ""))
                if combo:
                    execute("INSERT INTO equipment_rentals VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, court['id'], "Combo vợt + cầu", extra, "reserved", now()))
                st.success("Đã đặt nhanh. Mã lịch: "+bid if ok else bid)
        else:
            st.warning("Khung giờ này đã kín. Hãy chọn giờ khác.")


def page_wallet_loyalty() -> None:
    st.title("💰 Ví điểm & Loyalty")
    st.caption("Demo ví điểm khách hàng: tích điểm từ đặt sân, mua gói, check-in và review.")
    rows=q("SELECT * FROM wallet_transactions WHERE user_id=? ORDER BY created_at DESC", (st.session_state.user_id,))
    points=sum(int(r['points']) for r in rows)
    money=sum(int(r['amount']) for r in rows)
    c1,c2,c3=st.columns(3)
    with c1: metric_card("Điểm hiện có", points, "points")
    with c2: metric_card("Ví demo", vnd(money), "không phải thanh toán thật")
    with c3: metric_card("Cấp độ", "Gold" if points>=500 else "Silver" if points>=200 else "Member", "loyalty")
    st.markdown("### Nhận điểm nhanh")
    cols=st.columns(3)
    for col,(name,pts) in zip(cols,[("Check-in hôm nay", 30), ("Review sân", 50), ("Chia sẻ app", 80)]):
        with col:
            if st.button(f"+{pts} điểm · {name}", use_container_width=True):
                execute("INSERT INTO wallet_transactions VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, 0, pts, "earn", name, now()))
                st.success(f"Đã cộng {pts} điểm.")
    st.markdown("### Voucher đang có")
    for cp in q("SELECT * FROM coupons WHERE status='active'"):
        st.markdown(f"<div class='deal-card'><b>{cp['code']}</b> · {cp['title']}<br><span class='muted'>Giảm {vnd(cp['discount'])} cho đơn từ {vnd(cp['min_total'])}</span></div>", unsafe_allow_html=True)
    if rows:
        st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)


def page_crm_customers() -> None:
    st.title("🧑‍💼 CRM khách hàng")
    st.caption("Mini CRM cho chủ sân/admin: xem khách đặt nhiều, khách mới, khách cần chăm sóc.")
    rows=q("""SELECT u.id,u.name,u.phone,COUNT(b.id) bookings,COALESCE(SUM(b.total),0) spend,MAX(b.created_at) last_booking
              FROM users u LEFT JOIN bookings b ON b.user_id=u.id GROUP BY u.id ORDER BY spend DESC, bookings DESC""")
    if not rows:
        st.info("Chưa có khách hàng.")
        return
    df=pd.DataFrame([dict(r) for r in rows])
    st.dataframe(df, use_container_width=True)
    csv=df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("⬇️ Tải CRM CSV", csv, "badminton_vinh_crm.csv", "text/csv", use_container_width=True)
    st.markdown("### Gợi ý chăm sóc")
    for r in rows[:8]:
        tag="VIP" if int(r['spend'] or 0)>500000 else "Mới" if int(r['bookings'] or 0)<=1 else "Tiềm năng"
        st.markdown(f"<div class='crm-row'><span class='owner-chip'>{tag}</span><b>{r['name']}</b> · {r['phone'] or 'chưa có SĐT'}<br><span class='muted'>{r['bookings']} lịch · {vnd(r['spend'])} · lần gần nhất {r['last_booking'] or 'chưa có'}</span></div>", unsafe_allow_html=True)


def page_qr_checkin() -> None:
    st.title("🔳 QR Check-in Demo")
    st.caption("Tạo mã check-in demo để người chơi đưa cho chủ sân/CLB quét hoặc nhập mã.")
    code=f"BDM-{st.session_state.user_id[-6:].upper()}-{datetime.now().strftime('%H%M')}"
    st.markdown(f"<div class='qr-box'>🏸<br>{code}<br><span style='font-size:.8rem'>Mã check-in demo</span></div>", unsafe_allow_html=True)
    courts=q("SELECT * FROM courts WHERE status='active'")
    court=st.selectbox("Check-in tại sân", courts, format_func=lambda r: r['name']) if courts else None
    note=st.text_input("Ghi chú", value="Check-in QR demo")
    if st.button("✅ Xác nhận check-in QR", use_container_width=True):
        if court:
            execute("INSERT INTO checkins VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, code, court['id'], note, now()))
            execute("INSERT INTO wallet_transactions VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), st.session_state.user_id, 0, 20, "earn", "QR check-in", now()))
            st.success("Đã check-in và cộng 20 điểm.")
        else: st.error("Chưa có sân.")


def page_export_reports() -> None:
    st.title("📤 Xuất báo cáo & backup nâng cao")
    st.caption("Tải CSV/JSON để chủ sân hoặc admin lưu trữ, phân tích, gửi đối tác.")
    tables=["courts","bookings","products","users","memberships","checkins","tournaments","feedback","wallet_transactions"]
    selected=st.multiselect("Chọn bảng", tables, default=["bookings","courts","products"])
    for table in selected:
        rows=q(f"SELECT * FROM {table}")
        df=pd.DataFrame([dict(r) for r in rows])
        st.markdown(f"### {table} · {len(df)} dòng")
        st.dataframe(df.head(50), use_container_width=True)
        st.download_button(f"⬇️ Tải {table}.csv", df.to_csv(index=False).encode('utf-8-sig'), f"{table}.csv", "text/csv", key=f"csv_{table}", use_container_width=True)
    backup={t:[dict(r) for r in q(f"SELECT * FROM {t}")] for t in selected}
    st.download_button("⬇️ Tải backup JSON đã chọn", json.dumps(backup, ensure_ascii=False, indent=2).encode('utf-8'), "badminton_vinh_backup_selected.json", "application/json", use_container_width=True)


def page_ai_assistant_rules() -> None:
    st.title("🤖 Trợ lý vận hành offline")
    st.caption("Gợi ý thông minh không tốn API, dựa trên dữ liệu app và quy tắc vận hành cầu lông.")
    question=st.text_area("Bạn muốn hỏi gì?", placeholder="Ví dụ: Làm sao tăng lịch đặt sân buổi trưa? Nên tạo gói hội viên thế nào?")
    if st.button("Tạo gợi ý", use_container_width=True):
        text=(question or '').lower()
        if 'trưa' in text or 'thấp điểm' in text:
            ans="Tạo combo giờ thấp điểm: giảm 10–15%, tặng thuê vợt hoặc 1 chai nước. Đẩy thông báo cho nhóm sinh viên/văn phòng gần sân."
        elif 'hội viên' in text or 'gói' in text:
            ans="Nên có 3 gói: 5 buổi cho người mới, 10 buổi tiết kiệm, CLB tháng cho nhóm cố định. Cho phép giữ khung giờ đẹp nếu thanh toán trước."
        elif 'người chơi' in text or 'tìm kèo' in text:
            ans="Ghép người theo trình độ, khu vực và khung giờ. Khuyến khích tạo kèo công khai và có đánh giá sau buổi chơi."
        elif 'doanh thu' in text:
            ans="Tập trung tăng tỷ lệ lấp lịch, bán combo thuê vợt/cầu, mở lớp HLV nhập môn và giải giao lưu cuối tuần."
        else:
            ans="Ưu tiên 3 việc: dữ liệu sân thật chính xác, đặt lịch không trùng, chăm sóc khách quay lại bằng điểm thưởng/check-in/voucher."
        st.success(ans)


# -----------------------------
# AI AUTOMATION PRO SUITE
# -----------------------------

def _safe_count(table: str, where: str = "", params: Tuple = ()) -> int:
    try:
        sql = f"SELECT COUNT(*) AS c FROM {table} " + where
        rows = q(sql, params)
        return int(rows[0]["c"]) if rows else 0
    except Exception:
        return 0


def _sum_table(table: str, col: str, where: str = "", params: Tuple = ()) -> int:
    try:
        sql = f"SELECT COALESCE(SUM({col}),0) AS s FROM {table} " + where
        rows = q(sql, params)
        return int(rows[0]["s"] or 0) if rows else 0
    except Exception:
        return 0


def ai_collect_signals() -> Dict[str, Any]:
    today = date.today().isoformat()
    next_week = (date.today() + timedelta(days=7)).isoformat()
    bookings = q("SELECT b.*, c.name court_name, c.area, c.price FROM bookings b LEFT JOIN courts c ON c.id=b.court_id")
    courts = q("SELECT * FROM courts")
    products = q("SELECT * FROM products")
    users = q("SELECT * FROM users")
    feedbacks = q("SELECT * FROM feedback WHERE status!='done' ORDER BY created_at DESC")
    upcoming = [b for b in bookings if str(b['booking_date']) >= today and str(b['booking_date']) <= next_week]
    revenue = sum(int(b['total'] or 0) for b in bookings)
    avg_price = round(sum(int(c['price'] or 0) for c in courts) / max(1, len(courts))) if courts else 0
    hot_hours = {}
    for b in bookings:
        hot_hours[b['start_time']] = hot_hours.get(b['start_time'], 0) + 1
    top_hour = max(hot_hours, key=hot_hours.get) if hot_hours else "Chưa có dữ liệu"
    return {
        "courts": len(courts), "products": len(products), "users": len(users), "bookings": len(bookings),
        "upcoming": len(upcoming), "revenue": revenue, "avg_price": avg_price, "top_hour": top_hour,
        "feedback_open": len(feedbacks), "court_rows": courts, "booking_rows": bookings, "product_rows": products,
    }


def ai_score_business(signals: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 45
    reasons = []
    if signals['courts'] >= 5: score += 10; reasons.append("Danh sách sân đã đủ tối thiểu để người dùng lựa chọn.")
    else: reasons.append("Nên bổ sung thêm sân thật ở TP Vinh.")
    if signals['bookings'] >= 5: score += 10; reasons.append("Đã có dữ liệu đặt sân để phân tích.")
    else: reasons.append("Cần tăng dữ liệu booking thật để AI gợi ý chính xác hơn.")
    if signals['products'] >= 5: score += 8; reasons.append("Marketplace có sản phẩm để tạo giao dịch phụ.")
    else: reasons.append("Chợ dụng cụ còn ít sản phẩm, nên khuyến khích người dùng đăng bán.")
    if signals['feedback_open'] == 0: score += 7; reasons.append("Không có góp ý/lỗi đang mở.")
    else: reasons.append(f"Có {signals['feedback_open']} góp ý/lỗi cần xử lý.")
    if signals['revenue'] > 0: score += 10; reasons.append("Đã có doanh thu demo từ lịch đặt.")
    return min(100, score), reasons


def ai_generate_recommendations(signals: Dict[str, Any]) -> List[Dict[str, str]]:
    recs = []
    if signals['bookings'] < 5:
        recs.append({"title":"Tăng booking đầu tiên", "priority":"Cao", "category":"Growth", "detail":"Tạo voucher NEWBIE20, ghim nút đặt sân nhanh trên trang chính và chạy bài Facebook cho nhóm sinh viên/văn phòng ở TP Vinh."})
    if signals['products'] < 8:
        recs.append({"title":"Kích hoạt chợ dụng cụ", "priority":"Vừa", "category":"Marketplace", "detail":"Tạo chương trình đăng bán miễn phí 7 ngày, gợi ý danh mục vợt/giày/cầu và kiểm duyệt tin có số điện thoại rõ ràng."})
    if signals['top_hour'] != "Chưa có dữ liệu":
        recs.append({"title":"Tối ưu khung giờ hot", "priority":"Cao", "category":"Pricing", "detail":f"Khung giờ đang nổi bật là {signals['top_hour']}. Có thể giữ giá giờ hot, giảm nhẹ giờ thấp điểm và bán combo vợt + cầu."})
    else:
        recs.append({"title":"Thu thập dữ liệu giờ chơi", "priority":"Vừa", "category":"Data", "detail":"Khuyến khích người dùng đặt lịch trong app thay vì gọi điện để AI có đủ dữ liệu phân tích khung giờ."})
    if signals['feedback_open'] > 0:
        recs.append({"title":"Xử lý góp ý/lỗi", "priority":"Cao", "category":"Support", "detail":f"Có {signals['feedback_open']} góp ý/lỗi đang mở. Ưu tiên sửa thông tin sân sai, lỗi đặt lịch và lỗi hiển thị mobile."})
    recs.append({"title":"Tạo gói hội viên", "priority":"Vừa", "category":"Membership", "detail":"Gói 5 buổi cho người mới, gói 10 buổi tiết kiệm, gói CLB tháng giữ khung giờ cố định cho nhóm chơi đều."})
    recs.append({"title":"Tăng giữ chân khách", "priority":"Vừa", "category":"Retention", "detail":"Cộng điểm sau check-in, tặng voucher khi review sân, nhắc lịch chơi tuần sau cho khách đã từng đặt."})
    return recs


def ai_auto_create_tasks(recs: List[Dict[str, str]]) -> int:
    created = 0
    existing = {r['title'] for r in q("SELECT title FROM ai_automation_tasks WHERE status!='done'")}
    for rec in recs:
        if rec['title'] not in existing:
            execute("INSERT INTO ai_automation_tasks VALUES (?,?,?,?,?,?,?,?)", (
                str(uuid.uuid4()), rec['title'], rec['category'], rec['priority'], 'todo',
                (date.today()+timedelta(days=3)).isoformat(), rec['detail'], now()
            ))
            created += 1
    execute("INSERT INTO ai_logs VALUES (?,?,?,?)", (str(uuid.uuid4()), 'auto_tasks', f'Tạo {created} task AI tự động', now()))
    return created


def ai_campaign_templates(signals: Dict[str, Any]) -> List[Dict[str, str]]:
    return [
        {"title":"Chiến dịch Facebook cuối tuần", "target":"Người chơi cầu lông TP Vinh", "channel":"Facebook", "message":"🏸 Cuối tuần này đặt sân nhanh tại Badminton Vinh AI Automation Ultra. Có tìm kèo, thuê vợt, combo cầu và check-in nhận điểm."},
        {"title":"Chăm sóc khách đã đặt sân", "target":"Khách từng booking", "channel":"Zalo/SMS demo", "message":"Bạn có muốn giữ khung giờ chơi tuần này không? Đặt lại nhanh và nhận điểm loyalty trong app."},
        {"title":"Kích hoạt marketplace", "target":"Người có vợt/giày/cầu muốn thanh lý", "channel":"Facebook Group", "message":"Đăng bán dụng cụ cầu lông ở TP Vinh miễn phí. Người mua xem được khu vực, giá, tình trạng và liên hệ nhanh."},
        {"title":"Gói nhập môn HLV", "target":"Người mới chơi", "channel":"App Notification", "message":"Bạn mới chơi cầu lông? Thử buổi HLV nhập môn để sửa grip, bộ chân và phát cầu trong 60 phút."},
    ]


def ai_answer(question: str, signals: Dict[str, Any]) -> str:
    t = (question or '').lower()
    if any(x in t for x in ['doanh thu','tăng tiền','lợi nhuận']):
        return "Ưu tiên 3 đòn bẩy: tăng tỷ lệ lấp sân giờ thấp điểm, bán combo thuê vợt/cầu, và tạo gói hội viên giữ khung giờ cố định. Đừng tăng giá đại trà ngay; hãy tăng giá giờ hot và ưu đãi giờ trống."
    if any(x in t for x in ['marketing','facebook','quảng cáo','thu hút']):
        return "Nên chạy nội dung ngắn: video 15–30 giây, nhấn vào đặt sân nhanh, tìm kèo, voucher người mới và bản đồ sân ở TP Vinh. Bài đăng phải có CTA rõ: 'Nhắn tin đặt sân' hoặc 'Mở app đặt lịch'."
    if any(x in t for x in ['trùng lịch','đặt sân','booking']):
        return "Luôn kiểm tra trùng lịch theo court_id + ngày + khoảng giờ. Sau khi đặt thành công, gửi thông báo trong app và hiển thị lịch của tôi để người dùng không đặt nhầm."
    if any(x in t for x in ['hlv','lớp học','tập luyện']):
        return "Nên chia HLV thành 3 nhóm: người mới, trung bình, nâng cao. Gói dễ bán nhất là buổi học thử 60 phút + giáo án 4 tuần."
    if any(x in t for x in ['khách','crm','giữ chân']):
        return "Phân nhóm khách: mới, tiềm năng, VIP, sắp rời bỏ. Khách VIP nên được giữ khung giờ đẹp; khách mới nên nhận voucher lần 2; khách lâu chưa quay lại nên nhận lời mời chơi cuối tuần."
    return f"Tình trạng hiện tại: {signals['courts']} sân, {signals['bookings']} lịch đặt, {signals['products']} sản phẩm, doanh thu demo {vnd(signals['revenue'])}. Gợi ý chung: làm dữ liệu sân thật chính xác, đặt lịch không trùng, mobile dễ dùng và chăm sóc khách quay lại bằng điểm/voucher."


def page_ai_automation_center() -> None:
    st.title("🤖 AI Automation Center")
    st.caption("AI tự động hóa toàn diện, mặc định không tốn API: phân tích dữ liệu, gợi ý vận hành, tạo task, marketing, pricing, CRM và checklist tăng trưởng.")
    signals = ai_collect_signals()
    score, reasons = ai_score_business(signals)
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("AI Business Score", f"{score}/100", "độ sẵn sàng vận hành")
    with c2: metric_card("Booking", signals['bookings'], "lịch đặt")
    with c3: metric_card("Doanh thu demo", vnd(signals['revenue']), "từ booking")
    with c4: metric_card("Giờ nổi bật", signals['top_hour'], "theo dữ liệu")
    st.markdown("### 🧠 Chẩn đoán nhanh")
    for r in reasons:
        st.markdown(f"<div class='status-ok'>✅ {r}</div>", unsafe_allow_html=True)
    st.markdown("### ⚡ Gợi ý tự động")
    recs = ai_generate_recommendations(signals)
    for rec in recs:
        color = 'red' if rec['priority']=='Cao' else 'yellow' if rec['priority']=='Vừa' else 'blue'
        st.markdown(f"<div class='pro-panel'><span class='pill {color}'>{rec['priority']}</span><span class='pill blue'>{rec['category']}</span><h3>{rec['title']}</h3><div class='muted'>{rec['detail']}</div></div>", unsafe_allow_html=True)
    if st.button("✅ AI tự tạo task vận hành từ các gợi ý", use_container_width=True):
        created = ai_auto_create_tasks(recs)
        st.success(f"Đã tạo {created} task mới cho đội vận hành.")


def page_ai_task_manager() -> None:
    st.title("✅ AI Task Manager")
    st.caption("Quản lý việc AI tự tạo: marketing, vận hành sân, chăm sóc khách, marketplace, hội viên.")
    with st.form("manual_ai_task"):
        c1,c2,c3=st.columns(3)
        with c1: title=st.text_input("Tên task")
        with c2: category=st.selectbox("Nhóm", ["Growth","Support","Pricing","CRM","Marketplace","Maintenance","Membership","Data"])
        with c3: priority=st.selectbox("Ưu tiên", ["Cao","Vừa","Thấp"])
        detail=st.text_area("Chi tiết")
        due=st.date_input("Hạn xử lý", value=date.today()+timedelta(days=3))
        if st.form_submit_button("Thêm task", use_container_width=True):
            execute("INSERT INTO ai_automation_tasks VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), title or 'Task mới', category, priority, 'todo', due.isoformat(), detail, now()))
            st.success("Đã thêm task.")
    rows=q("SELECT * FROM ai_automation_tasks ORDER BY CASE priority WHEN 'Cao' THEN 1 WHEN 'Vừa' THEN 2 ELSE 3 END, due_date ASC")
    for r in rows:
        st.markdown(f"<div class='crm-row'><span class='owner-chip'>{r['priority']}</span><span class='pill blue'>{r['category']}</span><b>{r['title']}</b><br><span class='muted'>Hạn: {r['due_date']} · Trạng thái: {r['status']}<br>{r['detail']}</span></div>", unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1:
            if st.button("Đang làm", key=f"doing_{r['id']}", use_container_width=True):
                execute("UPDATE ai_automation_tasks SET status='doing' WHERE id=?", (r['id'],)); st.rerun()
        with c2:
            if st.button("Hoàn tất", key=f"done_{r['id']}", use_container_width=True):
                execute("UPDATE ai_automation_tasks SET status='done' WHERE id=?", (r['id'],)); st.rerun()
        with c3:
            if st.button("Xóa", key=f"del_{r['id']}", use_container_width=True):
                execute("DELETE FROM ai_automation_tasks WHERE id=?", (r['id'],)); st.rerun()


def page_ai_marketing_auto() -> None:
    st.title("📣 AI Marketing Automation")
    st.caption("Tự tạo chiến dịch quảng cáo, caption, thông báo chăm sóc khách và gợi ý nội dung Facebook/Zalo.")
    signals=ai_collect_signals()
    templates=ai_campaign_templates(signals)
    for t in templates:
        st.markdown(f"<div class='deal-card'><span class='pill purple'>{t['channel']}</span><span class='pill blue'>{t['target']}</span><h3>{t['title']}</h3><div>{t['message']}</div></div>", unsafe_allow_html=True)
        if st.button(f"Lưu chiến dịch: {t['title']}", key=f"camp_{t['title']}", use_container_width=True):
            execute("INSERT INTO ai_campaigns VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), t['title'], t['target'], t['channel'], t['message'], 'draft', now()))
            st.success("Đã lưu vào danh sách chiến dịch.")
    st.markdown("### ✍️ Tạo caption nhanh")
    offer=st.text_input("Ưu đãi muốn quảng cáo", value="Đặt sân cuối tuần + check-in nhận điểm")
    audience=st.selectbox("Đối tượng", ["Người mới chơi", "Nhóm văn phòng", "Sinh viên", "CLB cầu lông", "Người muốn mua/bán vợt"])
    if st.button("AI tạo caption Facebook", use_container_width=True):
        caption=f"🏸 {audience} ở TP Vinh ơi!\n\n{offer}. Với Badminton Vinh AI Automation Ultra, bạn có thể đặt sân nhanh, tìm kèo, thuê vợt/cầu, mua bán dụng cụ và check-in tích điểm.\n\nChơi đều hơn, kết nối dễ hơn, quản lý lịch gọn hơn.\n\n#BadmintonVinh #CauLongVinh #DatSanCauLong"
        st.text_area("Caption", value=caption, height=220)
    rows=q("SELECT * FROM ai_campaigns ORDER BY created_at DESC")
    if rows:
        st.markdown("### Chiến dịch đã lưu")
        st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)


def page_ai_pricing_ops() -> None:
    st.title("💹 AI Pricing & Court Ops")
    st.caption("Gợi ý giá theo khung giờ, lấp sân thấp điểm, bảo trì sân và vận hành chủ sân.")
    courts=q("SELECT * FROM courts WHERE status='active'")
    bookings=q("SELECT * FROM bookings")
    st.markdown("### Gợi ý giá thông minh")
    for c in courts:
        count=sum(1 for b in bookings if b['court_id']==c['id'])
        base=int(c['price'])
        hot_price=base+20000 if count>=3 else base+10000
        low_price=max(40000, base-15000)
        st.markdown(f"<div class='pro-panel'><h3>{c['name']}</h3><div class='muted'>Hiện tại: {vnd(base)}/giờ · số booking: {count}</div><div class='grid3'><div class='heat-cell heat-hot'>Giờ hot<br><b>{vnd(hot_price)}</b></div><div class='heat-cell heat-mid'>Giờ thường<br><b>{vnd(base)}</b></div><div class='heat-cell heat-low'>Giờ thấp điểm<br><b>{vnd(low_price)}</b></div></div></div>", unsafe_allow_html=True)
    st.markdown("### Checklist vận hành tự động")
    checks=["Kiểm tra đèn sân trước 17:00", "Kiểm tra lưới và thảm sau mỗi ngày", "Gọi xác nhận khách đặt sân giờ cao điểm", "Đẩy voucher giờ thấp điểm vào buổi trưa", "Nhắc khách check-in để nhận điểm"]
    for i,ch in enumerate(checks,1): st.checkbox(ch, key=f"ops_{i}")


def page_ai_crm_matchmaking() -> None:
    st.title("🧑‍🤝‍🧑 AI CRM & Matchmaking")
    st.caption("Tự phân nhóm khách, gợi ý chăm sóc và ghép kèo theo khu vực/trình độ/khung giờ.")
    users=q("SELECT * FROM users")
    bookings=q("SELECT * FROM bookings")
    for u in users[:20]:
        user_bookings=[b for b in bookings if b['user_id']==u['id']]
        spend=sum(int(b['total'] or 0) for b in user_bookings)
        if spend>500000: tag='VIP'; action='Giữ khung giờ đẹp, tặng voucher hội viên.'
        elif len(user_bookings)>=2: tag='Tiềm năng'; action='Mời mua gói 5 buổi hoặc tham gia giải giao lưu.'
        else: tag='Mới'; action='Gửi hướng dẫn đặt sân nhanh và voucher lần 2.'
        st.markdown(f"<div class='crm-row'><span class='owner-chip'>{tag}</span><b>{u['name']}</b> · {u['phone'] or 'chưa có SĐT'}<br><span class='muted'>{len(user_bookings)} lịch · {vnd(spend)} · AI gợi ý: {action}</span></div>", unsafe_allow_html=True)
    st.markdown("### Ghép kèo tự động demo")
    c1,c2,c3=st.columns(3)
    with c1: level=st.selectbox("Trình độ", ["Mới chơi","Trung bình","Khá","Nâng cao"])
    with c2: area=st.selectbox("Khu vực", ["Trung tâm","Lê Mao","Quán Bàu","Hưng Dũng","Bến Thủy"])
    with c3: time_slot=st.selectbox("Khung giờ", ["Sáng","Chiều","Tối","Cuối tuần"])
    st.success(f"AI gợi ý: Tạo kèo {level} tại {area}, khung {time_slot}. Nên mời 4–6 người và đặt sân trước ít nhất 2 giờ.")


def page_ai_workflow_builder() -> None:
    st.title("🧩 AI Workflow Builder")
    st.caption("Tạo rule tự động hóa không cần code: khi có điều kiện → app gợi ý hành động.")
    with st.form("rule_form"):
        name=st.text_input("Tên rule", value="Nhắc khách đặt lại sân")
        trigger=st.selectbox("Khi nào?", ["Có booking mới", "Khách check-in", "Giờ thấp điểm còn trống", "Có feedback mới", "Có sản phẩm mới đăng"])
        action=st.text_area("AI nên làm gì?", value="Gửi thông báo gợi ý đặt lại sân tuần sau và cộng điểm loyalty.")
        enabled=st.checkbox("Bật rule", value=True)
        if st.form_submit_button("Lưu rule", use_container_width=True):
            execute("INSERT INTO ai_rules VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), name, trigger, action, 1 if enabled else 0, now()))
            st.success("Đã lưu workflow rule.")
    rows=q("SELECT * FROM ai_rules ORDER BY created_at DESC")
    for r in rows:
        st.markdown(f"<div class='pro-panel'><span class='pill {'green' if r['is_enabled'] else 'red'}'>{'ON' if r['is_enabled'] else 'OFF'}</span><h3>{r['name']}</h3><div class='muted'>Trigger: {r['trigger_name']}<br>Action: {r['action_text']}</div></div>", unsafe_allow_html=True)


def page_ai_chat_pro() -> None:
    st.title("💬 AI Chat Pro Offline")
    st.caption("Hỏi trợ lý vận hành chuyên nghiệp. Mặc định dùng rule-based offline nên không tốn API.")
    signals=ai_collect_signals()
    qtext=st.text_area("Câu hỏi của bạn", placeholder="Ví dụ: Làm sao tăng khách buổi trưa? Cách bán gói hội viên? Cách quảng cáo Facebook?")
    if st.button("AI trả lời", use_container_width=True):
        st.success(ai_answer(qtext, signals))
        execute("INSERT INTO ai_logs VALUES (?,?,?,?)", (str(uuid.uuid4()), 'chat', qtext or 'empty', now()))
    st.markdown("### Câu hỏi nhanh")
    quick=["Làm sao tăng doanh thu sân?", "Cách quảng cáo Facebook?", "Cách giữ chân khách cũ?", "Nên bán gói hội viên thế nào?", "Làm sao tránh trùng lịch đặt sân?"]
    for item in quick:
        if st.button(item, key=f"quick_ai_{item}", use_container_width=True):
            st.info(ai_answer(item, signals))



# -----------------------------
# AI AUTOMATION ULTRA SUITE
# -----------------------------

def ultra_ai_signals() -> Dict[str, Any]:
    sig = ai_collect_signals()
    bookings = sig.get('booking_rows', [])
    products = sig.get('product_rows', [])
    days = {}
    areas = {}
    for b in bookings:
        day = str(b['booking_date'])
        days[day] = days.get(day, 0) + 1
        areas[str(b['area'] if 'area' in b.keys() else 'Khác')] = areas.get(str(b['area'] if 'area' in b.keys() else 'Khác'), 0) + 1
    sig['booking_days'] = days
    sig['hot_area'] = max(areas, key=areas.get) if areas else 'Chưa có dữ liệu'
    sig['inventory_value'] = sum(int(p['price'] or 0) for p in products)
    sig['utilization_hint'] = min(100, round(sig['bookings'] / max(1, sig['courts'] * 8) * 100))
    sig['mobile_readiness'] = 92
    sig['automation_maturity'] = min(100, 35 + sig['bookings']*3 + sig['products']*2 + len(q("SELECT * FROM ai_rules"))*5)
    return sig


def ultra_ai_playbooks(sig: Dict[str, Any]) -> List[Dict[str, str]]:
    return [
        {"title":"Playbook 7 ngày tăng booking", "area":"Growth", "goal":"Tăng số lịch đặt sân thật", "steps":"Ngày 1: kiểm tra thông tin sân thật. Ngày 2: đăng bài Facebook nhóm địa phương. Ngày 3: tạo voucher giờ thấp điểm. Ngày 4: mời nhóm văn phòng. Ngày 5: đẩy combo thuê vợt/cầu. Ngày 6: nhắc khách đặt lại. Ngày 7: xem báo cáo và tối ưu."},
        {"title":"Playbook lấp giờ thấp điểm", "area":"Pricing", "goal":"Tăng tỷ lệ sử dụng sân buổi trưa/sáng sớm", "steps":"Tìm giờ có ít booking. Tạo voucher 10-20%. Tạo gói sinh viên/văn phòng. Gửi thông báo app. Theo dõi booking 7 ngày."},
        {"title":"Playbook tăng marketplace", "area":"Marketplace", "goal":"Tăng sản phẩm mua bán dụng cụ", "steps":"Ghim danh mục vợt/giày/cầu. Khuyến khích đăng bán miễn phí. Kiểm duyệt tin có ảnh/giá/SĐT. Tạo bài tổng hợp sản phẩm nổi bật mỗi tuần."},
        {"title":"Playbook giữ chân khách", "area":"CRM", "goal":"Tăng quay lại và mua gói hội viên", "steps":"Phân loại khách mới/tiềm năng/VIP. Khách mới nhận voucher lần 2. Khách tiềm năng nhận gói 5 buổi. VIP giữ khung giờ đẹp và ưu đãi giải đấu."},
        {"title":"Playbook vận hành chủ sân", "area":"Court Ops", "goal":"Giảm lỗi vận hành và tăng trải nghiệm", "steps":"Mỗi ngày kiểm tra đèn/lưới/thảm. Trước giờ hot xác nhận lịch. Sau buổi chơi mời review/check-in. Ghi nhận lỗi sân và ưu tiên sửa."},
    ]


def ultra_generate_actions(sig: Dict[str, Any]) -> List[Dict[str, str]]:
    actions = []
    if sig['utilization_hint'] < 40:
        actions.append({"name":"Tự tạo voucher giờ trống", "target":"Khung giờ thấp điểm", "cadence":"Mỗi ngày", "detail":"Nếu tỷ lệ lấp sân thấp, tạo voucher 10-20% cho giờ sáng/trưa và đăng nhắc trên Facebook."})
    if sig['feedback_open'] > 0:
        actions.append({"name":"Tự tạo task xử lý feedback", "target":"Đội vận hành", "cadence":"Ngay khi có feedback", "detail":"Tạo task ưu tiên cao cho lỗi app, sai thông tin sân hoặc góp ý liên quan đặt lịch."})
    actions.append({"name":"Nhắc khách đặt lại sân", "target":"Khách đã booking", "cadence":"Hằng tuần", "detail":"Gửi thông báo gợi ý giữ khung giờ cũ, kèm điểm loyalty hoặc voucher nhỏ."})
    actions.append({"name":"Tự đề xuất combo", "target":"Người đặt sân", "cadence":"Mỗi booking", "detail":"Nếu đặt sân mới, gợi ý thuê vợt, mua cầu, nước uống hoặc gói HLV nhập môn."})
    actions.append({"name":"Tự tạo báo cáo cuối ngày", "target":"Chủ sân/admin", "cadence":"Hằng ngày", "detail":"Tổng hợp booking, doanh thu, giờ hot, feedback, sản phẩm mới và task đang mở."})
    actions.append({"name":"Tự gợi ý kèo phù hợp", "target":"Người chơi", "cadence":"Khi tìm người chơi", "detail":"Ghép theo khu vực, trình độ, khung giờ và số người còn thiếu."})
    return actions


def ultra_forecast(sig: Dict[str, Any]) -> Dict[str, Any]:
    base = max(1, sig['bookings'])
    projected_bookings = round(base * 1.25 + len(q("SELECT * FROM ai_rules")))
    projected_revenue = projected_bookings * max(60000, int(sig.get('avg_price') or 80000))
    risk = []
    if sig['courts'] < 5: risk.append('Thiếu dữ liệu sân thật')
    if sig['products'] < 8: risk.append('Marketplace chưa đủ sản phẩm')
    if sig['feedback_open'] > 0: risk.append('Còn feedback/lỗi mở')
    if sig['bookings'] < 5: risk.append('Chưa đủ dữ liệu booking để dự báo chính xác')
    return {"projected_bookings": projected_bookings, "projected_revenue": projected_revenue, "risks": risk or ['Ổn định'], "confidence": min(92, 50 + sig['bookings']*4 + sig['courts']*3)}


def page_ai_ultra_command_center() -> None:
    st.title("🧠 AI Ultra Command Center")
    st.caption("Bộ não tự động hóa toàn hệ thống: phân tích, ưu tiên, tạo chiến lược, tự tạo task và gợi ý hành động tiếp theo. Offline-first, không tốn API mặc định.")
    sig = ultra_ai_signals(); forecast = ultra_forecast(sig)
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("Automation Score", f"{sig['automation_maturity']}/100", "mức tự động hóa")
    with c2: metric_card("Lấp sân ước tính", f"{sig['utilization_hint']}%", "dựa trên booking")
    with c3: metric_card("Dự báo booking", forecast['projected_bookings'], "chu kỳ tiếp theo")
    with c4: metric_card("Dự báo doanh thu", vnd(forecast['projected_revenue']), "ước tính")
    st.markdown("### 🔥 AI ưu tiên hôm nay")
    priority = [("1", "Tăng booking", "Ghim nút đặt sân nhanh, tạo voucher NEWBIE20, đăng bài Facebook 15 giây."),("2", "Giữ chân khách", "Khách đã check-in/booking cần được mời đặt lại sân tuần sau."),("3", "Làm sạch dữ liệu", "Kiểm tra tên sân, giá, SĐT và khung giờ để tránh mất niềm tin."),("4", "Kích hoạt marketplace", "Mời người chơi đăng bán vợt, giày, cầu và phụ kiện.")]
    for n,t,d in priority:
        st.markdown(f"<div class='automation-step'><b>#{n} · {t}</b><br><span class='muted'>{d}</span></div>", unsafe_allow_html=True)
    st.markdown("### 🤖 AI Agents chuyên trách")
    agents = [("Growth Agent", "Tăng booking, tạo chiến dịch, tối ưu CTA."),("Court Ops Agent", "Theo dõi sân, đèn, lưới, lịch trùng và khung giờ hot."),("CRM Agent", "Phân loại khách, giữ chân, nhắc đặt lại, loyalty."),("Marketplace Agent", "Gợi ý đăng bán, kiểm duyệt sản phẩm, đẩy sản phẩm nổi bật."),("Coach Agent", "Gợi ý giáo án, HLV, lớp học thử."),("Finance Agent", "Dự báo doanh thu, giá giờ hot/thấp điểm.")]
    cols = st.columns(3)
    for i,(name,body) in enumerate(agents):
        with cols[i%3]:
            st.markdown(f"<div class='agent-card'><span class='pill green'>AI Agent</span><h3>{name}</h3><div class='muted'>{body}</div></div>", unsafe_allow_html=True)
    if st.button("🚀 AI tự tạo kế hoạch vận hành 7 ngày", use_container_width=True):
        made=0
        for pb in ultra_ai_playbooks(sig):
            execute("INSERT INTO ai_playbooks VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), pb['title'], pb['area'], pb['goal'], pb['steps'], 'draft', now()))
            made+=1
        st.success(f"Đã tạo {made} playbook vận hành.")


def page_ai_auto_scheduler() -> None:
    st.title("⏱️ AI Auto Scheduler")
    st.caption("AI tạo lịch tự động hóa vận hành: nhắc khách, tạo voucher, báo cáo cuối ngày, xử lý feedback, gợi ý combo.")
    sig = ultra_ai_signals(); actions = ultra_generate_actions(sig)
    for a in actions:
        st.markdown(f"<div class='ai-ultra'><span class='pill blue'>{a['cadence']}</span><h3>{a['name']}</h3><div class='muted'><b>Đối tượng:</b> {a['target']}<br>{a['detail']}</div></div>", unsafe_allow_html=True)
        if st.button(f"Lưu automation: {a['name']}", key=f"save_auto_{a['name']}", use_container_width=True):
            execute("INSERT INTO ai_scheduled_actions VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), a['name'], a['target'], a['cadence'], (date.today()+timedelta(days=1)).isoformat(), 'active', a['detail'], now()))
            st.success("Đã lưu automation.")
    rows=q("SELECT * FROM ai_scheduled_actions ORDER BY created_at DESC")
    if rows:
        st.markdown("### Automation đã lưu")
        st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)


def page_ai_playbook_lab() -> None:
    st.title("📚 AI Playbook Lab")
    st.caption("Kho chiến lược AI tự tạo cho tăng trưởng, vận hành sân, marketplace, CRM và hội viên.")
    sig = ultra_ai_signals()
    tabs = st.tabs(["Gợi ý playbook", "Playbook đã lưu", "A/B Experiment"])
    with tabs[0]:
        for pb in ultra_ai_playbooks(sig):
            st.markdown(f"<div class='pro-panel'><span class='pill purple'>{pb['area']}</span><h3>{pb['title']}</h3><b>Mục tiêu:</b> {pb['goal']}<br><br><span class='muted'>{pb['steps']}</span></div>", unsafe_allow_html=True)
            if st.button(f"Lưu playbook: {pb['title']}", key=f"pb_{pb['title']}", use_container_width=True):
                execute("INSERT INTO ai_playbooks VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), pb['title'], pb['area'], pb['goal'], pb['steps'], 'draft', now()))
                st.success("Đã lưu playbook.")
    with tabs[1]:
        rows=q("SELECT * FROM ai_playbooks ORDER BY created_at DESC")
        if rows: st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)
        else: st.info("Chưa có playbook đã lưu.")
    with tabs[2]:
        with st.form("exp_form"):
            title=st.text_input("Tên thử nghiệm", value="Voucher giờ trưa 15%")
            hypothesis=st.text_area("Giả thuyết", value="Nếu giảm 15% giờ trưa, số booking giờ thấp điểm sẽ tăng.")
            metric=st.text_input("Chỉ số đo", value="Số booking giờ 10:00-14:00")
            if st.form_submit_button("Tạo A/B experiment", use_container_width=True):
                execute("INSERT INTO ai_experiments VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), title, hypothesis, metric, 'Chưa có dữ liệu', 'running', now()))
                st.success("Đã tạo experiment.")
        exps=q("SELECT * FROM ai_experiments ORDER BY created_at DESC")
        if exps: st.dataframe(pd.DataFrame([dict(r) for r in exps]), use_container_width=True)


def page_ai_inventory_finance() -> None:
    st.title("📦 AI Inventory & Finance")
    st.caption("AI kiểm tra sản phẩm, giá, tồn kho demo, gợi ý combo và dự báo doanh thu.")
    sig=ultra_ai_signals(); products=sig.get('product_rows', [])
    c1,c2,c3=st.columns(3)
    with c1: metric_card("Sản phẩm", sig['products'], "marketplace")
    with c2: metric_card("Giá trị hàng demo", vnd(sig['inventory_value']), "tổng giá đăng bán")
    with c3: metric_card("Dự báo doanh thu", vnd(ultra_forecast(sig)['projected_revenue']), "booking")
    cats={}
    for p in products:
        cats[p['category']]=cats.get(p['category'],0)+1
    st.markdown("### AI gợi ý danh mục cần bổ sung")
    for cat in ['Vợt','Giày','Cầu','Phụ kiện','Áo quần']:
        count=cats.get(cat,0)
        if count<2: st.warning(f"Nên bổ sung thêm {cat}: hiện có {count} tin.")
        else: st.success(f"{cat}: ổn, có {count} tin.")
    st.markdown("### Combo AI đề xuất")
    combos=["Đặt sân + thuê 2 vợt + 1 ống cầu", "Gói người mới: 1 buổi HLV + sân 60 phút", "Gói CLB: giữ sân 4 tuần + voucher cầu", "Combo giải đấu: sân + cầu + nước + check-in QR"]
    for c in combos: st.markdown(f"<div class='deal-card'>🏸 {c}</div>", unsafe_allow_html=True)


def page_ai_risk_guard() -> None:
    st.title("🛡️ AI Risk Guard")
    st.caption("Kiểm tra rủi ro vận hành: trùng lịch, thiếu dữ liệu, feedback chưa xử lý, sản phẩm thiếu thông tin, UX mobile.")
    sig=ultra_ai_signals(); issues=[]
    bookings=sig.get('booking_rows', [])
    seen=set()
    for b in bookings:
        key=(b['court_id'], b['booking_date'], b['start_time'])
        if key in seen: issues.append(f"Có nguy cơ trùng lịch: {b['booking_date']} {b['start_time']}")
        seen.add(key)
    for p in sig.get('product_rows', []):
        if not p['phone'] or not p['price']: issues.append(f"Sản phẩm thiếu SĐT/giá: {p['title']}")
    if sig['feedback_open']>0: issues.append(f"Có {sig['feedback_open']} feedback/lỗi chưa xử lý.")
    if sig['courts']<5: issues.append("Dữ liệu sân còn ít, nên bổ sung sân thật ở TP Vinh.")
    if not issues:
        st.success("AI Risk Guard: chưa thấy rủi ro lớn trong dữ liệu hiện tại.")
    else:
        for x in issues: st.error("⚠️ " + x)
    st.markdown("### Checklist an toàn public")
    checks=["Thông tin sân đã đúng SĐT/địa chỉ", "Không thu tiền thật nếu chưa tích hợp thanh toán", "Có điều khoản mua bán dụng cụ", "Có quy định hủy lịch", "Có admin xử lý feedback", "Backup SQLite định kỳ"]
    for i,ch in enumerate(checks): st.checkbox(ch, key=f"risk_{i}")


def page_ai_ultra_settings() -> None:
    st.title("⚙️ AI Ultra Settings")
    st.caption("Cấu hình AI tự động hóa offline-first. Mặc định không dùng API trả phí.")
    st.markdown("<div class='ai-ultra'><h3>Chế độ AI hiện tại</h3><span class='pill green'>Offline-first</span><span class='pill blue'>Không tốn API</span><span class='pill purple'>Rule-based + dữ liệu nội bộ</span></div>", unsafe_allow_html=True)
    mode=st.selectbox("AI Mode", ["offline", "hybrid-demo", "external-api-later"])
    st.info("Khuyến nghị giữ offline để không phát sinh chi phí. Khi cần API thật, chỉ bật sau khi có giới hạn quota và khóa chi phí.")
    st.markdown("### Secrets khuyến nghị")
    st.code("""AI_MODE="offline"
USE_EXTERNAL_AI="false"
MAX_AI_CALLS_PER_SESSION="0"
ENABLE_AI_AUTOMATION="true"
ENABLE_AI_RISK_GUARD="true""", language='toml')
    if st.button("Ghi log cấu hình AI", use_container_width=True):
        execute("INSERT INTO ai_logs VALUES (?,?,?,?)", (str(uuid.uuid4()), 'settings', f'AI mode viewed: {mode}', now()))
        st.success("Đã ghi log.")

# -----------------------------
# ROUTER
# -----------------------------

def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🏸", layout="wide", initial_sidebar_state="expanded")
    inject_css()
    init_db()
    ensure_session()
    login_panel()
    st.sidebar.divider()
    page = st.sidebar.radio(
        "Điều hướng",
        [
            "🏠 Trang chính",
            "📅 Đặt lịch sân",
            "🛒 Chợ mua bán",
            "➕ Đăng bán",
            "🗓️ Lịch của tôi",
            "👥 Tìm người chơi",
            "🎓 HLV & lớp học",
            "🏋️ Giáo án luyện tập",
            "🏆 Giải đấu",
            "💎 Hội viên",
            "✅ Check-in",
            "📊 Báo cáo Pro",
            "🚀 Pro Max Center",
            "⚡ Đặt sân thông minh",
            "🏟️ Chủ sân Portal",
            "💰 Ví điểm & Loyalty",
            "🔳 QR Check-in",
            "🧑‍💼 CRM khách hàng",
            "📤 Xuất báo cáo",
            "🧠 AI Ultra Command Center",
            "⏱️ AI Auto Scheduler",
            "📚 AI Playbook Lab",
            "📦 AI Inventory & Finance",
            "🛡️ AI Risk Guard",
            "⚙️ AI Ultra Settings",
            "🤖 AI Automation Center",
            "✅ AI Task Manager",
            "📣 AI Marketing Auto",
            "💹 AI Pricing & Ops",
            "🧑‍🤝‍🧑 AI CRM & Matchmaking",
            "🧩 AI Workflow Builder",
            "💬 AI Chat Pro",
            "🤖 Trợ lý offline",
            "🛡️ An toàn & điều khoản",
            "🔔 Thông báo",
            "👑 Admin mini",
            "🩺 Health Check",
            "⚙️ Cài đặt",
        ],
    )
    st.markdown('<div class="mobile-nav-note">🏸 Badminton Vinh AI Automation Ultra · Pro</div>', unsafe_allow_html=True)
    if page == "🏠 Trang chính": page_home()
    elif page == "📅 Đặt lịch sân": page_courts()
    elif page == "🛒 Chợ mua bán": page_market()
    elif page == "➕ Đăng bán": page_sell()
    elif page == "🗓️ Lịch của tôi": page_my_schedule()
    elif page == "👥 Tìm người chơi": page_find_players()
    elif page == "🎓 HLV & lớp học": page_coaches()
    elif page == "🏋️ Giáo án luyện tập": page_training()
    elif page == "🏆 Giải đấu": page_tournaments()
    elif page == "💎 Hội viên": page_membership()
    elif page == "✅ Check-in": page_checkin()
    elif page == "📊 Báo cáo Pro": page_pro_analytics()
    elif page == "🚀 Pro Max Center": page_pro_max_center()
    elif page == "⚡ Đặt sân thông minh": page_smart_booking()
    elif page == "🏟️ Chủ sân Portal": page_owner_portal()
    elif page == "💰 Ví điểm & Loyalty": page_wallet_loyalty()
    elif page == "🔳 QR Check-in": page_qr_checkin()
    elif page == "🧑‍💼 CRM khách hàng": page_crm_customers()
    elif page == "📤 Xuất báo cáo": page_export_reports()
    elif page == "🧠 AI Ultra Command Center": page_ai_ultra_command_center()
    elif page == "⏱️ AI Auto Scheduler": page_ai_auto_scheduler()
    elif page == "📚 AI Playbook Lab": page_ai_playbook_lab()
    elif page == "📦 AI Inventory & Finance": page_ai_inventory_finance()
    elif page == "🛡️ AI Risk Guard": page_ai_risk_guard()
    elif page == "⚙️ AI Ultra Settings": page_ai_ultra_settings()
    elif page == "🤖 AI Automation Center": page_ai_automation_center()
    elif page == "✅ AI Task Manager": page_ai_task_manager()
    elif page == "📣 AI Marketing Auto": page_ai_marketing_auto()
    elif page == "💹 AI Pricing & Ops": page_ai_pricing_ops()
    elif page == "🧑‍🤝‍🧑 AI CRM & Matchmaking": page_ai_crm_matchmaking()
    elif page == "🧩 AI Workflow Builder": page_ai_workflow_builder()
    elif page == "💬 AI Chat Pro": page_ai_chat_pro()
    elif page == "🤖 Trợ lý offline": page_ai_assistant_rules()
    elif page == "🛡️ An toàn & điều khoản": page_public_safety()
    elif page == "🔔 Thông báo": page_notifications()
    elif page == "👑 Admin mini": page_admin()
    elif page == "🩺 Health Check": page_health()
    elif page == "⚙️ Cài đặt": page_settings()
    st.caption("Badminton Vinh AI Automation Ultra · AI Automation · Owner Portal · CRM · Loyalty · QR · Analytics · Đặt sân · Marketplace · HLV · Giải đấu · Hội viên · Analytics · Mobile-first.")


if __name__ == "__main__":
    main()
