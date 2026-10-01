import { onCall, HttpsError } from "firebase-functions/v2/https";
import {
  db, FieldValue, APP, ensureSeed, getSettings, getCourts, normalizeCourt, publicBooking,
  validateDate, today, currentMinutes, clean, normalizePhone, overlap, timeToMinutes,
  minutesToTime, courtDayId, makeBookingCode, lookupHash, invalid, normalizeError
} from "./lib.js";

export const getBootstrap = onCall(async () => {
  await ensureSeed();
  const [settings, courts] = await Promise.all([getSettings(), getCourts(true)]);
  return {
    ok: true,
    today: today(),
    maxAdvanceDays: APP.MAX_ADVANCE_DAYS,
    settings,
    courts,
  };
});

export const getAvailability = onCall(async (request) => {
  await ensureSeed();
  const dateStr = clean(request.data?.dateStr ?? request.data?.date);
  validateDate(dateStr);

  const [courts, daySnap] = await Promise.all([
    getCourts(true),
    db.collection("courtDays").where("date", "==", dateStr).get(),
  ]);

  const occupiedByCourt = new Map();
  for (const doc of daySnap.docs) {
    const data = doc.data() || {};
    occupiedByCourt.set(String(data.courtId || ""), Array.isArray(data.intervals) ? data.intervals : []);
  }

  const isToday = dateStr === today();
  const nowMinutes = currentMinutes();

  return {
    ok: true,
    date: dateStr,
    courts: courts.map((court) => {
      const slots = [];
      const open = timeToMinutes(court.openTime);
      const close = timeToMinutes(court.closeTime);
      const step = Number(court.slotMinutes);
      const occupied = occupiedByCourt.get(court.id) || [];

      for (let start = open; start + step <= close; start += step) {
        const end = start + step;
        const booked = occupied.some((interval) =>
          overlap(start, end, Number(interval.startMinutes), Number(interval.endMinutes))
        );
        const past = isToday && start <= nowMinutes;
        slots.push({
          start: minutesToTime(start),
          end: minutesToTime(end),
          available: !booked && !past,
          reason: past ? "past" : booked ? "booked" : "",
        });
      }
      return { ...court, slots };
    }),
  };
});

export const createBooking = onCall(async (request) => {
  await ensureSeed();
  const payload = request.data?.payload ?? request.data ?? {};
  const date = clean(payload.date);
  const courtId = clean(payload.courtId);
  const startTime = clean(payload.startTime);
  const durationMinutes = Number(payload.durationMinutes || 0);
  const customerName = clean(payload.customerName).slice(0, 80);
  const phone = normalizePhone(payload.phone);
  const note = clean(payload.note).slice(0, 500);

  validateDate(date);
  if (!courtId || !startTime || !durationMinutes || !customerName || !phone) {
    throw invalid("Vui lòng nhập đầy đủ ngày, sân, giờ, họ tên và số điện thoại.");
  }
  if (!/^\d{9,12}$/.test(phone)) throw invalid("Số điện thoại chưa hợp lệ.");

  const bookingRef = db.collection("bookings").doc();

  for (let attempt = 0; attempt < 7; attempt++) {
    const code = makeBookingCode(date);
    const codeRef = db.collection("bookingCodes").doc(code);
    const lookupKey = lookupHash(code, phone);
    const lookupRef = db.collection("bookingLookups").doc(lookupKey);
    const dayRef = db.collection("courtDays").doc(courtDayId(date, courtId));

    try {
      let createdBooking = null;
      await db.runTransaction(async (tx) => {
        const courtRef = db.collection("courts").doc(courtId);
        const [courtSnap, codeSnap, daySnap] = await tx.getAll(courtRef, codeRef, dayRef);

        if (!courtSnap.exists) throw invalid("Sân không tồn tại hoặc đang tạm ngừng nhận lịch.");
        const court = normalizeCourt(courtSnap.id, courtSnap.data());
        if (!court.active) throw invalid("Sân đang tạm ngừng nhận lịch.");
        if (codeSnap.exists) throw new Error("CODE_COLLISION");

        const start = timeToMinutes(startTime);
        const open = timeToMinutes(court.openTime);
        const close = timeToMinutes(court.closeTime);
        const step = Number(court.slotMinutes);
        const end = start + durationMinutes;

        if (durationMinutes < step || durationMinutes % step !== 0 || durationMinutes > step * APP.MAX_SLOTS_PER_BOOKING) {
          throw invalid("Thời lượng đặt sân không hợp lệ.");
        }
        if (start < open || end > close || (start - open) % step !== 0) {
          throw invalid("Khung giờ nằm ngoài giờ hoạt động của sân.");
        }
        if (date === today() && start <= currentMinutes()) {
          throw invalid("Khung giờ này đã qua. Vui lòng chọn giờ khác.");
        }

        const intervals = daySnap.exists && Array.isArray(daySnap.data()?.intervals) ? daySnap.data().intervals : [];
        if (intervals.some((interval) =>
          overlap(start, end, Number(interval.startMinutes), Number(interval.endMinutes))
        )) {
          throw new HttpsError("already-exists", "Khung giờ vừa được người khác đặt. Vui lòng chọn giờ khác.");
        }

        const amount = Math.round((durationMinutes / step) * Number(court.pricePerSlot));
        const now = FieldValue.serverTimestamp();
        const booking = {
          id: bookingRef.id,
          code,
          date,
          courtId: court.id,
          courtName: court.name,
          startTime,
          endTime: minutesToTime(end),
          durationMinutes,
          customerName,
          phone,
          note,
          amount,
          status: "Pending",
          paymentStatus: "Unpaid",
          createdAt: now,
          updatedAt: now,
        };

        tx.create(codeRef, { bookingId: bookingRef.id, createdAt: now });
        tx.create(lookupRef, { bookingId: bookingRef.id, code, phone, createdAt: now });
        tx.create(bookingRef, booking);
        tx.set(dayRef, {
          date,
          courtId: court.id,
          intervals: [...intervals, {
            bookingId: bookingRef.id,
            code,
            startMinutes: start,
            endMinutes: end,
            startTime,
            endTime: minutesToTime(end),
          }],
          updatedAt: now,
        }, { merge: true });

        createdBooking = booking;
      });

      return { ok: true, booking: publicBooking(createdBooking) };
    } catch (err) {
      if (String(err?.message) === "CODE_COLLISION") continue;
      throw normalizeError(err);
    }
  }

  throw new HttpsError("aborted", "Không tạo được mã đặt sân. Vui lòng thử lại.");
});

