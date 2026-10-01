import { onCall, HttpsError } from "firebase-functions/v2/https";
import {
  db, FieldValue, ensureSeed, getSettings, getCourts, adminBooking, requireAdmin,
  validateDateLoose, today, clean, isTime, timeToMinutes, courtDayId, invalid, overlap
} from "./lib.js";

export const adminDashboard = onCall(async (request) => {
  requireAdmin(request);
  await ensureSeed();
  const filters = request.data?.filters ?? request.data ?? {};
  const date = clean(filters.date || today());
  const status = clean(filters.status);
  const search = clean(filters.search).toLowerCase();

  let bookingSnap;
  if (date) {
    validateDateLoose(date);
    bookingSnap = await db.collection("bookings").where("date", "==", date).get();
  } else {
    bookingSnap = await db.collection("bookings").orderBy("createdAt", "desc").limit(300).get();
  }

  let bookings = bookingSnap.docs.map((d) => ({ id: d.id, ...d.data() }));
  if (status) bookings = bookings.filter((b) => b.status === status);
  if (search) {
    bookings = bookings.filter((b) => [b.code, b.customerName, b.phone, b.courtName]
      .some((v) => String(v || "").toLowerCase().includes(search)));
  }
  bookings.sort((a, b) => `${b.date}${b.startTime}`.localeCompare(`${a.date}${a.startTime}`));

  const todaySnap = await db.collection("bookings").where("date", "==", today()).get();
  const todayBookings = todaySnap.docs.map((d) => d.data()).filter((b) => b.status !== "Cancelled");
  const paidRevenue = todayBookings
    .filter((b) => b.paymentStatus === "Paid")
    .reduce((sum, b) => sum + Number(b.amount || 0), 0);

  const [courts, settings] = await Promise.all([getCourts(false), getSettings()]);
  return {
    ok: true,
    summary: {
      todayCount: todayBookings.length,
      pendingCount: todayBookings.filter((b) => b.status === "Pending").length,
      confirmedCount: todayBookings.filter((b) => b.status === "Confirmed").length,
      paidRevenue,
    },
    bookings: bookings.map(adminBooking),
    courts,
    settings,
  };
});

export const adminUpdateBooking = onCall(async (request) => {
  requireAdmin(request);
  const bookingId = clean(request.data?.bookingId);
  const updates = request.data?.updates ?? {};
  if (!bookingId) throw invalid("Thiếu mã lịch đặt.");

  const allowedStatus = ["Pending", "Confirmed", "Completed", "Cancelled"];
  const allowedPayment = ["Unpaid", "Paid", "Refunded"];
  if (updates.status && !allowedStatus.includes(updates.status)) throw invalid("Trạng thái không hợp lệ.");
  if (updates.paymentStatus && !allowedPayment.includes(updates.paymentStatus)) throw invalid("Trạng thái thanh toán không hợp lệ.");

  const bookingRef = db.collection("bookings").doc(bookingId);
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(bookingRef);
    if (!snap.exists) throw new HttpsError("not-found", "Không tìm thấy lịch đặt.");
    const booking = snap.data();
    const nextStatus = updates.status || booking.status;
    const statusChanged = nextStatus !== booking.status;

    let dayRef = null;
    let dayIntervals = [];
    if (statusChanged && (booking.status === "Cancelled" || nextStatus === "Cancelled")) {
      dayRef = db.collection("courtDays").doc(courtDayId(booking.date, booking.courtId));
      const daySnap = await tx.get(dayRef);
      dayIntervals = daySnap.exists && Array.isArray(daySnap.data()?.intervals) ? daySnap.data().intervals : [];
    }

    if (booking.status === "Cancelled" && nextStatus !== "Cancelled") {
      const start = timeToMinutes(booking.startTime);
      const end = timeToMinutes(booking.endTime);
      if (dayIntervals.some((interval) =>
        interval.bookingId !== bookingId && overlap(start, end, Number(interval.startMinutes), Number(interval.endMinutes))
      )) {
        throw new HttpsError("already-exists", "Không thể khôi phục vì khung giờ đã được người khác đặt.");
      }
      tx.set(dayRef, {
        date: booking.date,
        courtId: booking.courtId,
        intervals: [...dayIntervals.filter((x) => x.bookingId !== bookingId), {
          bookingId,
          code: booking.code,
          startMinutes: start,
          endMinutes: end,
          startTime: booking.startTime,
          endTime: booking.endTime,
        }],
        updatedAt: FieldValue.serverTimestamp(),
      }, { merge: true });
    }

    if (booking.status !== "Cancelled" && nextStatus === "Cancelled") {
      tx.set(dayRef, {
        date: booking.date,
        courtId: booking.courtId,
        intervals: dayIntervals.filter((x) => x.bookingId !== bookingId),
        updatedAt: FieldValue.serverTimestamp(),
      }, { merge: true });
    }

    const patch = { updatedAt: FieldValue.serverTimestamp() };
    if (updates.status) patch.status = updates.status;
    if (updates.paymentStatus) patch.paymentStatus = updates.paymentStatus;
    tx.update(bookingRef, patch);
  });

  return { ok: true };
});

export const adminSaveCourt = onCall(async (request) => {
  requireAdmin(request);
  const court = request.data?.court ?? request.data ?? {};
  const name = clean(court.name).slice(0, 80);
  const type = clean(court.type || "Tiêu chuẩn").slice(0, 80);
  const openTime = clean(court.openTime);
  const closeTime = clean(court.closeTime);
  const slotMinutes = Number(court.slotMinutes || 60);
  const pricePerSlot = Number(court.pricePerSlot || 0);
  const active = court.active !== false;

  if (!name) throw invalid("Tên sân không được để trống.");
  if (!isTime(openTime) || !isTime(closeTime)) throw invalid("Giờ mở/đóng cửa chưa đúng định dạng HH:mm.");
  if (timeToMinutes(openTime) >= timeToMinutes(closeTime)) throw invalid("Giờ đóng cửa phải sau giờ mở cửa.");
  if (![30, 60, 90].includes(slotMinutes)) throw invalid("Slot hợp lệ: 30, 60 hoặc 90 phút.");
  if (!Number.isFinite(pricePerSlot) || pricePerSlot < 0) throw invalid("Giá sân không hợp lệ.");

  const id = clean(court.id) || `C${Date.now()}`;
  await db.collection("courts").doc(id).set({ name, type, openTime, closeTime, slotMinutes, pricePerSlot, active, updatedAt: FieldValue.serverTimestamp() }, { merge: true });
  return { ok: true, id };
});

export const adminSaveSettings = onCall(async (request) => {
  requireAdmin(request);
  const input = request.data?.settings ?? request.data ?? {};
  const settings = {
    businessName: clean(input.businessName).slice(0, 120),
    hotline: clean(input.hotline).slice(0, 30),
    address: clean(input.address).slice(0, 300),
    bookingNote: clean(input.bookingNote).slice(0, 500),
    updatedAt: FieldValue.serverTimestamp(),
  };
  await db.collection("settings").doc("public").set(settings, { merge: true });
  return { ok: true, settings: await getSettings() };
});

