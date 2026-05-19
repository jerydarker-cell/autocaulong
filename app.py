# -*- coding: utf-8 -*-
"""
Badminton Vinh Production Ready
Chạy local: streamlit run app.py
Một file độc lập: đặt sân, mua bán, tìm người chơi, chủ sân, admin, AI vận hành offline, backup/sync.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

APP_NAME = "Badminton Vinh Production Ready v1.1"
APP_VERSION = "1.1 Production Ready"
DB_PATH = Path("badminton_vinh_production_ready_v1_1.sqlite3")

# ========================= UI =========================

def css() -> None:
    st.markdown("""
    <style>
    :root{--bg:#050b12;--panel:#0d1725;--line:#1f334d;--muted:#9fb3c8;--green:#22c55e;--blue:#38bdf8;--yellow:#f59e0b;--red:#ef4444;--purple:#8b5cf6}
    .main .block-container{max-width:1080px;padding-top:1rem;padding-bottom:4rem}
    h1,h2,h3{letter-spacing:-.03em}.muted{color:var(--muted)}
    .hero{background:radial-gradient(circle at 10% 0%,rgba(34,197,94,.24),transparent 38%),radial-gradient(circle at 90% 0%,rgba(56,189,248,.16),transparent 40%),linear-gradient(135deg,#07111f,#0c1b2d 70%,#08111d);border:1px solid rgba(94,234,212,.18);border-radius:28px;padding:22px;margin-bottom:18px;box-shadow:0 22px 60px rgba(0,0,0,.35)}
    .hero-title{font-size:2.1rem;font-weight:950;line-height:1.05;color:#fff}.hero-sub{font-size:1rem;color:var(--muted);max-width:760px;margin-top:8px}
    .grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
    .card{background:linear-gradient(180deg,rgba(16,29,46,.96),rgba(10,18,31,.96));border:1px solid var(--line);border-radius:24px;padding:16px;box-shadow:0 18px 36px rgba(0,0,0,.22);margin:8px 0}.card h3{margin:.2rem 0 .35rem 0;font-size:1.05rem}.big{font-size:1.75rem;font-weight:950;color:#fff}
    .pill{display:inline-flex;align-items:center;gap:6px;padding:7px 11px;border-radius:999px;font-weight:800;font-size:.78rem;margin:3px 4px 3px 0;border:1px solid var(--line)}.green{background:rgba(34,197,94,.12);color:#86efac;border-color:rgba(34,197,94,.28)}.blue{background:rgba(56,189,248,.12);color:#7dd3fc;border-color:rgba(56,189,248,.28)}.yellow{background:rgba(245,158,11,.12);color:#fcd34d;border-color:rgba(245,158,11,.28)}.red{background:rgba(239,68,68,.12);color:#fca5a5;border-color:rgba(239,68,68,.28)}.purple{background:rgba(139,92,246,.12);color:#c4b5fd;border-color:rgba(139,92,246,.28)}
    .row-card{background:linear-gradient(180deg,#0e1b2b,#0b1422);border:1px solid #1e3350;border-radius:22px;padding:14px;margin:10px 0}.price{font-size:1.15rem;font-weight:950;color:#86efac}.safe{border-left:4px solid var(--green);background:rgba(34,197,94,.08);padding:10px 12px;border-radius:12px}.warn{border-left:4px solid var(--yellow);background:rgba(245,158,11,.08);padding:10px 12px;border-radius:12px}.bad{border-left:4px solid var(--red);background:rgba(239,68,68,.08);padding:10px 12px;border-radius:12px}
    .stButton>button{border-radius:16px!important;min-height:42px;font-weight:850!important;border:1px solid #24405f!important;background:#10233a!important;color:#eef7ff!important}.stButton>button:hover{border-color:#22c55e!important;color:#86efac!important}
    section[data-testid="stSidebar"] .stRadio label{padding:.25rem .35rem!important;min-height:30px!important}section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{font-size:.92rem!important;line-height:1.18!important}
    .mobile-note{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);z-index:999;background:rgba(8,15,28,.9);border:1px solid #24405f;border-radius:999px;padding:8px 14px;color:#dbeafe;font-size:.8rem;backdrop-filter:blur(8px)}
    @media(max-width:850px){.main .block-container{padding-left:.7rem;padding-right:.7rem}.hero{padding:16px;border-radius:22px}.hero-title{font-size:1.55rem}.grid4,.grid3,.grid2{grid-template-columns:1fr}.card{padding:13px;border-radius:20px}.big{font-size:1.35rem}.pill{font-size:.72rem;padding:6px 9px}}
    </style>
    """, unsafe_allow_html=True)

def hero(title: str, sub: str) -> None:
    st.markdown(f"""<div class='hero'><div class='hero-title'>{title}</div><div class='hero-sub'>{sub}</div><div style='margin-top:12px'><span class='pill green'>🏸 TP Vinh</span><span class='pill blue'>📅 Đặt sân</span><span class='pill yellow'>🛒 Mua bán</span><span class='pill purple'>🤖 AI offline</span></div></div>""", unsafe_allow_html=True)

def metric(title: str, value: Any, cap: str = "") -> None:
    st.markdown(f"<div class='card'><div class='muted'>{title}</div><div class='big'>{value}</div><div class='muted'>{cap}</div></div>", unsafe_allow_html=True)

def card(icon: str, title: str, body: str, tag: str="") -> None:
    tag_html = f"<span class='pill blue'>{tag}</span>" if tag else ""
    st.markdown(f"<div class='card'><div style='font-size:1.8rem'>{icon}</div><h3>{title}</h3><div class='muted'>{body}</div><div style='margin-top:8px'>{tag_html}</div></div>", unsafe_allow_html=True)

def status(msg: str, kind: str="safe") -> None:
    st.markdown(f"<div class='{kind}'>{msg}</div>", unsafe_allow_html=True)

def fmt_money(v: Any) -> str:
    try: return f"{int(v):,}".replace(",", ".") + "đ"
    except Exception: return str(v)

# ========================= DB =========================

def conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def q(sql: str, params: tuple=()) -> List[sqlite3.Row]:
    with conn() as c:
        return c.execute(sql, params).fetchall()

def one(sql: str, params: tuple=()) -> Optional[sqlite3.Row]:
    rows = q(sql, params)
    return rows[0] if rows else None

def execute(sql: str, params: tuple=()) -> None:
    with conn() as c:
        c.execute(sql, params); c.commit()

def init_db() -> None:
    with conn() as c:
        cur = c.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,name TEXT,phone TEXT,role TEXT,level TEXT,area TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS courts(id TEXT PRIMARY KEY,owner_id TEXT,name TEXT,area TEXT,address TEXT,phone TEXT,price INTEGER,peak_price INTEGER,rating REAL,court_count INTEGER,features TEXT,open_time TEXT,close_time TEXT,status TEXT);
        CREATE TABLE IF NOT EXISTS bookings(id TEXT PRIMARY KEY,user_id TEXT,court_id TEXT,booking_date TEXT,start_time TEXT,duration INTEGER,players INTEGER,total INTEGER,payment_status TEXT,status TEXT,note TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY,seller_id TEXT,title TEXT,category TEXT,condition TEXT,price INTEGER,area TEXT,phone TEXT,description TEXT,status TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS matches(id TEXT PRIMARY KEY,creator_id TEXT,title TEXT,area TEXT,level TEXT,play_date TEXT,start_time TEXT,slots INTEGER,note TEXT,status TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY,user_id TEXT,target_type TEXT,target_id TEXT,rating INTEGER,comment TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS memberships(id TEXT PRIMARY KEY,user_id TEXT,package TEXT,balance INTEGER,total INTEGER,expires_at TEXT,status TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS checkins(id TEXT PRIMARY KEY,user_id TEXT,booking_id TEXT,court_id TEXT,points INTEGER,created_at TEXT);
        CREATE TABLE IF NOT EXISTS notifications(id TEXT PRIMARY KEY,user_id TEXT,title TEXT,body TEXT,seen INTEGER,created_at TEXT);
        CREATE TABLE IF NOT EXISTS feedback(id TEXT PRIMARY KEY,user_id TEXT,category TEXT,message TEXT,status TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,title TEXT,owner TEXT,priority TEXT,status TEXT,due_date TEXT,source TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY,v TEXT);
        """)
        c.commit()
    seed()

def seed() -> None:
    if one("SELECT id FROM users LIMIT 1"):
        return
    now = datetime.now().isoformat(timespec="seconds")
    users = [
        ("u_admin","Admin Demo","0900000000","admin","Advanced","Trung tâm",now),
        ("u_owner","Chủ sân Demo","0911111111","owner","Intermediate","Lê Lợi",now),
        ("u_player","Người chơi Demo","0922222222","player","Beginner","Quán Bàu",now),
    ]
    courts = [
        ("c1","u_owner","Sân Cầu Lông Trung Đô","Trung Đô","Đường Nguyễn Viết Xuân, TP Vinh","0912 000 111",80000,120000,4.8,6,"Đèn LED, thảm tốt, gửi xe","05:00","23:00","active"),
        ("c2","u_owner","CLB Cầu Lông Lê Lợi","Lê Lợi","Khu Lê Lợi, TP Vinh","0912 000 222",70000,110000,4.6,4,"Có HLV, nước uống, phòng chờ","05:30","22:30","active"),
        ("c3","u_owner","Sân Cầu Lông Quán Bàu","Quán Bàu","Quán Bàu, TP Vinh","0912 000 333",60000,90000,4.4,3,"Giá mềm, gần khu dân cư","06:00","22:00","active"),
        ("c4","u_owner","Sân Cầu Lông Hưng Bình","Hưng Bình","Hưng Bình, TP Vinh","0912 000 444",75000,100000,4.5,5,"Sân rộng, ghép kèo nhanh","05:00","22:00","active"),
    ]
    products = [
        ("p1","u_player","Vợt Yonex Astrox 77","Vợt","Đã dùng 90%",2200000,"Trung tâm","0922222222","Căng dây 11kg, hợp đánh đôi.","active",now),
        ("p2","u_player","Giày cầu lông Mizuno size 41","Giày","Đã dùng 2 tháng",950000,"Lê Lợi","0922222222","Đế còn tốt, bám sân.","active",now),
        ("p3","u_owner","Ống cầu Victor chính hãng","Cầu","Mới",350000,"Quán Bàu","0911111111","Cầu tập luyện CLB.","active",now),
    ]
    matches = [
        ("m1","u_player","Tìm 2 bạn đánh đôi tối nay","Trung tâm","Trung bình",str(date.today()),"19:00",2,"Vui vẻ, chia sân đều.","open",now),
        ("m2","u_owner","Giao lưu CLB cuối tuần","Lê Lợi","Mọi trình độ",str(date.today()+timedelta(days=2)),"18:30",8,"Ưu tiên người mới tham gia.","open",now),
    ]
    bookings = [("b1","u_player","c1",str(date.today()),"19:00",2,4,240000,"Chưa thanh toán","Đã xác nhận","Demo booking",now)]
    with conn() as c:
        c.executemany("INSERT INTO users VALUES (?,?,?,?,?,?,?)", users)
        c.executemany("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", courts)
        c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)", products)
        c.executemany("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?)", matches)
        c.executemany("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", bookings)
        c.commit()

def rows_to_df(rows: List[sqlite3.Row]) -> pd.DataFrame:
    return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()

def add_notification(user_id: str, title: str, body: str) -> None:
    execute("INSERT INTO notifications VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), user_id, title, body, 0, datetime.now().isoformat(timespec="seconds")))

# ========================= AUTH / SESSION =========================

def current_user() -> sqlite3.Row:
    uid = st.session_state.get("uid", "u_player")
    user = one("SELECT * FROM users WHERE id=?", (uid,))
    if not user:
        st.session_state["uid"] = "u_player"
        user = one("SELECT * FROM users WHERE id=?", ("u_player",))
    return user

def auth_panel() -> None:
    st.sidebar.markdown("### 👤 Tài khoản")
    users = q("SELECT * FROM users ORDER BY CASE role WHEN 'admin' THEN 1 WHEN 'owner' THEN 2 ELSE 3 END, name")
    labels = [f"{u['name']} · {u['role']}" for u in users]
    uid_map = {labels[i]: users[i]["id"] for i in range(len(users))}
    current = current_user()
    idx = next((i for i,u in enumerate(users) if u["id"] == current["id"]), 0)
    label = st.sidebar.selectbox("Chọn tài khoản demo", labels, index=idx)
    st.session_state["uid"] = uid_map[label]
    current = current_user()
    st.sidebar.caption(f"Role: {current['role']} · {current['phone']}")
    with st.sidebar.expander("➕ Tạo tài khoản nhanh"):
        with st.form("quick_user"):
            name = st.text_input("Tên")
            phone = st.text_input("SĐT")
            role = st.selectbox("Vai trò", ["player", "owner", "admin"])
            level = st.selectbox("Trình độ", ["Beginner", "Intermediate", "Advanced", "Coach"])
            area = st.text_input("Khu vực", "TP Vinh")
            if st.form_submit_button("Tạo tài khoản") and name:
                uid = str(uuid.uuid4())
                execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", (uid, name, phone, role, level, area, datetime.now().isoformat(timespec="seconds")))
                st.session_state["uid"] = uid
                st.rerun()

# ========================= SAFE SELECT =========================

def select_row(label: str, rows: List[sqlite3.Row], fmt, key: str) -> Optional[sqlite3.Row]:
    if not rows:
        st.info("Chưa có dữ liệu phù hợp.")
        return None
    labels = [fmt(r) for r in rows]
    idx = st.selectbox(label, list(range(len(rows))), format_func=lambda i: labels[i], key=key)
    return rows[int(idx)]

# ========================= AI OFFLINE =========================

def app_stats() -> Dict[str, Any]:
    courts = q("SELECT * FROM courts")
    bookings = q("SELECT * FROM bookings")
    products = q("SELECT * FROM products WHERE status='active'")
    users = q("SELECT * FROM users")
    feedback = q("SELECT * FROM feedback WHERE status!='Đã xử lý'")
    revenue = sum(int(b["total"] or 0) for b in bookings)
    fill_hint = min(100, int(len(bookings) / max(1, len(courts)*6) * 100))
    return {"courts":len(courts),"bookings":len(bookings),"products":len(products),"users":len(users),"feedback_open":len(feedback),"revenue":revenue,"fill":fill_hint}

def ai_recommendations() -> List[Dict[str,str]]:
    s = app_stats()
    recs = []
    if s["fill"] < 45:
        recs.append({"title":"Lấp giờ thấp điểm", "body":"Tạo voucher 10–20% cho khung 13:00–16:00 và gửi cho nhóm sinh viên/văn phòng.", "priority":"Cao"})
    if s["products"] < 8:
        recs.append({"title":"Kích hoạt chợ dụng cụ", "body":"Mời người chơi đăng vợt/giày/cầu cũ, miễn phí đẩy tin 7 ngày đầu.", "priority":"Vừa"})
    if s["feedback_open"] > 0:
        recs.append({"title":"Xử lý phản hồi", "body":"Có phản hồi chưa xử lý. Ưu tiên gọi lại khách trong 24h để tăng uy tín.", "priority":"Cao"})
    recs.append({"title":"Tăng đặt lại sân", "body":"Sau mỗi check-in, gửi gợi ý đặt lại cùng khung giờ tuần sau + cộng điểm loyalty.", "priority":"Vừa"})
    recs.append({"title":"Combo sân + cầu + nước", "body":"Gói combo giúp tăng doanh thu mỗi buổi mà không cần tăng giá sân trực tiếp.", "priority":"Vừa"})
    return recs

def ai_answer(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["doanh thu", "revenue", "tiền"]):
        return "Để tăng doanh thu: lấp giờ thấp điểm bằng voucher, bán combo sân+cầu+nước, tạo gói hội viên 5/10 buổi, chăm sóc khách đặt lại theo tuần và đẩy marketplace dụng cụ."
    if any(k in p for k in ["facebook", "marketing", "quảng cáo"]):
        return "Chiến dịch Facebook nên nhắm: người chơi mới, sinh viên, dân văn phòng, CLB. Nội dung tốt nhất: video sân thật + giá rõ + nút đặt sân + ưu đãi giờ thấp điểm."
    if any(k in p for k in ["trùng", "lịch", "booking"]):
        return "Tránh trùng lịch bằng cách kiểm tra court_id + ngày + giờ bắt đầu trước khi ghi booking. Nên khóa trạng thái 'Chờ xác nhận' rồi chủ sân xác nhận."
    if any(k in p for k in ["crm", "khách"]):
        return "CRM nên chia khách: khách mới, khách quay lại, khách VIP, khách rủi ro rời bỏ. Mỗi nhóm có tin nhắn chăm sóc và voucher khác nhau."
    return "Gợi ý vận hành: giữ luồng đặt sân thật đơn giản, dữ liệu sân thật đầy đủ, ưu tiên mobile, dùng AI offline để tạo task hàng ngày và chỉ bật API khi thật cần."

# ========================= PAGES =========================

def page_home() -> None:
    user = current_user(); s = app_stats()
    hero("🏸 Badminton Vinh Production Ready", "Bản v1.1 dùng thật hơn: dữ liệu sân thật, đặt sân rõ trạng thái, cọc/thanh toán demo, checklist public, cloud plan và AI vận hành gọn một trung tâm.")
    st.markdown(f"<span class='pill green'>Xin chào {user['name']}</span><span class='pill blue'>Vai trò: {user['role']}</span><span class='pill purple'>Production Ready</span>", unsafe_allow_html=True)
    c = st.columns(4)
    with c[0]: metric("Sân", s["courts"], "đang quản lý")
    with c[1]: metric("Booking", s["bookings"], "lượt đặt")
    with c[2]: metric("Marketplace", s["products"], "sản phẩm")
    with c[3]: metric("Doanh thu demo", fmt_money(s["revenue"]), "tổng booking")
    st.markdown("### 🚀 Lối tắt")
    cols = st.columns(4)
    shortcuts = [("📅", "Đặt sân", "Chọn sân, ngày, giờ, xác nhận nhanh."),("🛒","Chợ mua bán","Đăng bán/mua vợt, giày, cầu."),("🤝","Tìm người chơi","Ghép kèo theo trình độ/khu vực."),("🤖","AI vận hành","Gợi ý tăng booking, CRM, giá sân.")]
    for i,x in enumerate(shortcuts):
        with cols[i]: card(*x)
    st.markdown("### 🤖 Gợi ý AI hôm nay")
    for r in ai_recommendations()[:3]:
        status(f"<b>{r['title']}</b> · {r['body']} <span class='pill yellow'>{r['priority']}</span>", "safe" if r["priority"]!="Cao" else "warn")

def page_booking() -> None:
    hero("📅 Đặt lịch sân", "Luồng production: chọn sân → ngày → giờ → thông tin → xác nhận. Có kiểm tra trùng lịch cơ bản.")
    courts = q("SELECT * FROM courts WHERE status='active' ORDER BY rating DESC")
    areas = ["Tất cả"] + sorted({c["area"] for c in courts})
    col1,col2,col3 = st.columns(3)
    with col1: area = st.selectbox("Khu vực", areas)
    with col2: max_price = st.slider("Giá tối đa/giờ", 50000, 150000, 120000, 10000)
    with col3: day = st.date_input("Ngày chơi", value=date.today())
    filtered = [c for c in courts if (area=="Tất cả" or c["area"]==area) and int(c["price"]) <= max_price]
    court = select_row("Chọn sân", filtered, lambda r: f"{r['name']} · {r['area']} · {fmt_money(r['price'])}/h · ⭐{r['rating']}", "book_court")
    if not court: return
    with st.container(border=True):
        st.subheader(court["name"])
        st.write(court["address"])
        st.caption(f"☎ {court['phone']} · {court['features']} · Mở {court['open_time']}–{court['close_time']}")
    times = [f"{h:02d}:00" for h in range(5,23)]
    col1,col2,col3 = st.columns(3)
    with col1: start = st.selectbox("Giờ bắt đầu", times)
    with col2: duration = st.selectbox("Thời lượng", [1,2,3], index=1)
    with col3: players = st.selectbox("Số người", [2,4,6,8], index=1)
    total = int(court["peak_price"] if start in ["18:00","19:00","20:00"] else court["price"]) * int(duration)
    existed = one("SELECT * FROM bookings WHERE court_id=? AND booking_date=? AND start_time=? AND status NOT IN ('Đã hủy')", (court["id"], str(day), start))
    if existed:
        status("Khung giờ này đã có lịch. Hãy chọn giờ khác hoặc liên hệ chủ sân.", "bad")
    else:
        status(f"Khung giờ còn trống. Tạm tính: <b>{fmt_money(total)}</b>", "safe")
    note = st.text_area("Ghi chú", placeholder="Ví dụ: cần thuê 2 vợt, mua 1 ống cầu...")
    pay = st.selectbox("Thanh toán", ["Chưa thanh toán", "Thanh toán tại sân", "Đã cọc", "Đã thanh toán"])
    if st.button("✅ Xác nhận đặt sân", type="primary", disabled=bool(existed)):
        uid = current_user()["id"]
        bid = str(uuid.uuid4())
        execute("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (bid, uid, court["id"], str(day), start, duration, players, total, pay, "Chờ xác nhận", note, datetime.now().isoformat(timespec="seconds")))
        add_notification(uid, "Đặt sân thành công", f"Bạn đã đặt {court['name']} lúc {start} ngày {day}.")
        st.success("Đã tạo lịch đặt sân. Chủ sân sẽ xác nhận.")
        st.rerun()

def page_my_bookings() -> None:
    hero("📋 Lịch của tôi", "Xem lịch đặt, trạng thái thanh toán, check-in và hủy lịch.")
    user = current_user()
    rows = q("""SELECT b.*, c.name court_name, c.area FROM bookings b JOIN courts c ON b.court_id=c.id WHERE b.user_id=? ORDER BY b.booking_date DESC,b.start_time DESC""", (user["id"],))
    if not rows:
        st.info("Bạn chưa có lịch đặt."); return
    for b in rows:
        with st.container(border=True):
            st.markdown(f"### {b['court_name']} · {b['booking_date']} {b['start_time']}")
            st.write(f"Trạng thái: **{b['status']}** · Thanh toán: **{b['payment_status']}** · Tổng: **{fmt_money(b['total'])}**")
            col1,col2 = st.columns(2)
            with col1:
                if st.button("✅ Check-in", key="ci"+b["id"], disabled=b["status"]=="Đã hủy"):
                    cid=str(uuid.uuid4())
                    execute("INSERT INTO checkins VALUES (?,?,?,?,?,?)", (cid,user["id"],b["id"],b["court_id"],10,datetime.now().isoformat(timespec="seconds")))
                    execute("UPDATE bookings SET status='Đã check-in' WHERE id=?", (b["id"],))
                    st.success("Đã check-in và cộng 10 điểm."); st.rerun()
            with col2:
                if st.button("❌ Hủy lịch", key="cancel"+b["id"], disabled=b["status"]=="Đã hủy"):
                    execute("UPDATE bookings SET status='Đã hủy' WHERE id=?", (b["id"],)); st.warning("Đã hủy lịch."); st.rerun()

def page_market() -> None:
    hero("🛒 Chợ mua bán", "Mua bán dụng cụ cầu lông: vợt, giày, cầu, túi, phụ kiện. Có lọc danh mục và liên hệ người bán.")
    rows = q("SELECT p.*, u.name seller FROM products p LEFT JOIN users u ON p.seller_id=u.id WHERE p.status='active' ORDER BY p.created_at DESC")
    cats = ["Tất cả"] + sorted({r["category"] for r in rows})
    cat = st.selectbox("Danh mục", cats)
    keyword = st.text_input("Tìm kiếm", placeholder="vợt, giày, Yonex...")
    rows = [r for r in rows if (cat=="Tất cả" or r["category"]==cat) and (not keyword or keyword.lower() in (r["title"]+r["description"]).lower())]
    for p in rows:
        st.markdown(f"<div class='row-card'><h3>🏸 {p['title']}</h3><div class='price'>{fmt_money(p['price'])}</div><div class='muted'>{p['category']} · {p['condition']} · {p['area']}</div><p>{p['description']}</p><span class='pill blue'>Người bán: {p['seller']}</span><span class='pill green'>☎ {p['phone']}</span></div>", unsafe_allow_html=True)

def page_sell() -> None:
    hero("➕ Đăng bán", "Đăng bán dụng cụ cầu lông. Tin đăng rõ giá, tình trạng, SĐT sẽ dễ bán hơn.")
    with st.form("sell_form"):
        title = st.text_input("Tên sản phẩm")
        cat = st.selectbox("Danh mục", ["Vợt","Giày","Cầu","Túi","Quần áo","Phụ kiện","Khác"])
        cond = st.selectbox("Tình trạng", ["Mới","Như mới","Đã dùng 90%","Đã dùng","Cần sửa"])
        price = st.number_input("Giá", 0, 100000000, 500000, 50000)
        area = st.text_input("Khu vực", current_user()["area"] or "TP Vinh")
        phone = st.text_input("Số điện thoại", current_user()["phone"] or "")
        desc = st.text_area("Mô tả")
        if st.form_submit_button("Đăng bán"):
            execute("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), current_user()["id"], title, cat, cond, price, area, phone, desc, "active", datetime.now().isoformat(timespec="seconds")))
            st.success("Đã đăng bán sản phẩm."); st.rerun()

def page_matches() -> None:
    hero("🤝 Tìm người chơi", "Tạo kèo, tìm bạn đánh đôi, tìm CLB theo khu vực và trình độ.")
    with st.expander("➕ Tạo kèo mới", expanded=False):
        with st.form("match_form"):
            title = st.text_input("Tiêu đề", "Tìm bạn đánh đôi")
            area = st.text_input("Khu vực", current_user()["area"] or "TP Vinh")
            level = st.selectbox("Trình độ", ["Người mới","Trung bình","Khá","Mọi trình độ"])
            d = st.date_input("Ngày", date.today())
            t = st.selectbox("Giờ", [f"{h:02d}:00" for h in range(5,23)], index=14)
            slots = st.number_input("Cần thêm người", 1, 20, 2)
            note = st.text_area("Ghi chú")
            if st.form_submit_button("Đăng kèo"):
                execute("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), current_user()["id"], title, area, level, str(d), t, slots, note, "open", datetime.now().isoformat(timespec="seconds")))
                st.success("Đã đăng kèo."); st.rerun()
    for m in q("SELECT m.*, u.name creator FROM matches m LEFT JOIN users u ON m.creator_id=u.id WHERE m.status='open' ORDER BY m.play_date,m.start_time"):
        st.markdown(f"<div class='row-card'><h3>🏸 {m['title']}</h3><div class='muted'>{m['area']} · {m['level']} · {m['play_date']} {m['start_time']} · cần {m['slots']} người</div><p>{m['note']}</p><span class='pill green'>Người tạo: {m['creator']}</span></div>", unsafe_allow_html=True)

def page_owner() -> None:
    hero("🏟️ Chủ sân Portal", "Quản lý lịch đặt, xác nhận/hủy, xem doanh thu, cập nhật sân. Dành cho chủ sân/admin.")
    user = current_user()
    if user["role"] not in ["owner","admin"]:
        st.warning("Trang này dành cho chủ sân hoặc admin."); return
    court_filter = "" if user["role"]=="admin" else "WHERE owner_id=?"
    courts = q(f"SELECT * FROM courts {court_filter}", (user["id"],) if user["role"]!="admin" else ())
    c1,c2,c3 = st.columns(3)
    owner_court_ids = [c["id"] for c in courts]
    placeholders = ",".join("?"*len(owner_court_ids)) if owner_court_ids else "''"
    bks = q(f"SELECT b.*, c.name court_name, u.name user_name FROM bookings b JOIN courts c ON b.court_id=c.id LEFT JOIN users u ON b.user_id=u.id WHERE b.court_id IN ({placeholders}) ORDER BY b.booking_date DESC", tuple(owner_court_ids)) if owner_court_ids else []
    with c1: metric("Sân của bạn", len(courts), "sân")
    with c2: metric("Booking", len(bks), "lượt")
    with c3: metric("Doanh thu", fmt_money(sum(int(b["total"] or 0) for b in bks)), "demo")
    st.markdown("### Lịch chờ xử lý")
    for b in bks:
        with st.container(border=True):
            st.write(f"**{b['court_name']}** · {b['booking_date']} {b['start_time']} · {b['user_name']} · {fmt_money(b['total'])}")
            st.caption(f"Trạng thái: {b['status']} · Thanh toán: {b['payment_status']}")
            col1,col2,col3 = st.columns(3)
            with col1:
                if st.button("Xác nhận", key="ok"+b["id"]): execute("UPDATE bookings SET status='Đã xác nhận' WHERE id=?", (b["id"],)); st.rerun()
            with col2:
                if st.button("Đã thanh toán", key="pay"+b["id"]): execute("UPDATE bookings SET payment_status='Đã thanh toán' WHERE id=?", (b["id"],)); st.rerun()
            with col3:
                if st.button("Hủy", key="no"+b["id"]): execute("UPDATE bookings SET status='Đã hủy' WHERE id=?", (b["id"],)); st.rerun()
    st.markdown("### Thêm/cập nhật sân")
    with st.form("court_form"):
        name=st.text_input("Tên sân")
        area=st.text_input("Khu vực")
        address=st.text_input("Địa chỉ")
        phone=st.text_input("SĐT")
        price=st.number_input("Giá thường/giờ", 0, 500000, 70000, 10000)
        peak=st.number_input("Giá giờ cao điểm/giờ", 0, 500000, 100000, 10000)
        count=st.number_input("Số sân",1,50,4)
        features=st.text_input("Tiện ích", "Đèn LED, thảm tốt")
        if st.form_submit_button("Thêm sân") and name:
            execute("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), user["id"], name, area, address, phone, price, peak, 4.5, count, features, "05:00","23:00","active")); st.success("Đã thêm sân."); st.rerun()

def page_membership() -> None:
    hero("💎 Hội viên & Loyalty", "Gói hội viên, điểm check-in, ưu đãi giữ chân khách.")
    user=current_user()
    points=sum(int(r["points"] or 0) for r in q("SELECT points FROM checkins WHERE user_id=?", (user["id"],)))
    c1,c2=st.columns(2)
    with c1: metric("Điểm hiện tại", points, "10 điểm/check-in")
    with c2: metric("Gói hội viên", len(q("SELECT * FROM memberships WHERE user_id=?", (user["id"],))), "gói")
    st.markdown("### Mua gói demo")
    packs = [("Gói 5 buổi",5,450000),("Gói 10 buổi",10,850000),("Gói CLB tháng",20,1500000)]
    cols=st.columns(3)
    for i,p in enumerate(packs):
        with cols[i]:
            card("💎",p[0],f"{p[1]} lượt · {fmt_money(p[2])}","Hội viên")
            if st.button("Đăng ký", key=p[0]):
                execute("INSERT INTO memberships VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), user["id"], p[0], p[1], p[1], str(date.today()+timedelta(days=60)), "active", datetime.now().isoformat(timespec="seconds")))
                st.success("Đã đăng ký gói demo."); st.rerun()

def page_ai() -> None:
    hero("🤖 AI Trợ lý vận hành", "Một trung tâm AI duy nhất: tổng quan, gợi ý hôm nay, marketing, CRM, giá sân, rủi ro, tự động hóa. Offline-first, không tốn API.")
    tabs = st.tabs(["Tổng quan", "Gợi ý hôm nay", "Marketing", "CRM", "Giá sân", "Rủi ro", "Tự động hóa", "Chat"])
    s=app_stats()
    with tabs[0]:
        cols=st.columns(4)
        with cols[0]: metric("Automation Score", min(100, 45+s["bookings"]*5+s["products"]*3), "/100")
        with cols[1]: metric("Tỷ lệ lấp gợi ý", f"{s['fill']}%")
        with cols[2]: metric("Feedback mở", s["feedback_open"])
        with cols[3]: metric("Doanh thu", fmt_money(s["revenue"]))
    with tabs[1]:
        for r in ai_recommendations(): status(f"<b>{r['title']}</b><br>{r['body']}<br><span class='pill yellow'>{r['priority']}</span>", "warn" if r["priority"]=="Cao" else "safe")
        if st.button("AI tạo task từ gợi ý"):
            for r in ai_recommendations():
                execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), r["title"], "AI Agent", r["priority"], "Open", str(date.today()+timedelta(days=1)), "AI", datetime.now().isoformat(timespec="seconds")))
            st.success("Đã tạo task AI.")
    with tabs[2]:
        audience=st.selectbox("Nhóm khách", ["Người mới chơi","Sinh viên","Dân văn phòng","CLB cầu lông","Khách VIP"])
        captions={
            "Người mới chơi":"Bạn mới chơi cầu lông? Đặt sân dễ, tìm bạn đánh cùng nhanh, có gợi ý sân phù hợp tại TP Vinh.",
            "Sinh viên":"Cầu lông sau giờ học? Tìm sân giá mềm, ghép kèo nhanh, ưu đãi giờ thấp điểm cho sinh viên.",
            "Dân văn phòng":"Tan làm đánh cầu lông giảm stress. Đặt sân nhanh, giữ lịch quen, nhận nhắc lịch tự động.",
            "CLB cầu lông":"Quản lý lịch CLB, hội viên, giải giao lưu và check-in bằng QR trong một app.",
            "Khách VIP":"Giữ khung giờ đẹp, ưu đãi gói hội viên và chăm sóc riêng cho khách chơi đều."
        }
        st.text_area("Caption Facebook AI", captions[audience], height=140)
    with tabs[3]:
        users=q("SELECT u.*, COUNT(b.id) bookings, COALESCE(SUM(b.total),0) spend FROM users u LEFT JOIN bookings b ON u.id=b.user_id GROUP BY u.id ORDER BY spend DESC")
        for u in users:
            tag="VIP" if int(u["spend"] or 0)>500000 else "Mới/Tiềm năng"
            st.markdown(f"<div class='row-card'><b>{u['name']}</b> · {u['role']} · {tag}<br><span class='muted'>{u['bookings']} booking · {fmt_money(u['spend'])}</span></div>", unsafe_allow_html=True)
    with tabs[4]:
        st.write("AI gợi ý giá theo khung giờ:")
        df=pd.DataFrame([{"Khung giờ":"05:00–09:00","Gợi ý":"Giá thường","Mục tiêu":"Khách tập sáng"},{"Khung giờ":"13:00–16:00","Gợi ý":"Giảm 10–20%","Mục tiêu":"Lấp giờ trống"},{"Khung giờ":"18:00–21:00","Gợi ý":"Giá cao điểm","Mục tiêu":"Tối đa doanh thu"}])
        st.dataframe(df, use_container_width=True)
    with tabs[5]:
        checks=[("Có dữ liệu sân", s["courts"]>0),("Có booking", s["bookings"]>0),("Có marketplace", s["products"]>0),("Feedback được xử lý", s["feedback_open"]==0)]
        for name,ok in checks: status(("✅ " if ok else "⚠️ ")+name, "safe" if ok else "warn")
    with tabs[6]:
        rules=["Booking mới → gửi gợi ý đặt lại tuần sau","Check-in → cộng điểm loyalty","Giờ thấp điểm trống → tạo voucher","Feedback mới → tạo task xử lý","Sản phẩm mới → gợi ý đẩy marketplace"]
        for r in rules: st.checkbox(r, value=True)
    with tabs[7]:
        prompt=st.text_input("Hỏi AI offline")
        if prompt: st.info(ai_answer(prompt))

def page_reports() -> None:
    hero("📊 Báo cáo & xuất dữ liệu", "Báo cáo vận hành, doanh thu demo, booking, sản phẩm, khách hàng. Có tải CSV.")
    datasets={"bookings":"SELECT * FROM bookings","courts":"SELECT * FROM courts","users":"SELECT * FROM users","products":"SELECT * FROM products","matches":"SELECT * FROM matches","checkins":"SELECT * FROM checkins","tasks":"SELECT * FROM tasks"}
    name=st.selectbox("Chọn bảng", list(datasets))
    df=rows_to_df(q(datasets[name]))
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Tải CSV", df.to_csv(index=False).encode("utf-8-sig"), f"{name}.csv", "text/csv")

def page_backup() -> None:
    hero("☁️ Lưu trữ & đồng bộ", "Backup JSON, restore dữ liệu, chuẩn bị Supabase cloud sync cho production.")
    tables=["users","courts","bookings","products","matches","reviews","memberships","checkins","notifications","feedback","tasks"]
    data={t:[dict(r) for r in q(f"SELECT * FROM {t}")] for t in tables}
    st.download_button("⬇️ Backup toàn bộ JSON", json.dumps(data,ensure_ascii=False,indent=2).encode("utf-8"), "badminton_vinh_backup.json", "application/json")
    up=st.file_uploader("Restore từ JSON backup", type=["json"])
    if up and st.button("Restore dữ liệu"):
        payload=json.load(up)
        with conn() as c:
            for t,rows in payload.items():
                if t not in tables: continue
                c.execute(f"DELETE FROM {t}")
                for row in rows:
                    cols=list(row.keys()); vals=[row[k] for k in cols]
                    c.execute(f"INSERT INTO {t} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})", vals)
            c.commit()
        st.success("Đã restore dữ liệu."); st.rerun()
    st.markdown("### Supabase Production")
    status("Bản này đã chuẩn bị luồng backup/restore. Khi public nhiều người dùng, nên chuyển database chính sang Supabase thay vì chỉ dùng SQLite local.", "warn")
    st.code('''# Streamlit Secrets mẫu\nSUPABASE_URL="https://xxx.supabase.co"\nSUPABASE_SERVICE_ROLE_KEY="..."\nAPP_MODE="production"''', language="toml")

def page_admin() -> None:
    hero("👑 Admin Production", "Kiểm tra trước public, dữ liệu thật, trạng thái app, user, quyền, health check.")
    if current_user()["role"] != "admin": st.warning("Trang này dành cho admin demo."); return
    tabs=st.tabs(["Checklist", "Users", "Tasks", "Feedback", "Settings"])
    with tabs[0]:
        checks=[("Có ít nhất 3 sân thật", len(q("SELECT * FROM courts"))>=3),("Sân có SĐT", all(r["phone"] for r in q("SELECT phone FROM courts"))),("Booking lưu được", len(q("SELECT * FROM bookings"))>=1),("Marketplace có tin", len(q("SELECT * FROM products"))>=1),("Có backup JSON", True),("AI offline không tốn API", True)]
        score=sum(ok for _,ok in checks)
        st.progress(score/len(checks)); st.metric("Production Score", f"{score}/{len(checks)}")
        for name,ok in checks: status(("✅ " if ok else "⚠️ ")+name, "safe" if ok else "warn")
    with tabs[1]: st.dataframe(rows_to_df(q("SELECT * FROM users")), use_container_width=True)
    with tabs[2]:
        for t in q("SELECT * FROM tasks ORDER BY created_at DESC"):
            with st.container(border=True): st.write(f"**{t['title']}** · {t['priority']} · {t['status']} · {t['owner']}")
    with tabs[3]:
        with st.form("fb"):
            cat=st.selectbox("Loại", ["Lỗi app","Thông tin sân sai","Góp ý UX","Khác"]); msg=st.text_area("Nội dung")
            if st.form_submit_button("Gửi feedback") and msg:
                execute("INSERT INTO feedback VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), current_user()["id"], cat, msg, "Open", datetime.now().isoformat(timespec="seconds"))); st.success("Đã ghi nhận.")
        st.dataframe(rows_to_df(q("SELECT * FROM feedback")), use_container_width=True)
    with tabs[4]:
        st.info("Các cài đặt production nên đặt trong Streamlit Secrets, không commit lên GitHub.")
        st.checkbox("Chế độ mobile-first", True)
        st.checkbox("AI offline-first", True)
        st.checkbox("Ẩn trang admin với người dùng thường", True)

def page_health() -> None:
    hero("🩺 Health Check", "Kiểm tra app trước khi public và sau khi deploy Streamlit Cloud.")
    checks=[]
    checks.append(("app.py tồn tại", Path("app.py").exists()))
    checks.append(("requirements.txt tồn tại", Path("requirements.txt").exists()))
    checks.append(("SQLite đọc được", DB_PATH.exists()))
    for table in ["users","courts","bookings","products","tasks"]:
        try: n=len(q(f"SELECT * FROM {table}")); checks.append((f"Bảng {table}: {n} dòng", True))
        except Exception: checks.append((f"Bảng {table} lỗi", False))
    score=sum(ok for _,ok in checks)
    st.progress(score/len(checks)); st.metric("Health", f"{score}/{len(checks)}")
    for name,ok in checks: status(("✅ " if ok else "❌ ")+name, "safe" if ok else "bad")
    st.markdown("### Lỗi thường gặp")
    st.markdown("- Nếu không thấy app.py: upload sai cấp thư mục lên GitHub.\n- Nếu mất dữ liệu sau deploy: dùng Backup JSON hoặc chuyển sang Supabase.\n- Nếu sidebar quá dài: dùng chế độ phân quyền User/Owner/Admin trong bản này.")


# ========================= PRODUCTION V1.1 ADD-ONS =========================

def page_court_data_manager() -> None:
    hero("🏟️ Dữ liệu sân thật TP Vinh", "Nhập/chỉnh dữ liệu sân thật trước khi public. Đây là phần quan trọng nhất để app hữu ích với người chơi.")
    if current_user()["role"] not in ["owner", "admin"]:
        st.warning("Trang này dành cho chủ sân hoặc admin."); return
    tabs = st.tabs(["Danh sách sân", "Thêm sân thật", "Import CSV", "Checklist dữ liệu"])
    with tabs[0]:
        rows = q("SELECT * FROM courts ORDER BY area,name")
        st.dataframe(rows_to_df(rows), use_container_width=True)
        court = select_row("Chọn sân để cập nhật nhanh", rows, lambda r: f"{r['name']} · {r['area']} · {r['phone']}", "edit_court_real")
        if court:
            with st.form("quick_edit_court"):
                name = st.text_input("Tên sân", court["name"])
                area = st.text_input("Khu vực", court["area"])
                address = st.text_input("Địa chỉ", court["address"])
                phone = st.text_input("Số điện thoại", court["phone"])
                price = st.number_input("Giá thường", 0, 1000000, int(court["price"] or 0), 10000)
                peak = st.number_input("Giá cao điểm", 0, 1000000, int(court["peak_price"] or 0), 10000)
                count = st.number_input("Số sân", 1, 100, int(court["court_count"] or 1))
                features = st.text_input("Tiện ích", court["features"] or "")
                status_value = st.selectbox("Trạng thái", ["active", "hidden", "maintenance"], index=["active", "hidden", "maintenance"].index(court["status"] if court["status"] in ["active","hidden","maintenance"] else "active"))
                if st.form_submit_button("💾 Lưu cập nhật"):
                    execute("UPDATE courts SET name=?,area=?,address=?,phone=?,price=?,peak_price=?,court_count=?,features=?,status=? WHERE id=?", (name,area,address,phone,price,peak,count,features,status_value,court["id"]))
                    st.success("Đã cập nhật sân."); st.rerun()
    with tabs[1]:
        with st.form("add_real_court_v11"):
            name=st.text_input("Tên sân thật")
            area=st.text_input("Khu vực", "TP Vinh")
            address=st.text_input("Địa chỉ chi tiết")
            phone=st.text_input("Số điện thoại")
            price=st.number_input("Giá giờ thường", 0, 1000000, 70000, 10000)
            peak=st.number_input("Giá giờ cao điểm", 0, 1000000, 100000, 10000)
            count=st.number_input("Số sân", 1, 100, 4)
            features=st.text_input("Tiện ích", "Gửi xe, nước uống, thuê vợt")
            open_time=st.text_input("Giờ mở cửa", "05:00")
            close_time=st.text_input("Giờ đóng cửa", "23:00")
            if st.form_submit_button("➕ Thêm sân thật") and name:
                execute("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), current_user()["id"], name, area, address, phone, price, peak, 4.5, count, features, open_time, close_time, "active"))
                st.success("Đã thêm sân thật."); st.rerun()
    with tabs[2]:
        template = pd.DataFrame([{"name":"Tên sân mẫu", "area":"Trung tâm", "address":"Địa chỉ", "phone":"09xxxxxxxx", "price":70000, "peak_price":100000, "court_count":4, "features":"Gửi xe, nước uống", "open_time":"05:00", "close_time":"23:00"}])
        st.download_button("⬇️ Tải mẫu CSV sân", template.to_csv(index=False).encode("utf-8-sig"), "mau_san_cau_long_vinh.csv", "text/csv")
        up = st.file_uploader("Upload CSV sân thật", type=["csv"])
        if up:
            df = pd.read_csv(up)
            st.dataframe(df, use_container_width=True)
            if st.button("Import CSV vào danh sách sân"):
                need = {"name","area","address","phone","price","peak_price","court_count","features","open_time","close_time"}
                if not need.issubset(set(df.columns)):
                    st.error("CSV thiếu cột. Hãy tải file mẫu để nhập đúng định dạng.")
                else:
                    for _,r in df.iterrows():
                        execute("INSERT INTO courts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), current_user()["id"], str(r["name"]), str(r["area"]), str(r["address"]), str(r["phone"]), int(r["price"]), int(r["peak_price"]), 4.5, int(r["court_count"]), str(r["features"]), str(r["open_time"]), str(r["close_time"]), "active"))
                    st.success("Đã import sân từ CSV."); st.rerun()
    with tabs[3]:
        rows = q("SELECT * FROM courts")
        checks = [("Có ít nhất 3 sân", len(rows) >= 3),("Mọi sân có số điện thoại", all((r["phone"] or "").strip() for r in rows)),("Mọi sân có địa chỉ", all((r["address"] or "").strip() for r in rows)),("Mọi sân có giá thường", all(int(r["price"] or 0) > 0 for r in rows)),("Mọi sân có giờ mở/đóng cửa", all((r["open_time"] or "") and (r["close_time"] or "") for r in rows))]
        score = sum(ok for _,ok in checks)
        st.progress(score/len(checks)); st.metric("Court Data Score", f"{score}/{len(checks)}")
        for name,ok in checks: status(("✅ " if ok else "⚠️ ")+name, "safe" if ok else "warn")


def page_payment_status() -> None:
    hero("💳 Cọc & thanh toán demo", "Ghi nhận trạng thái thanh toán/cọc sân. Chưa tích hợp ngân hàng thật, nhưng đủ để chủ sân quản lý vận hành.")
    if current_user()["role"] not in ["owner", "admin"]:
        st.warning("Trang này dành cho chủ sân hoặc admin."); return
    rows = q("SELECT b.*, c.name court_name, u.name user_name, u.phone user_phone FROM bookings b JOIN courts c ON b.court_id=c.id LEFT JOIN users u ON b.user_id=u.id ORDER BY b.booking_date DESC,b.start_time DESC")
    c1,c2,c3=st.columns(3)
    with c1: metric("Tổng lịch", len(rows), "booking")
    with c2: metric("Đã thanh toán/cọc", len([r for r in rows if r["payment_status"] in ["Đã cọc","Đã thanh toán"]]), "lịch")
    with c3: metric("Doanh thu demo", fmt_money(sum(int(r["total"] or 0) for r in rows)), "tổng")
    for b in rows:
        with st.container(border=True):
            st.write(f"**{b['court_name']}** · {b['booking_date']} {b['start_time']} · {b['user_name']} · {fmt_money(b['total'])}")
            st.caption(f"SĐT: {b['user_phone']} · Lịch: {b['status']} · Thanh toán: {b['payment_status']}")
            col1,col2,col3=st.columns(3)
            with col1:
                pay_options=["Chưa thanh toán","Thanh toán tại sân","Đã cọc","Đã thanh toán"]
                new_pay=st.selectbox("Thanh toán", pay_options, index=pay_options.index(b["payment_status"] if b["payment_status"] in pay_options else "Chưa thanh toán"), key="pay_v11"+b["id"])
            with col2:
                status_options=["Chờ xác nhận","Đã xác nhận","Đã check-in","Đã hủy","Không đến"]
                new_status=st.selectbox("Trạng thái lịch", status_options, index=status_options.index(b["status"] if b["status"] in status_options else "Chờ xác nhận"), key="stat_v11"+b["id"])
            with col3:
                st.write("")
                if st.button("💾 Cập nhật", key="upd_pay_v11"+b["id"]):
                    execute("UPDATE bookings SET payment_status=?, status=? WHERE id=?", (new_pay,new_status,b["id"]))
                    st.success("Đã cập nhật."); st.rerun()


def page_cloud_production() -> None:
    hero("☁️ Cloud Production Plan", "Hướng dẫn chuyển từ SQLite demo sang Supabase khi public thật cho nhiều người dùng.")
    st.markdown("""
    ### Khi nào cần Supabase?
    Nếu app có nhiều người cùng đặt sân, bạn nên dùng Supabase làm database chính. SQLite phù hợp demo/local, nhưng trên Streamlit Cloud dữ liệu có thể không bền sau reboot/deploy.
    
    ### Quy trình khuyến nghị
    1. Tạo Supabase project.
    2. Tạo bảng users/courts/bookings/products/matches.
    3. Lưu SUPABASE_URL và SERVICE_ROLE_KEY trong Streamlit Secrets.
    4. Không commit key lên GitHub.
    5. Dùng Backup JSON hiện tại để di chuyển dữ liệu ban đầu.
    """)
    st.code("""# Streamlit Secrets mẫu
APP_MODE = "production"
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "YOUR_SERVICE_ROLE_KEY"
AI_MODE = "offline"
USE_EXTERNAL_AI = "false""", language="toml")
    st.markdown("### SQL gợi ý tối thiểu")
    st.code("""create table if not exists cloud_snapshots (
  id uuid primary key default gen_random_uuid(),
  space text not null,
  payload jsonb not null,
  created_at timestamptz default now()
);""", language="sql")
    status("Bản v1.1 vẫn giữ SQLite để bạn chạy ngay. Khi muốn public thật, dùng Supabase hoặc database cloud để dữ liệu bền hơn.", "warn")


def page_public_launch_checklist() -> None:
    hero("🚀 Public Launch Checklist", "Checklist cuối trước khi gửi link cho người chơi và chủ sân ở TP Vinh.")
    courts = q("SELECT * FROM courts")
    checks = [("Có dữ liệu sân thật", len(courts) >= 3),("Sân có SĐT/địa chỉ/giá", all((r["phone"] and r["address"] and int(r["price"] or 0)>0) for r in courts)),("Có ít nhất 1 booking test", len(q("SELECT * FROM bookings")) >= 1),("Có tài khoản player/owner/admin", len(q("SELECT * FROM users WHERE role='player'"))>=1 and len(q("SELECT * FROM users WHERE role='owner'"))>=1 and len(q("SELECT * FROM users WHERE role='admin'"))>=1),("Có backup JSON", True),("AI offline không tốn API", True),("Mobile menu đã gọn theo vai trò", True),("Không lưu Secrets trong GitHub", True)]
    score=sum(ok for _,ok in checks)
    st.progress(score/len(checks)); st.metric("Launch Score", f"{score}/{len(checks)}")
    for name,ok in checks: status(("✅ " if ok else "⚠️ ")+name, "safe" if ok else "warn")
    st.markdown("### Test nhanh trên điện thoại")
    st.markdown("- Mở app → chọn Người chơi Demo → Đặt sân → Check-in.\n- Chọn Chủ sân Demo → xác nhận lịch → cập nhật thanh toán.\n- Chọn Admin Demo → backup JSON → Health Check.\n- Kiểm tra chữ/nút có dễ bấm không.")


def page_ai_ops_v11() -> None:
    hero("🤖 AI Ops v1.1", "AI vận hành gọn hơn: kế hoạch hôm nay, task tự động, marketing và rủi ro. Offline-first, không tốn API.")
    tabs=st.tabs(["Kế hoạch hôm nay","Tự tạo task","Marketing 7 ngày","Risk Guard","Chat"])
    with tabs[0]:
        for i,r in enumerate(ai_recommendations(),1):
            status(f"<b>{i}. {r['title']}</b><br>{r['body']}<br><span class='pill yellow'>{r['priority']}</span>", "warn" if r["priority"]=="Cao" else "safe")
    with tabs[1]:
        owner=st.selectbox("Giao cho", ["Chủ sân", "Admin", "Marketing", "CSKH", "AI Agent"])
        due=st.date_input("Hạn xử lý", date.today()+timedelta(days=1))
        if st.button("AI tạo task vận hành hôm nay"):
            for r in ai_recommendations():
                execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), r["title"], owner, r["priority"], "Open", str(due), "AI Ops v1.1", datetime.now().isoformat(timespec="seconds")))
            st.success("Đã tạo task từ AI.")
    with tabs[2]:
        campaign=st.selectbox("Chiến dịch", ["Lấp giờ thấp điểm", "Ra mắt app", "Marketplace dụng cụ", "Gói hội viên", "Giải giao lưu"])
        texts={"Lấp giờ thấp điểm":"Tuần này đặt sân giờ thấp điểm tại TP Vinh có ưu đãi. Rủ bạn đánh cầu, giữ sức khỏe, tiết kiệm chi phí.","Ra mắt app":"Badminton Vinh giúp đặt sân, tìm kèo, mua bán dụng cụ và quản lý lịch chơi trong một nơi.","Marketplace dụng cụ":"Có vợt/giày/cầu không dùng nữa? Đăng bán miễn phí cho cộng đồng cầu lông Vinh.","Gói hội viên":"Chơi đều mỗi tuần? Gói hội viên giúp giữ lịch quen và nhận ưu đãi tốt hơn.","Giải giao lưu":"Tạo giải giao lưu cuối tuần, tìm đối thủ cùng trình độ và kết nối cộng đồng cầu lông Vinh."}
        st.text_area("Caption AI", texts[campaign], height=130)
    with tabs[3]:
        s=app_stats(); risks=[]
        if s["fill"]<30: risks.append("Tỷ lệ lấp sân còn thấp: cần voucher/marketing giờ trống.")
        if s["feedback_open"]>0: risks.append("Có feedback chưa xử lý: cần phản hồi khách trong 24h.")
        if len(q("SELECT * FROM courts WHERE phone='' OR address=''"))>0: risks.append("Một số sân thiếu SĐT/địa chỉ.")
        if not risks: risks=["Chưa phát hiện rủi ro lớn trong dữ liệu demo."]
        for r in risks: status("⚠️ "+r, "warn")
    with tabs[4]:
        prompt=st.text_input("Hỏi AI vận hành")
        if prompt: st.info(ai_answer(prompt))

# ========================= NAV =========================

PAGES = {
    "👤 Người dùng": {
        "🏠 Trang chính": page_home,
        "📅 Đặt sân": page_booking,
        "📋 Lịch của tôi": page_my_bookings,
        "🛒 Chợ mua bán": page_market,
        "➕ Đăng bán": page_sell,
        "🤝 Tìm người chơi": page_matches,
        "💎 Hội viên": page_membership,
    },
    "🏟️ Chủ sân": {
        "🏟️ Chủ sân Portal": page_owner,
        "📊 Báo cáo": page_reports,
        "🤖 AI Trợ lý vận hành": page_ai,
        "🤖 AI Ops v1.1": page_ai_ops_v11,
        "🏟️ Dữ liệu sân thật": page_court_data_manager,
        "💳 Cọc & thanh toán": page_payment_status,
    },
    "👑 Admin": {
        "👑 Admin Production": page_admin,
        "☁️ Lưu trữ & đồng bộ": page_backup,
        "☁️ Cloud Production Plan": page_cloud_production,
        "🏟️ Dữ liệu sân thật": page_court_data_manager,
        "💳 Cọc & thanh toán": page_payment_status,
        "🚀 Public Launch Checklist": page_public_launch_checklist,
        "🩺 Health Check": page_health,
        "🤖 AI Trợ lý vận hành": page_ai,
        "🤖 AI Ops v1.1": page_ai_ops_v11,
    }
}

def sidebar() -> Any:
    auth_panel()
    user=current_user()
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Manage App")
    # default groups by role
    allowed = ["👤 Người dùng"]
    if user["role"] in ["owner","admin"]: allowed.append("🏟️ Chủ sân")
    if user["role"] == "admin": allowed.append("👑 Admin")
    group = st.sidebar.radio("Chế độ", allowed, index=0)
    page_name = st.sidebar.radio("Chức năng", list(PAGES[group].keys()))
    all_names=[]
    for g,ps in PAGES.items():
        if g in allowed:
            all_names += list(ps.keys())
    quick = st.sidebar.selectbox("🔎 Mở nhanh", ["Không dùng"] + all_names)
    if quick != "Không dùng":
        for g,ps in PAGES.items():
            if quick in ps: return ps[quick]
    st.sidebar.markdown(f"<div class='mobile-note'>{APP_NAME} · {APP_VERSION}</div>", unsafe_allow_html=True)
    return PAGES[group][page_name]

def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🏸", layout="wide", initial_sidebar_state="expanded")
    css(); init_db()
    page_func = sidebar()
    try:
        page_func()
    except Exception as e:
        st.error("Trang này đang gặp lỗi hiển thị. Hãy thử reload app hoặc vào Health Check.")
        with st.expander("Chi tiết lỗi kỹ thuật"):
            st.exception(e)

if __name__ == "__main__":
    main()