export const lookupBooking = onCall(async (request) => {
  const code = clean(request.data?.code).toUpperCase();
  const phone = normalizePhone(request.data?.phone);
  if (!code || !phone) throw invalid("Nhập mã đặt sân và số điện thoại.");

  const lookup = await db.collection("bookingLookups").doc(lookupHash(code, phone)).get();
  if (!lookup.exists) throw new HttpsError("not-found", "Không tìm thấy lịch đặt phù hợp.");
  const booking = await db.collection("bookings").doc(lookup.data().bookingId).get();
  if (!booking.exists) throw new HttpsError("not-found", "Không tìm thấy lịch đặt phù hợp.");
  return { ok: true, booking: publicBooking({ id: booking.id, ...booking.data() }) };
});

export const cancelMyBooking = onCall(async (request) => {
  const code = clean(request.data?.code).toUpperCase();
  const phone = normalizePhone(request.data?.phone);
  if (!code || !phone) throw invalid("Nhập mã đặt sân và số điện thoại.");

  const lookupRef = db.collection("bookingLookups").doc(lookupHash(code, phone));
  await db.runTransaction(async (tx) => {
    const lookupSnap = await tx.get(lookupRef);
    if (!lookupSnap.exists) throw new HttpsError("not-found", "Không tìm thấy lịch đặt phù hợp.");

    const bookingRef = db.collection("bookings").doc(lookupSnap.data().bookingId);
    const bookingSnap = await tx.get(bookingRef);
    if (!bookingSnap.exists) throw new HttpsError("not-found", "Không tìm thấy lịch đặt phù hợp.");
    const booking = bookingSnap.data();
    if (booking.status !== "Pending") throw new HttpsError("failed-precondition", "Chỉ lịch đang chờ xác nhận mới có thể tự hủy.");

    const dayRef = db.collection("courtDays").doc(courtDayId(booking.date, booking.courtId));
    const daySnap = await tx.get(dayRef);
    const intervals = daySnap.exists && Array.isArray(daySnap.data()?.intervals) ? daySnap.data().intervals : [];

    tx.update(bookingRef, { status: "Cancelled", updatedAt: FieldValue.serverTimestamp() });
    tx.set(dayRef, {
      date: booking.date,
      courtId: booking.courtId,
      intervals: intervals.filter((x) => x.bookingId !== bookingRef.id),
      updatedAt: FieldValue.serverTimestamp(),
    }, { merge: true });
  });

  return { ok: true, message: "Đã hủy lịch đặt." };
});

