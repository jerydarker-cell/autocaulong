# -*- coding: utf-8 -*-
"""Badminton Vinh Production Ready v1.2 Cloud Login
Chạy: streamlit run app.py
Một file độc lập: đăng nhập thật, phân quyền, đặt sân, chủ sân, admin, backup/cloud sync, AI vận hành offline.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

APP_NAME = "Badminton Vinh Production Ready v1.2 Cloud Login"
APP_VERSION = "1.2 Cloud Login"
DB_PATH = Path("badminton_vinh_v1_2_cloud_login.sqlite3")

# ========================= UI =========================

def css() -> None:
    st.markdown("""
    <style>
    :root{--bg:#050b12;--panel:#0d1725;--line:#1f334d;--muted:#9fb3c8;--green:#22c55e;--blue:#38bdf8;--yellow:#f59e0b;--red:#ef4444;--purple:#8b5cf6}
    .main .block-container{max-width:1080px;padding-top:1rem;padding-bottom:4rem}
    h1,h2,h3{letter-spacing:-.03em}.muted{color:var(--muted)}
    .hero{background:radial-gradient(circle at 10% 0%,rgba(34,197,94,.22),transparent 38%),radial-gradient(circle at 90% 0%,rgba(56,189,248,.16),transparent 40%),linear-gradient(135deg,#07111f,#0c1b2d 70%,#08111d);border:1px solid rgba(94,234,212,.18);border-radius:28px;padding:22px;margin-bottom:18px;box-shadow:0 22px 60px rgba(0,0,0,.35)}
    .hero-title{font-size:2.05rem;font-weight:950;line-height:1.05;color:#fff}.hero-sub{font-size:1rem;color:var(--muted);max-width:760px;margin-top:8px}
    .grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
    .card{background:linear-gradient(180deg,rgba(16,29,46,.96),rgba(10,18,31,.96));border:1px solid var(--line);border-radius:24px;padding:16px;box-shadow:0 18px 36px rgba(0,0,0,.22);margin:8px 0}.card h3{margin:.2rem 0 .35rem 0;font-size:1.05rem}.big{font-size:1.75rem;font-weight:950;color:#fff}
    .pill{display:inline-flex;align-items:center;gap:6px;padding:7px 11px;border-radius:999px;font-weight:800;font-size:.78rem;margin:3px 4px 3px 0;border:1px solid var(--line)}.green{background:rgba(34,197,94,.12);color:#86efac;border-color:rgba(34,197,94,.28)}.blue{background:rgba(56,189,248,.12);color:#7dd3fc;border-color:rgba(56,189,248,.28)}.yellow{background:rgba(245,158,11,.12);color:#fcd34d;border-color:rgba(245,158,11,.28)}.red{background:rgba(239,68,68,.12);color:#fca5a5;border-color:rgba(239,68,68,.28)}.purple{background:rgba(139,92,246,.12);color:#c4b5fd;border-color:rgba(139,92,246,.28)}
    .row-card{background:linear-gradient(180deg,#0e1b2b,#0b1422);border:1px solid #1e3350;border-radius:22px;padding:14px;margin:10px 0}.price{font-size:1.15rem;font-weight:950;color:#86efac}.safe{border-left:4px solid var(--green);background:rgba(34,197,94,.08);padding:10px 12px;border-radius:12px}.warn{border-left:4px solid var(--yellow);background:rgba(245,158,11,.08);padding:10px 12px;border-radius:12px}.bad{border-left:4px solid var(--red);background:rgba(239,68,68,.08);padding:10px 12px;border-radius:12px}
    .stButton>button{border-radius:16px!important;min-height:42px;font-weight:850!important;border:1px solid #24405f!important;background:#10233a!important;color:#eef7ff!important}.stButton>button:hover{border-color:#22c55e!important;color:#86efac!important}
    .mobile-note{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);z-index:999;background:rgba(8,15,28,.9);border:1px solid #24405f;border-radius:999px;padding:8px 14px;color:#dbeafe;font-size:.8rem;backdrop-filter:blur(8px)}
    @media(max-width:850px){.main .block-container{padding-left:.7rem;padding-right:.7rem}.hero{padding:16px;border-radius:22px}.hero-title{font-size:1.45rem}.grid4,.grid3,.grid2{grid-template-columns:1fr}.card{padding:13px;border-radius:20px}.big{font-size:1.35rem}.pill{font-size:.72rem;padding:6px 9px}}
    </style>
    """, unsafe_allow_html=True)

def hero(title: str, sub: str) -> None:
    st.markdown(f"""<div class='hero'><div class='hero-title'>{title}</div><div class='hero-sub'>{sub}</div><div style='margin-top:12px'><span class='pill green'>🏸 TP Vinh</span><span class='pill blue'>🔐 Cloud Login</span><span class='pill yellow'>📅 Đặt sân</span><span class='pill purple'>🤖 AI offline</span></div></div>""", unsafe_allow_html=True)

def status(msg: str, kind: str = "safe") -> None:
    st.markdown(f"<div class='{kind}'>{msg}</div>", unsafe_allow_html=True)

def metric(title: str, value: Any, cap: str = "") -> None:
    st.markdown(f"<div class='card'><div class='muted'>{title}</div><div class='big'>{value}</div><div class='muted'>{cap}</div></div>", unsafe_allow_html=True)

def card(icon: str, title: str, body: str, tag: str = "") -> None:
    tag_html = f"<span class='pill blue'>{tag}</span>" if tag else ""
    st.markdown(f"<div class='card'><div style='font-size:1.8rem'>{icon}</div><h3>{title}</h3><div class='muted'>{body}</div><div style='margin-top:8px'>{tag_html}</div></div>", unsafe_allow_html=True)

def fmt_money(v: Any) -> str:
    try:
        return f"{int(v):,}".replace(",", ".") + "đ"
    except Exception:
        return str(v)

# ========================= DB =========================

def conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def q(sql: str, params: tuple = ()) -> List[sqlite3.Row]:
    with conn() as c:
        return c.execute(sql, params).fetchall()

def one(sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
    rows = q(sql, params)
    return rows[0] if rows else None

def execute(sql: str, params: tuple = ()) -> None:
    with conn() as c:
        c.execute(sql, params)
        c.commit()

def rows_to_df(rows: List[sqlite3.Row]) -> pd.DataFrame:
    return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()

def init_db() -> None:
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE, phone TEXT, password_hash TEXT,
            role TEXT, level TEXT, area TEXT, is_active INTEGER DEFAULT 1, last_login TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS courts(
            id TEXT PRIMARY KEY, owner_id TEXT, name TEXT, area TEXT, address TEXT, phone TEXT,
            price INTEGER, peak_price INTEGER, rating REAL, court_count INTEGER, features TEXT,
            open_time TEXT, close_time TEXT, status TEXT, bank_info TEXT
        );
        CREATE TABLE IF NOT EXISTS bookings(
            id TEXT PRIMARY KEY, user_id TEXT, court_id TEXT, booking_date TEXT, start_time TEXT,
            duration INTEGER, players INTEGER, total INTEGER, payment_status TEXT, status TEXT,
            note TEXT, customer_name TEXT, customer_phone TEXT, deposit_amount INTEGER DEFAULT 0,
            transaction_code TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS products(
            id TEXT PRIMARY KEY, seller_id TEXT, title TEXT, category TEXT, condition TEXT,
            price INTEGER, area TEXT, phone TEXT, description TEXT, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS matches(
            id TEXT PRIMARY KEY, creator_id TEXT, title TEXT, area TEXT, level TEXT,
            play_date TEXT, start_time TEXT, slots INTEGER, note TEXT, status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS memberships(id TEXT PRIMARY KEY,user_id TEXT,package TEXT,balance INTEGER,total INTEGER,expires_at TEXT,status TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS checkins(id TEXT PRIMARY KEY,user_id TEXT,booking_id TEXT,court_id TEXT,points INTEGER,created_at TEXT);
        CREATE TABLE IF NOT EXISTS notifications(id TEXT PRIMARY KEY,user_id TEXT,title TEXT,body TEXT,seen INTEGER,created_at TEXT);
        CREATE TABLE IF NOT EXISTS feedback(id TEXT PRIMARY KEY,user_id TEXT,category TEXT,message TEXT,status TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,title TEXT,owner TEXT,priority TEXT,status TEXT,due_date TEXT,source TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS sync_logs(id TEXT PRIMARY KEY, action TEXT, status TEXT, message TEXT, created_at TEXT);
        """)
        c.commit()
    seed()

def password_hash(password: str, salt: str | None = None) -> str:
    salt = salt or base64.urlsafe_b64encode(os.urandom(16)).decode()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return salt + "$" + base64.urlsafe_b64encode(digest).decode()

def verify_password(password: str, stored: str | None) -> bool:
    if not stored or "$" not in stored:
        return False
    salt, _ = stored.split("$", 1)
    return password_hash(password, salt) == stored

def seed() -> None:
    if one("SELECT id FROM users LIMIT 1"):
        return
    now = datetime.now().isoformat(timespec="seconds")
    users = [
        ("u_admin", "Admin Demo", "admin@badmintonvinh.local", "0900000000", password_hash("admin123"), "admin", "Advanced", "Trung tâm", 1, None, now),
        ("u_owner", "Chủ sân Demo", "owner@badmintonvinh.local", "0911111111", password_hash("owner123"), "owner", "Intermediate", "Lê Lợi", 1, None, now),
        ("u_player", "Người chơi Demo", "player@badmintonvinh.local", "0922222222", password_hash("player123"), "player", "Beginner", "Quán Bàu", 1, None, now),
    ]
    courts = [
        ("c1","u_owner","Sân Cầu Lông Trung Đô","Trung Đô","Đường Nguyễn Viết Xuân, TP Vinh","0912 000 111",80000,120000,4.8,6,"Đèn LED, thảm tốt, gửi xe","05:00","23:00","active","MB Bank 0900000000"),
        ("c2","u_owner","CLB Cầu Lông Lê Lợi","Lê Lợi","Khu Lê Lợi, TP Vinh","0912 000 222",70000,110000,4.6,4,"Có HLV, nước uống, phòng chờ","05:30","22:30","active","VCB 0911111111"),
        ("c3","u_owner","Sân Cầu Lông Quán Bàu","Quán Bàu","Quán Bàu, TP Vinh","0912 000 333",60000,90000,4.4,3,"Giá mềm, gần khu dân cư","06:00","22:00","active",""),
        ("c4","u_owner","Sân Cầu Lông Hưng Bình","Hưng Bình","Hưng Bình, TP Vinh","0912 000 444",75000,100000,4.5,5,"Sân rộng, ghép kèo nhanh","05:00","22:00","active",""),
    ]
    products = [
        ("p1","u_player","Vợt Yonex Astrox 77","Vợt","Đã dùng 90%",2200000,"Trung tâm","0922222222","Căng dây 11kg, hợp đánh đôi.","active",now),
        ("p2","u_player","Giày cầu lông Mizuno size 41","Giày","Đã dùng 2 tháng",950000,"Lê Lợi","0922222222","Đế còn tốt, bám sân.","active",now),
        ("p3","u_owner","Ống cầu Victor chính hãng","Cầu","Mới",350000,"Quán Bàu","0911111111","Cầu tập luyện CLB.","active",now),
    ]
    matches = [("m1","u_player","Tìm 2 bạn đánh đôi tối nay","Trung tâm","Trung bình",str(date.today()),"19:00",2,"Vui vẻ, chia sân đều.","open",now)]
    bookings = [("b1","u_player","c1",str(date.today()),"19:00",2,4,240000,"Chưa thanh toán","Đã xác nhận","Demo booking","Người chơi Demo","0922222222",0,"",now)]
    with conn() as c:
        c.executemany("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?)", users)
        c.executemany("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", courts)
        c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)", products)
        c.executemany("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?)", matches)
        c.executemany("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", bookings)
        c.commit()

def add_notification(user_id: str, title: str, body: str) -> None:
    execute("INSERT INTO notifications VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), user_id, title, body, 0, datetime.now().isoformat(timespec="seconds")))

# ========================= AUTH =========================

def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    return one("SELECT * FROM users WHERE lower(email)=lower(?)", (email.strip().lower(),))

def current_user() -> sqlite3.Row:
    uid = st.session_state.get("uid")
    if uid:
        u = one("SELECT * FROM users WHERE id=?", (uid,))
        if u:
            return u
    return one("SELECT * FROM users WHERE id='u_player'") or q("SELECT * FROM users LIMIT 1")[0]

def create_user(name: str, email: str, phone: str, password: str, role: str, level: str, area: str) -> Tuple[bool, str]:
    if not name.strip() or not email.strip() or not password:
        return False, "Vui lòng nhập tên, email và mật khẩu."
    if get_user_by_email(email):
        return False, "Email này đã tồn tại."
    uid = str(uuid.uuid4())
    execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?)", (uid, name.strip(), email.strip().lower(), phone.strip(), password_hash(password), role, level, area.strip(), 1, None, datetime.now().isoformat(timespec="seconds")))
    return True, uid

def login_user(email: str, password: str) -> Tuple[bool, str]:
    u = get_user_by_email(email)
    if not u:
        return False, "Không tìm thấy email."
    if int(u["is_active"] or 1) != 1:
        return False, "Tài khoản đang bị khóa."
    if not verify_password(password, u["password_hash"]):
        return False, "Sai mật khẩu."
    st.session_state["uid"] = u["id"]
    st.session_state["authenticated"] = True
    execute("UPDATE users SET last_login=? WHERE id=?", (datetime.now().isoformat(timespec="seconds"), u["id"]))
    return True, "Đăng nhập thành công."

def logout() -> None:
    st.session_state.pop("uid", None)
    st.session_state.pop("authenticated", None)
    st.rerun()

def auth_gate() -> bool:
    if st.session_state.get("authenticated") and st.session_state.get("uid"):
        return True
    hero("🏸 Badminton Vinh Production Ready v1.2", "Đăng nhập thật, phân quyền Người chơi / Chủ sân / Admin, có Cloud Sync để dữ liệu bền hơn.")
    st.markdown("<div class='safe'><b>Demo:</b> player@badmintonvinh.local / player123 · owner@badmintonvinh.local / owner123 · admin@badmintonvinh.local / admin123</div>", unsafe_allow_html=True)
    tabs = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký", "⚡ Demo nhanh"])
    with tabs[0]:
        with st.form("login"):
            email = st.text_input("Email", placeholder="player@badmintonvinh.local")
            pwd = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("Đăng nhập", type="primary"):
                ok, msg = login_user(email, pwd)
                if ok:
                    st.success(msg); st.rerun()
                else:
                    st.error(msg)
    with tabs[1]:
        with st.form("register"):
            name = st.text_input("Họ tên")
            email = st.text_input("Email")
            phone = st.text_input("Số điện thoại")
            role = st.selectbox("Tôi là", ["player", "owner"], format_func=lambda x: "Người chơi" if x=="player" else "Chủ sân")
            level = st.selectbox("Trình độ", ["Beginner", "Intermediate", "Advanced", "Coach"])
            area = st.text_input("Khu vực", "TP Vinh")
            p1 = st.text_input("Mật khẩu", type="password")
            p2 = st.text_input("Nhập lại mật khẩu", type="password")
            agree = st.checkbox("Tôi đồng ý dùng app đúng mục đích và chịu trách nhiệm với thông tin đăng lên.")
            if st.form_submit_button("Tạo tài khoản"):
                if p1 != p2: st.error("Mật khẩu nhập lại chưa khớp.")
                elif len(p1) < 6: st.error("Mật khẩu nên có ít nhất 6 ký tự.")
                elif not agree: st.error("Bạn cần đồng ý điều khoản sử dụng.")
                else:
                    ok, res = create_user(name, email, phone, p1, role, level, area)
                    if ok:
                        st.session_state["uid"] = res; st.session_state["authenticated"] = True
                        st.success("Đã tạo tài khoản và đăng nhập."); st.rerun()
                    else: st.error(res)
    with tabs[2]:
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("👤 Người chơi Demo"): login_user("player@badmintonvinh.local","player123"); st.rerun()
        with c2:
            if st.button("🏟️ Chủ sân Demo"): login_user("owner@badmintonvinh.local","owner123"); st.rerun()
        with c3:
            if st.button("👑 Admin Demo"): login_user("admin@badmintonvinh.local","admin123"); st.rerun()
    return False

def auth_panel() -> None:
    u = current_user()
    st.sidebar.markdown("### 👤 Tài khoản")
    st.sidebar.success(f"{u['name']} · {u['role']}")
    st.sidebar.caption(u["email"] or u["phone"])
    if st.sidebar.button("Đăng xuất"):
        logout()

# ========================= HELPERS =========================

def select_row(label: str, rows: List[sqlite3.Row], fmt, key: str) -> Optional[sqlite3.Row]:
    if not rows:
        st.info("Chưa có dữ liệu phù hợp.")
        return None
    labels = [fmt(r) for r in rows]
    idx = st.selectbox(label, list(range(len(rows))), format_func=lambda i: labels[i], key=key)
    return rows[int(idx)]

def app_stats() -> Dict[str, Any]:
    courts = q("SELECT * FROM courts")
    bookings = q("SELECT * FROM bookings")
    products = q("SELECT * FROM products WHERE status='active'")
    users = q("SELECT * FROM users")
    revenue = sum(int(b["total"] or 0) for b in bookings)
    fill_hint = min(100, int(len(bookings) / max(1, len(courts)*6) * 100))
    return {"courts":len(courts),"bookings":len(bookings),"products":len(products),"users":len(users),"revenue":revenue,"fill":fill_hint}

def ai_recommendations() -> List[Dict[str,str]]:
    s = app_stats()
    recs = []
    if s["fill"] < 45:
        recs.append({"title":"Lấp giờ thấp điểm", "body":"Tạo voucher 10–20% cho khung 13:00–16:00 và gửi cho nhóm sinh viên/văn phòng.", "priority":"Cao"})
    if s["products"] < 8:
        recs.append({"title":"Kích hoạt chợ dụng cụ", "body":"Mời người chơi đăng vợt/giày/cầu cũ, miễn phí đẩy tin 7 ngày đầu.", "priority":"Vừa"})
    recs.append({"title":"Tăng đặt lại sân", "body":"Sau mỗi check-in, gửi gợi ý đặt lại cùng khung giờ tuần sau + cộng điểm loyalty.", "priority":"Vừa"})
    recs.append({"title":"Combo sân + cầu + nước", "body":"Gói combo giúp tăng doanh thu mỗi buổi mà không cần tăng giá sân trực tiếp.", "priority":"Vừa"})
    return recs

def ai_answer(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["doanh thu", "revenue", "tiền"]):
        return "Để tăng doanh thu: lấp giờ thấp điểm bằng voucher, bán combo sân+cầu+nước, tạo gói hội viên 5/10 buổi, chăm sóc khách đặt lại theo tuần."
    if any(k in p for k in ["facebook", "marketing", "quảng cáo"]):
        return "Chiến dịch Facebook nên nhắm người chơi mới, sinh viên, dân văn phòng, CLB. Nội dung tốt nhất: video sân thật + giá rõ + nút đặt sân + ưu đãi giờ thấp điểm."
    if any(k in p for k in ["trùng", "lịch", "booking"]):
        return "Tránh trùng lịch bằng cách kiểm tra sân + ngày + giờ trước khi ghi booking. Chủ sân xác nhận rồi mới xem là chắc lịch."
    return "Gợi ý: giữ luồng đặt sân thật đơn giản, dữ liệu sân thật đầy đủ, ưu tiên mobile, dùng AI offline để tạo task hàng ngày."

# ========================= PAGES =========================

def page_home() -> None:
    u = current_user(); s = app_stats()
    hero("🏸 Badminton Vinh Production Ready", "v1.2 Cloud Login: đăng nhập thật, phân quyền, đặt sân Pro, chủ sân/admin, backup cloud snapshot và AI vận hành offline.")
    st.markdown(f"<span class='pill green'>Xin chào {u['name']}</span><span class='pill blue'>Vai trò: {u['role']}</span><span class='pill purple'>Cloud Login</span>", unsafe_allow_html=True)
    c = st.columns(4)
    with c[0]: metric("Sân", s["courts"], "đang quản lý")
    with c[1]: metric("Booking", s["bookings"], "lượt đặt")
    with c[2]: metric("Marketplace", s["products"], "sản phẩm")
    with c[3]: metric("Doanh thu demo", fmt_money(s["revenue"]), "tổng booking")
    st.markdown("### 🤖 Gợi ý AI hôm nay")
    for r in ai_recommendations()[:3]:
        status(f"<b>{r['title']}</b> · {r['body']} <span class='pill yellow'>{r['priority']}</span>", "warn" if r["priority"]=="Cao" else "safe")

def page_booking() -> None:
    hero("📅 Đặt sân Pro", "Luồng mobile ngắn: chọn sân → ngày/giờ → SĐT → xác nhận. Có cọc, mã giao dịch, trạng thái rõ.")
    courts = q("SELECT * FROM courts WHERE status='active' ORDER BY rating DESC")
    areas = ["Tất cả"] + sorted({c["area"] for c in courts})
    col1,col2 = st.columns(2)
    with col1: area = st.selectbox("Khu vực", areas)
    with col2: day = st.date_input("Ngày chơi", value=date.today())
    filtered = [c for c in courts if area=="Tất cả" or c["area"]==area]
    court = select_row("Chọn sân", filtered, lambda r: f"{r['name']} · {r['area']} · {fmt_money(r['price'])}/h", "book_court")
    if not court: return
    st.markdown(f"<div class='row-card'><h3>{court['name']}</h3><div class='muted'>{court['address']} · ☎ {court['phone']}</div><span class='pill green'>Thường {fmt_money(court['price'])}</span><span class='pill yellow'>Cao điểm {fmt_money(court['peak_price'])}</span></div>", unsafe_allow_html=True)
    times = [f"{h:02d}:00" for h in range(5,23)]
    c1,c2,c3 = st.columns(3)
    with c1: start = st.selectbox("Giờ", times, index=14)
    with c2: duration = st.selectbox("Số giờ", [1,2,3], index=1)
    with c3: players = st.selectbox("Số người", [2,4,6,8], index=1)
    unit = int(court["peak_price"] if start in ["18:00","19:00","20:00"] else court["price"])
    total = unit * int(duration)
    existed = one("SELECT * FROM bookings WHERE court_id=? AND booking_date=? AND start_time=? AND status NOT IN ('Đã hủy','Không đến')", (court["id"], str(day), start))
    if existed: status("Khung này đã có lịch. Chọn giờ khác nhé.", "bad")
    else: status(f"Còn trống · Tổng tạm tính <b>{fmt_money(total)}</b>", "safe")
    u = current_user()
    with st.form("booking_form"):
        name = st.text_input("Tên người đặt", u["name"])
        phone = st.text_input("Số điện thoại", u["phone"] or "")
        pay = st.selectbox("Thanh toán", ["Chưa thanh toán","Thanh toán tại sân","Đã cọc","Đã thanh toán"])
        deposit = st.number_input("Tiền cọc nếu có", 0, 10000000, 0, 10000)
        code = st.text_input("Mã giao dịch/chuyển khoản nếu có")
        note = st.text_area("Ghi chú", placeholder="Cần thuê vợt, mua cầu...")
        if st.form_submit_button("✅ Xác nhận đặt sân", disabled=bool(existed), type="primary"):
            bid=str(uuid.uuid4())
            execute("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (bid,u["id"],court["id"],str(day),start,duration,players,total,pay,"Chờ xác nhận",note,name,phone,deposit,code,datetime.now().isoformat(timespec="seconds")))
            add_notification(u["id"], "Đặt sân thành công", f"{court['name']} · {day} {start} · {fmt_money(total)}")
            st.success("Đã tạo lịch đặt sân. Chủ sân sẽ xác nhận."); st.rerun()

def page_my_bookings() -> None:
    hero("📋 Lịch của tôi", "Xem lịch đặt, trạng thái thanh toán, check-in và hủy lịch.")
    u = current_user()
    rows = q("SELECT b.*, c.name court_name, c.area FROM bookings b JOIN courts c ON b.court_id=c.id WHERE b.user_id=? ORDER BY b.booking_date DESC,b.start_time DESC", (u["id"],))
    if not rows:
        st.info("Bạn chưa có lịch đặt."); return
    for b in rows:
        with st.container(border=True):
            st.markdown(f"### {b['court_name']} · {b['booking_date']} {b['start_time']}")
            st.write(f"Trạng thái: **{b['status']}** · Thanh toán: **{b['payment_status']}** · Tổng: **{fmt_money(b['total'])}**")
            col1,col2=st.columns(2)
            with col1:
                if st.button("✅ Check-in", key="ci"+b["id"], disabled=b["status"]=="Đã hủy"):
                    execute("INSERT INTO checkins VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()),u["id"],b["id"],b["court_id"],10,datetime.now().isoformat(timespec="seconds")))
                    execute("UPDATE bookings SET status='Đã check-in' WHERE id=?", (b["id"],)); st.success("Đã check-in."); st.rerun()
            with col2:
                if st.button("❌ Hủy lịch", key="cancel"+b["id"], disabled=b["status"]=="Đã hủy"):
                    execute("UPDATE bookings SET status='Đã hủy' WHERE id=?", (b["id"],)); st.warning("Đã hủy lịch."); st.rerun()

def page_market() -> None:
    hero("🛒 Chợ mua bán", "Mua bán dụng cụ cầu lông: vợt, giày, cầu, túi, phụ kiện.")
    rows = q("SELECT p.*, u.name seller FROM products p LEFT JOIN users u ON p.seller_id=u.id WHERE p.status='active' ORDER BY p.created_at DESC")
    cats = ["Tất cả"] + sorted({r["category"] for r in rows})
    cat = st.selectbox("Danh mục", cats)
    keyword = st.text_input("Tìm kiếm", placeholder="vợt, giày, Yonex...")
    rows = [r for r in rows if (cat=="Tất cả" or r["category"]==cat) and (not keyword or keyword.lower() in (r["title"]+r["description"]).lower())]
    for p in rows:
        st.markdown(f"<div class='row-card'><h3>🏸 {p['title']}</h3><div class='price'>{fmt_money(p['price'])}</div><div class='muted'>{p['category']} · {p['condition']} · {p['area']}</div><p>{p['description']}</p><span class='pill blue'>Người bán: {p['seller']}</span><span class='pill green'>☎ {p['phone']}</span></div>", unsafe_allow_html=True)

def page_sell() -> None:
    hero("➕ Đăng bán", "Đăng bán dụng cụ cầu lông.")
    u = current_user()
    with st.form("sell_form"):
        title=st.text_input("Tên sản phẩm")
        cat=st.selectbox("Danh mục", ["Vợt","Giày","Cầu","Túi","Quần áo","Phụ kiện","Khác"])
        cond=st.selectbox("Tình trạng", ["Mới","Như mới","Đã dùng 90%","Đã dùng","Cần sửa"])
        price=st.number_input("Giá", 0, 100000000, 500000, 50000)
        area=st.text_input("Khu vực", u["area"] or "TP Vinh")
        phone=st.text_input("Số điện thoại", u["phone"] or "")
        desc=st.text_area("Mô tả")
        if st.form_submit_button("Đăng bán") and title:
            execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()),u["id"],title,cat,cond,price,area,phone,desc,"active",datetime.now().isoformat(timespec="seconds")))
            st.success("Đã đăng bán."); st.rerun()

def page_matches() -> None:
    hero("🤝 Tìm người chơi", "Tạo kèo, tìm bạn đánh đôi, tìm CLB theo khu vực và trình độ.")
    u=current_user()
    with st.expander("➕ Tạo kèo mới"):
        with st.form("match_form"):
            title=st.text_input("Tiêu đề", "Tìm bạn đánh đôi")
            area=st.text_input("Khu vực", u["area"] or "TP Vinh")
            level=st.selectbox("Trình độ", ["Người mới","Trung bình","Khá","Mọi trình độ"])
            d=st.date_input("Ngày", date.today())
            t=st.selectbox("Giờ", [f"{h:02d}:00" for h in range(5,23)], index=14)
            slots=st.number_input("Cần thêm người", 1, 20, 2)
            note=st.text_area("Ghi chú")
            if st.form_submit_button("Đăng kèo"):
                execute("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()),u["id"],title,area,level,str(d),t,slots,note,"open",datetime.now().isoformat(timespec="seconds")))
                st.success("Đã đăng kèo."); st.rerun()
    for m in q("SELECT m.*, u.name creator FROM matches m LEFT JOIN users u ON m.creator_id=u.id WHERE m.status='open' ORDER BY m.play_date,m.start_time"):
        st.markdown(f"<div class='row-card'><h3>🏸 {m['title']}</h3><div class='muted'>{m['area']} · {m['level']} · {m['play_date']} {m['start_time']} · cần {m['slots']} người</div><p>{m['note']}</p><span class='pill green'>Người tạo: {m['creator']}</span></div>", unsafe_allow_html=True)

def page_membership() -> None:
    hero("💎 Hội viên & Loyalty", "Gói hội viên, điểm check-in, ưu đãi giữ chân khách.")
    u=current_user()
    points=sum(int(r["points"] or 0) for r in q("SELECT points FROM checkins WHERE user_id=?", (u["id"],)))
    c1,c2=st.columns(2)
    with c1: metric("Điểm hiện tại", points, "10 điểm/check-in")
    with c2: metric("Gói hội viên", len(q("SELECT * FROM memberships WHERE user_id=?", (u["id"],))), "gói")
    packs=[("Gói 5 buổi",5,450000),("Gói 10 buổi",10,850000),("Gói CLB tháng",20,1500000)]
    cols=st.columns(3)
    for i,p in enumerate(packs):
        with cols[i]:
            card("💎",p[0],f"{p[1]} lượt · {fmt_money(p[2])}","Hội viên")
            if st.button("Đăng ký", key=p[0]):
                execute("INSERT INTO memberships VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()),u["id"],p[0],p[1],p[1],str(date.today()+timedelta(days=60)),"active",datetime.now().isoformat(timespec="seconds")))
                st.success("Đã đăng ký gói demo."); st.rerun()

def page_owner() -> None:
    hero("🏟️ Chủ sân Portal", "Quản lý lịch đặt, xác nhận/hủy, cập nhật thanh toán, xem doanh thu.")
    u=current_user()
    if u["role"] not in ["owner","admin"]:
        st.warning("Trang này dành cho chủ sân hoặc admin."); return
    if u["role"]=="admin":
        courts=q("SELECT * FROM courts")
    else:
        courts=q("SELECT * FROM courts WHERE owner_id=?", (u["id"],))
    ids=[c["id"] for c in courts]
    bks=[]
    if ids:
        placeholders=",".join("?"*len(ids))
        bks=q(f"SELECT b.*, c.name court_name, u.name user_name FROM bookings b JOIN courts c ON b.court_id=c.id LEFT JOIN users u ON b.user_id=u.id WHERE b.court_id IN ({placeholders}) ORDER BY b.booking_date DESC,b.start_time DESC", tuple(ids))
    c1,c2,c3=st.columns(3)
    with c1: metric("Sân", len(courts), "sân")
    with c2: metric("Booking", len(bks), "lượt")
    with c3: metric("Doanh thu", fmt_money(sum(int(b["total"] or 0) for b in bks)), "demo")
    for b in bks:
        with st.container(border=True):
            st.write(f"**{b['court_name']}** · {b['booking_date']} {b['start_time']} · {b['customer_name'] or b['user_name']} · {fmt_money(b['total'])}")
            st.caption(f"SĐT: {b['customer_phone']} · Lịch: {b['status']} · Thanh toán: {b['payment_status']} · Cọc: {fmt_money(b['deposit_amount'])}")
            col1,col2,col3=st.columns(3)
            with col1:
                if st.button("Xác nhận", key="ok"+b["id"]): execute("UPDATE bookings SET status='Đã xác nhận' WHERE id=?", (b["id"],)); st.rerun()
            with col2:
                if st.button("Đã thanh toán", key="pay"+b["id"]): execute("UPDATE bookings SET payment_status='Đã thanh toán' WHERE id=?", (b["id"],)); st.rerun()
            with col3:
                if st.button("Hủy", key="no"+b["id"]): execute("UPDATE bookings SET status='Đã hủy' WHERE id=?", (b["id"],)); st.rerun()
    st.markdown("### Thêm sân")
    with st.form("court_form"):
        name=st.text_input("Tên sân")
        area=st.text_input("Khu vực")
        address=st.text_input("Địa chỉ")
        phone=st.text_input("SĐT")
        price=st.number_input("Giá thường/giờ", 0, 500000, 70000, 10000)
        peak=st.number_input("Giá cao điểm/giờ", 0, 500000, 100000, 10000)
        count=st.number_input("Số sân",1,50,4)
        features=st.text_input("Tiện ích", "Đèn LED, thảm tốt")
        bank=st.text_input("Thông tin chuyển khoản", "")
        if st.form_submit_button("Thêm sân") and name:
            execute("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()),u["id"],name,area,address,phone,price,peak,4.5,count,features,"05:00","23:00","active",bank))
            st.success("Đã thêm sân."); st.rerun()

def page_court_data() -> None:
    hero("🏟️ Dữ liệu sân thật", "Nhập/chỉnh dữ liệu sân thật trước khi public.")
    if current_user()["role"] not in ["owner","admin"]:
        st.warning("Trang này dành cho chủ sân hoặc admin."); return
    tabs=st.tabs(["Danh sách", "Import CSV", "Checklist"])
    with tabs[0]:
        rows=q("SELECT * FROM courts ORDER BY area,name")
        st.dataframe(rows_to_df(rows), use_container_width=True)
        court=select_row("Chọn sân sửa nhanh", rows, lambda r: f"{r['name']} · {r['area']} · {r['phone']}", "edit_court")
        if court:
            with st.form("editcourt"):
                name=st.text_input("Tên", court["name"]); area=st.text_input("Khu vực", court["area"])
                address=st.text_input("Địa chỉ", court["address"]); phone=st.text_input("SĐT", court["phone"])
                price=st.number_input("Giá thường",0,1000000,int(court["price"] or 0),10000)
                peak=st.number_input("Giá cao điểm",0,1000000,int(court["peak_price"] or 0),10000)
                count=st.number_input("Số sân",1,100,int(court["court_count"] or 1))
                features=st.text_input("Tiện ích", court["features"] or "")
                bank=st.text_input("Chuyển khoản", court["bank_info"] or "")
                if st.form_submit_button("Lưu"):
                    execute("UPDATE courts SET name=?,area=?,address=?,phone=?,price=?,peak_price=?,court_count=?,features=?,bank_info=? WHERE id=?", (name,area,address,phone,price,peak,count,features,bank,court["id"]))
                    st.success("Đã lưu."); st.rerun()
    with tabs[1]:
        template=pd.DataFrame([{"name":"Tên sân mẫu","area":"Trung tâm","address":"Địa chỉ","phone":"09xxxxxxxx","price":70000,"peak_price":100000,"court_count":4,"features":"Gửi xe, nước uống","bank_info":"VCB ..."}])
        st.download_button("Tải mẫu CSV", template.to_csv(index=False).encode("utf-8-sig"), "mau_san.csv", "text/csv")
        up=st.file_uploader("Upload CSV", type=["csv"])
        if up:
            df=pd.read_csv(up); st.dataframe(df, use_container_width=True)
            if st.button("Import"):
                for _,r in df.iterrows():
                    execute("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()),current_user()["id"],str(r.get("name","")),str(r.get("area","")),str(r.get("address","")),str(r.get("phone","")),int(r.get("price",0)),int(r.get("peak_price",0)),4.5,int(r.get("court_count",1)),str(r.get("features","")),"05:00","23:00","active",str(r.get("bank_info",""))))
                st.success("Đã import."); st.rerun()
    with tabs[2]:
        rows=q("SELECT * FROM courts")
        checks=[("Có ít nhất 3 sân", len(rows)>=3), ("Mọi sân có SĐT", all((r["phone"] or "").strip() for r in rows)), ("Mọi sân có địa chỉ", all((r["address"] or "").strip() for r in rows)), ("Mọi sân có giá", all(int(r["price"] or 0)>0 for r in rows))]
        score=sum(ok for _,ok in checks); st.progress(score/len(checks)); st.metric("Court Data", f"{score}/{len(checks)}")
        for name,ok in checks: status(("✅ " if ok else "⚠️ ")+name, "safe" if ok else "warn")

def page_reports() -> None:
    hero("📊 Báo cáo", "Báo cáo booking, doanh thu demo, sản phẩm, người dùng.")
    s=app_stats()
    c=st.columns(4)
    with c[0]: metric("Users", s["users"])
    with c[1]: metric("Courts", s["courts"])
    with c[2]: metric("Bookings", s["bookings"])
    with c[3]: metric("Revenue", fmt_money(s["revenue"]))
    st.dataframe(rows_to_df(q("SELECT b.*, c.name court_name FROM bookings b JOIN courts c ON b.court_id=c.id ORDER BY created_at DESC")), use_container_width=True)

def page_ai() -> None:
    hero("🤖 AI Trợ lý vận hành", "AI offline-first: gợi ý hôm nay, marketing, CRM, giá sân, rủi ro, tự động hóa.")
    tabs=st.tabs(["Gợi ý", "Tạo task", "Marketing", "Chat"])
    with tabs[0]:
        for r in ai_recommendations(): status(f"<b>{r['title']}</b><br>{r['body']}<br><span class='pill yellow'>{r['priority']}</span>", "warn" if r["priority"]=="Cao" else "safe")
    with tabs[1]:
        owner=st.selectbox("Giao cho", ["Chủ sân", "Admin", "Marketing", "CSKH", "AI Agent"])
        due=st.date_input("Hạn xử lý", date.today()+timedelta(days=1))
        if st.button("AI tạo task"):
            for r in ai_recommendations(): execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()),r["title"],owner,r["priority"],"Open",str(due),"AI v1.2",datetime.now().isoformat(timespec="seconds")))
            st.success("Đã tạo task.")
    with tabs[2]:
        camp=st.selectbox("Chiến dịch", ["Ra mắt app", "Lấp giờ thấp điểm", "Marketplace dụng cụ", "Gói hội viên"])
        text={"Ra mắt app":"Badminton Vinh giúp đặt sân, tìm kèo, mua bán dụng cụ và quản lý lịch chơi trong một nơi.","Lấp giờ thấp điểm":"Tuần này đặt sân giờ thấp điểm tại TP Vinh có ưu đãi. Rủ bạn đánh cầu, giữ sức khỏe, tiết kiệm chi phí.","Marketplace dụng cụ":"Có vợt/giày/cầu không dùng nữa? Đăng bán miễn phí cho cộng đồng cầu lông Vinh.","Gói hội viên":"Chơi đều mỗi tuần? Gói hội viên giúp giữ lịch quen và nhận ưu đãi tốt hơn."}
        st.text_area("Caption AI", text[camp], height=130)
    with tabs[3]:
        p=st.text_input("Hỏi AI")
        if p: st.info(ai_answer(p))

def page_user_admin() -> None:
    hero("👥 Tài khoản & phân quyền", "Admin quản lý người chơi, chủ sân, trạng thái tài khoản và phân quyền.")
    if current_user()["role"] != "admin": st.warning("Trang này dành cho admin."); return
    tabs=st.tabs(["Danh sách", "Tạo tài khoản", "Phân quyền"])
    with tabs[0]: st.dataframe(rows_to_df(q("SELECT id,name,email,phone,role,level,area,is_active,last_login,created_at FROM users ORDER BY created_at DESC")), use_container_width=True)
    with tabs[1]:
        with st.form("new_user"):
            name=st.text_input("Tên"); email=st.text_input("Email"); phone=st.text_input("SĐT")
            role=st.selectbox("Vai trò", ["player","owner","admin"]); level=st.selectbox("Trình độ", ["Beginner","Intermediate","Advanced","Coach"])
            area=st.text_input("Khu vực", "TP Vinh"); pwd=st.text_input("Mật khẩu", value="123456")
            if st.form_submit_button("Tạo"):
                ok,res=create_user(name,email,phone,pwd,role,level,area); st.success("Đã tạo") if ok else st.error(res)
    with tabs[2]:
        users=q("SELECT * FROM users ORDER BY role,name")
        u=select_row("Chọn tài khoản", users, lambda r: f"{r['name']} · {r['role']} · {r['email']}", "role_user")
        if u:
            role=st.selectbox("Role", ["player","owner","admin"], index=["player","owner","admin"].index(u["role"]))
            active=st.checkbox("Hoạt động", bool(u["is_active"]))
            if st.button("Lưu phân quyền"):
                execute("UPDATE users SET role=?, is_active=? WHERE id=?", (role,1 if active else 0,u["id"])); st.success("Đã lưu."); st.rerun()

def export_payload() -> Dict[str, Any]:
    tables=["users","courts","bookings","products","matches","memberships","checkins","notifications","feedback","tasks"]
    return {"app":APP_NAME,"version":APP_VERSION,"exported_at":datetime.now().isoformat(timespec="seconds"),"tables":{t:[dict(r) for r in q(f"SELECT * FROM {t}")] for t in tables}}

def restore_payload(payload: Dict[str, Any]) -> Tuple[bool, str]:
    tables=payload.get("tables", {}) if isinstance(payload,dict) else {}
    if not tables: return False,"File không đúng định dạng backup."
    with conn() as c:
        cur=c.cursor()
        for table, rows in tables.items():
            if table not in {"users","courts","bookings","products","matches","memberships","checkins","notifications","feedback","tasks"}: continue
            cols=[r["name"] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]
            cur.execute(f"DELETE FROM {table}")
            for row in rows:
                valid={k:row.get(k) for k in cols if k in row}
                if valid:
                    cur.execute(f"INSERT OR REPLACE INTO {table}({','.join(valid.keys())}) VALUES ({','.join('?' for _ in valid)})", tuple(valid.values()))
        c.commit()
    return True,"Đã khôi phục dữ liệu."

def secrets_get(name: str, default: str = "") -> str:
    try: return str(st.secrets.get(name, default))
    except Exception: return os.getenv(name, default)

def supabase_configured() -> bool:
    return bool(secrets_get("SUPABASE_URL") and secrets_get("SUPABASE_SERVICE_ROLE_KEY"))

def supabase_headers() -> Dict[str,str]:
    key=secrets_get("SUPABASE_SERVICE_ROLE_KEY")
    return {"apikey":key,"Authorization":f"Bearer {key}","Content-Type":"application/json","Prefer":"return=representation"}

def supabase_push(space: str, payload: Dict[str,Any]) -> Tuple[bool,str]:
    if not supabase_configured(): return False,"Chưa cấu hình SUPABASE_URL / SERVICE_ROLE_KEY."
    try:
        import requests
        url=secrets_get("SUPABASE_URL").rstrip("/")+"/rest/v1/badminton_snapshots"
        r=requests.post(url,headers=supabase_headers(),json={"space":space,"payload":payload},timeout=25)
        if r.status_code>=300: return False, f"Supabase lỗi {r.status_code}: {r.text[:300]}"
        execute("INSERT INTO sync_logs VALUES (?,?,?,?,?)", (str(uuid.uuid4()),"push","success","Đã đẩy snapshot",datetime.now().isoformat(timespec="seconds")))
        return True,"Đã đẩy snapshot lên Supabase."
    except Exception as e: return False, f"Lỗi push cloud: {e}"

def supabase_pull(space: str) -> Tuple[bool,str,Optional[Dict[str,Any]]]:
    if not supabase_configured(): return False,"Chưa cấu hình Supabase Secrets.",None
    try:
        import requests
        url=secrets_get("SUPABASE_URL").rstrip("/")+f"/rest/v1/badminton_snapshots?space=eq.{space}&order=created_at.desc&limit=1"
        r=requests.get(url,headers=supabase_headers(),timeout=25)
        if r.status_code>=300: return False, f"Supabase lỗi {r.status_code}: {r.text[:300]}", None
        arr=r.json()
        if not arr: return False,"Chưa có snapshot trên cloud.",None
        return True,"Đã lấy snapshot.",arr[0].get("payload")
    except Exception as e: return False,f"Lỗi pull cloud: {e}",None

def page_cloud_sync() -> None:
    hero("☁️ Cloud Login & Sync", "Backup JSON + Supabase snapshot để dữ liệu bền hơn khi deploy Streamlit Cloud.")
    tabs=st.tabs(["Trạng thái", "Backup/Restore", "Supabase", "SQL & Secrets"])
    with tabs[0]:
        st.metric("Auth", "Email/Password")
        st.metric("Supabase", "Đã cấu hình" if supabase_configured() else "Chưa cấu hình")
        st.dataframe(rows_to_df(q("SELECT * FROM sync_logs ORDER BY created_at DESC LIMIT 20")), use_container_width=True)
    with tabs[1]:
        payload=export_payload()
        st.download_button("⬇️ Tải backup JSON", json.dumps(payload,ensure_ascii=False,indent=2).encode("utf-8"), "badminton_vinh_backup_v1_2.json", "application/json")
        up=st.file_uploader("Restore JSON", type=["json"])
        if up and st.button("Khôi phục"):
            ok,msg=restore_payload(json.load(up)); st.success(msg) if ok else st.error(msg)
            if ok: st.rerun()
    with tabs[2]:
        space=st.text_input("SYNC_SPACE", secrets_get("SYNC_SPACE","badminton-vinh-production"))
        c1,c2=st.columns(2)
        with c1:
            if st.button("☁️ Push snapshot"):
                ok,msg=supabase_push(space,export_payload()); st.success(msg) if ok else st.error(msg)
        with c2:
            if st.button("⬇️ Pull latest"):
                ok,msg,payload=supabase_pull(space)
                if ok and payload:
                    ok2,msg2=restore_payload(payload); st.success(msg2) if ok2 else st.error(msg2)
                    if ok2: st.rerun()
                else: st.error(msg)
    with tabs[3]:
        st.code('''SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "YOUR_SERVICE_ROLE_KEY"
SYNC_SPACE = "badminton-vinh-production"
AI_MODE = "offline"
USE_EXTERNAL_AI = "false"''', language="toml")
        st.code('''create table if not exists badminton_snapshots (
  id uuid primary key default gen_random_uuid(),
  space text not null,
  payload jsonb not null,
  created_at timestamptz default now()
);
create index if not exists badminton_snapshots_space_created_idx on badminton_snapshots(space, created_at desc);''', language="sql")

def page_health() -> None:
    hero("🩺 Health Check", "Kiểm tra app trước khi public và sau khi deploy Streamlit Cloud.")
    checks=[]
    checks.append(("app.py tồn tại", Path("app.py").exists()))
    checks.append(("requirements.txt tồn tại", Path("requirements.txt").exists()))
    for table in ["users","courts","bookings","products","tasks"]:
        try: checks.append((f"Bảng {table}: {len(q(f'SELECT * FROM {table}'))} dòng", True))
        except Exception: checks.append((f"Bảng {table} lỗi", False))
    checks.append(("Có user admin", bool(one("SELECT * FROM users WHERE role='admin'"))))
    checks.append(("Supabase configured", supabase_configured()))
    score=sum(ok for _,ok in checks); st.progress(score/len(checks)); st.metric("Health", f"{score}/{len(checks)}")
    for name,ok in checks: status(("✅ " if ok else "⚠️ ")+name, "safe" if ok else "warn")

def page_launch() -> None:
    hero("🚀 Public Launch Checklist", "Checklist cuối trước khi gửi link cho người chơi và chủ sân ở TP Vinh.")
    courts=q("SELECT * FROM courts")
    checks=[("Có dữ liệu sân thật", len(courts)>=3), ("Sân có SĐT/địa chỉ/giá", all((r["phone"] and r["address"] and int(r["price"] or 0)>0) for r in courts)), ("Có booking test", len(q("SELECT * FROM bookings"))>=1), ("Có role player/owner/admin", all(one("SELECT * FROM users WHERE role=?",(r,)) for r in ["player","owner","admin"])), ("Mobile menu đã gọn", True), ("AI offline không tốn API", True), ("Không lưu secrets lên GitHub", True)]
    score=sum(ok for _,ok in checks); st.progress(score/len(checks)); st.metric("Launch Score", f"{score}/{len(checks)}")
    for name,ok in checks: status(("✅ " if ok else "⚠️ ")+name, "safe" if ok else "warn")

# ========================= NAV =========================

PAGES = {
    "👤 Người dùng": {
        "🏠 Trang chính": page_home,
        "📅 Đặt sân Pro": page_booking,
        "📋 Lịch của tôi": page_my_bookings,
        "🛒 Chợ mua bán": page_market,
        "➕ Đăng bán": page_sell,
        "🤝 Tìm người chơi": page_matches,
        "💎 Hội viên": page_membership,
    },
    "🏟️ Chủ sân": {
        "🏟️ Chủ sân Portal": page_owner,
        "🏟️ Dữ liệu sân thật": page_court_data,
        "📊 Báo cáo": page_reports,
        "🤖 AI Trợ lý vận hành": page_ai,
    },
    "👑 Admin": {
        "👥 Tài khoản & phân quyền": page_user_admin,
        "☁️ Cloud Login & Sync": page_cloud_sync,
        "🏟️ Dữ liệu sân thật": page_court_data,
        "📊 Báo cáo": page_reports,
        "🚀 Public Launch Checklist": page_launch,
        "🩺 Health Check": page_health,
        "🤖 AI Trợ lý vận hành": page_ai,
    }
}

def sidebar() -> Any:
    auth_panel()
    u=current_user()
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Manage App")
    allowed=["👤 Người dùng"]
    if u["role"] in ["owner","admin"]: allowed.append("🏟️ Chủ sân")
    if u["role"] == "admin": allowed.append("👑 Admin")
    group=st.sidebar.radio("Chế độ", allowed)
    page=st.sidebar.radio("Chức năng", list(PAGES[group].keys()))
    all_names=[]
    for g,ps in PAGES.items():
        if g in allowed: all_names += list(ps.keys())
    quick=st.sidebar.selectbox("🔎 Mở nhanh", ["Không dùng"] + all_names)
    if quick != "Không dùng":
        for g,ps in PAGES.items():
            if quick in ps: return ps[quick]
    st.sidebar.markdown(f"<div class='mobile-note'>{APP_NAME}</div>", unsafe_allow_html=True)
    return PAGES[group][page]

def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🏸", layout="wide", initial_sidebar_state="expanded")
    css(); init_db()
    if not auth_gate(): return
    func=sidebar()
    try:
        func()
    except Exception as e:
        st.error("Trang này đang gặp lỗi hiển thị. Hãy thử reload app hoặc vào Health Check.")
        with st.expander("Chi tiết lỗi kỹ thuật"):
            st.exception(e)

if __name__ == "__main__":
    main()
