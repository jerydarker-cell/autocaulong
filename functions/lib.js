import { setGlobalOptions } from "firebase-functions/v2";
import { defineString } from "firebase-functions/params";
import { HttpsError } from "firebase-functions/v2/https";
import { initializeApp } from "firebase-admin/app";
import { getFirestore, FieldValue } from "firebase-admin/firestore";
import { createHash, randomInt } from "node:crypto";

initializeApp();
export const db = getFirestore();
export { FieldValue };

setGlobalOptions({
  region: "asia-southeast1",
  memory: "256MiB",
  timeoutSeconds: 30,
  maxInstances: 20,
});

const ADMIN_EMAILS = defineString("ADMIN_EMAILS", {
  description: "Comma-separated Firebase Authentication emails allowed to use admin functions",
});

export const APP = Object.freeze({
  TZ: "Asia/Ho_Chi_Minh",
  MAX_ADVANCE_DAYS: 60,
  MAX_SLOTS_PER_BOOKING: 3,
  DEFAULT_SETTINGS: {
    businessName: "Đặt Sân Cầu Lông",
    hotline: "",
    address: "",
    bookingNote: "Vui lòng đến đúng giờ. Sân sẽ liên hệ xác nhận nếu cần.",
  },
  DEFAULT_COURTS: [
    { id: "C1", name: "Sân 1", type: "Tiêu chuẩn", openTime: "05:00", closeTime: "23:00", slotMinutes: 60, pricePerSlot: 80000, active: true },
    { id: "C2", name: "Sân 2", type: "Tiêu chuẩn", openTime: "05:00", closeTime: "23:00", slotMinutes: 60, pricePerSlot: 80000, active: true },
    { id: "C3", name: "Sân 3", type: "Tiêu chuẩn", openTime: "05:00", closeTime: "23:00", slotMinutes: 60, pricePerSlot: 80000, active: true },
  ],
});

export async function ensureSeed() {
  const settingsRef = db.collection("settings").doc("public");
  const [settingsSnap, courtSnap] = await Promise.all([
    settingsRef.get(),
    db.collection("courts").limit(1).get(),
  ]);

  const writes = [];
  if (!settingsSnap.exists) writes.push(settingsRef.set({ ...APP.DEFAULT_SETTINGS, createdAt: FieldValue.serverTimestamp() }));
  if (courtSnap.empty) {
    for (const court of APP.DEFAULT_COURTS) {
      const { id, ...data } = court;
      writes.push(db.collection("courts").doc(id).set({ ...data, createdAt: FieldValue.serverTimestamp() }));
    }
  }
  await Promise.all(writes);
}

export async function getSettings() {
  const snap = await db.collection("settings").doc("public").get();
  const raw = snap.exists ? snap.data() : {};
  return {
    businessName: clean(raw.businessName || APP.DEFAULT_SETTINGS.businessName),
    hotline: clean(raw.hotline || APP.DEFAULT_SETTINGS.hotline),
    address: clean(raw.address || APP.DEFAULT_SETTINGS.address),
    bookingNote: clean(raw.bookingNote || APP.DEFAULT_SETTINGS.bookingNote),
  };
}

export async function getCourts(activeOnly) {
  const snap = await db.collection("courts").get();
  return snap.docs
    .map((d) => normalizeCourt(d.id, d.data()))
    .filter((c) => !activeOnly || c.active)
    .sort((a, b) => a.name.localeCompare(b.name, "vi"));
}

export function normalizeCourt(id, data = {}) {
  return {
    id,
    name: clean(data.name || id),
    type: clean(data.type || "Tiêu chuẩn"),
    openTime: clean(data.openTime || "05:00"),
    closeTime: clean(data.closeTime || "23:00"),
    slotMinutes: Number(data.slotMinutes || 60),
    pricePerSlot: Number(data.pricePerSlot || 0),
    active: data.active !== false,
  };
}

export function publicBooking(b) {
  return {
    id: b.id,
    code: b.code,
    date: b.date,
    courtId: b.courtId,
    courtName: b.courtName,
    startTime: b.startTime,
    endTime: b.endTime,
    durationMinutes: Number(b.durationMinutes || 0),
    customerName: b.customerName,
    phone: b.phone,
    note: b.note || "",
    amount: Number(b.amount || 0),
    status: b.status,
    paymentStatus: b.paymentStatus,
  };
}

export function adminBooking(b) {
  return {
    ...publicBooking(b),
    createdAt: toIso(b.createdAt),
    updatedAt: toIso(b.updatedAt),
  };
}

export function requireAdmin(request) {
  const email = String(request.auth?.token?.email || "").trim().toLowerCase();
  if (!request.auth || !email) throw new HttpsError("unauthenticated", "Vui lòng đăng nhập quản trị.");
  const allowed = ADMIN_EMAILS.value().split(",").map((x) => x.trim().toLowerCase()).filter(Boolean);
  if (!allowed.length || !allowed.includes(email)) throw new HttpsError("permission-denied", "Tài khoản này chưa được cấp quyền quản trị.");
  return email;
}

export function validateDate(dateStr) {
  validateDateLoose(dateStr);
  const diff = daysBetween(today(), dateStr);
  if (diff < 0) throw invalid("Không thể đặt sân trong quá khứ.");
  if (diff > APP.MAX_ADVANCE_DAYS) throw invalid(`Chỉ được đặt trước tối đa ${APP.MAX_ADVANCE_DAYS} ngày.`);
}

export function validateDateLoose(dateStr) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) throw invalid("Ngày không hợp lệ.");
  const [y, m, d] = dateStr.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  if (dt.getUTCFullYear() !== y || dt.getUTCMonth() !== m - 1 || dt.getUTCDate() !== d) throw invalid("Ngày không hợp lệ.");
}

export function daysBetween(a, b) {
  const [ay, am, ad] = a.split("-").map(Number);
  const [by, bm, bd] = b.split("-").map(Number);
  return Math.round((Date.UTC(by, bm - 1, bd) - Date.UTC(ay, am - 1, ad)) / 86400000);
}

export function today() {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone: APP.TZ, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
  const map = Object.fromEntries(parts.map((p) => [p.type, p.value]));
  return `${map.year}-${map.month}-${map.day}`;
}

export function currentMinutes() {
  const parts = new Intl.DateTimeFormat("en-GB", { timeZone: APP.TZ, hour12: false, hour: "2-digit", minute: "2-digit" }).formatToParts(new Date());
  const map = Object.fromEntries(parts.map((p) => [p.type, p.value]));
  return Number(map.hour) * 60 + Number(map.minute);
}

export function clean(value) { return String(value == null ? "" : value).trim(); }
export function normalizePhone(value) { return clean(value).replace(/\D/g, ""); }
export function overlap(aStart, aEnd, bStart, bEnd) { return aStart < bEnd && aEnd > bStart; }
export function isTime(t) { return /^([01]\d|2[0-3]):[0-5]\d$/.test(t); }

export function timeToMinutes(t) {
  if (!isTime(t)) throw invalid("Giờ không hợp lệ.");
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}

export function minutesToTime(mins) {
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export function courtDayId(date, courtId) {
  return `${date}__${courtId}`.replace(/[^A-Za-z0-9_-]/g, "_");
}

export function makeBookingCode(dateStr) {
  const yymmdd = dateStr.slice(2).replaceAll("-", "");
  return `CL-${yymmdd}-${String(randomInt(0, 1000000)).padStart(6, "0")}`;
}

export function lookupHash(code, phone) {
  return createHash("sha256").update(`${code.toUpperCase()}|${phone}`).digest("hex");
}

export function toIso(value) {
  if (!value) return "";
  if (typeof value.toDate === "function") return value.toDate().toISOString();
  if (value instanceof Date) return value.toISOString();
  return String(value);
}

export function invalid(message) { return new HttpsError("invalid-argument", message); }
export function normalizeError(err) {
  if (err instanceof HttpsError) return err;
  console.error(err);
  return new HttpsError("internal", "Có lỗi hệ thống. Vui lòng thử lại.");
}
