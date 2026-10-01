let fbAuth = null;
  let fbFunctions = null;

  const state = {
    bootstrap:null, selectedDate:null, availability:null,
    bookingSelection:null, adminToken:'',
    adminData:null, adminTimer:null
  };

  const STATUS_LABEL = {Pending:'Chờ xác nhận',Confirmed:'Đã xác nhận',Completed:'Hoàn tất',Cancelled:'Đã hủy'};
  const PAY_LABEL = {Unpaid:'Chưa thanh toán',Paid:'Đã thanh toán',Refunded:'Đã hoàn tiền'};

  document.addEventListener('DOMContentLoaded', init);

  async function init(){
    try{
      await initFirebase();
      const data = await gas('getBootstrap');
      state.bootstrap = data;
      state.selectedDate = data.today;
      applyBrand(data.settings);
      document.getElementById('courtCount').textContent = data.courts.length;
      document.getElementById('advanceDays').textContent = data.maxAdvanceDays;
      setupQuickDate();
      buildDateStrip();
      await loadAvailability();
      const user = await waitForAuth();
      state.adminToken = user ? 'firebase-auth' : '';
      if(state.adminToken){
        try{ await enterAdminWithToken(); }catch(e){ clearAdminSession(); }
      }
      if('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(()=>{});
    }catch(e){ showFatal(e); }
  }

  async function initFirebase(){
    const c=window.FIREBASE_CONFIG||{};
    if(!c.apiKey || !c.projectId || String(c.apiKey).includes('YOUR_') || String(c.projectId).includes('YOUR_')){
      throw new Error('Chưa cấu hình Firebase. Mở file firebase-config.js và dán cấu hình Web App từ Firebase Console.');
    }
    if(!firebase.apps.length) firebase.initializeApp(c);
    fbAuth=firebase.auth();
    await fbAuth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);
    fbFunctions=firebase.app().functions(window.FIREBASE_REGION||'asia-southeast1');
  }

  function waitForAuth(){
    return new Promise(resolve=>{
      let done=false;
      const unsub=fbAuth.onAuthStateChanged(user=>{if(done)return;done=true;unsub();resolve(user);},()=>{if(done)return;done=true;unsub();resolve(null);});
    });
  }

  async function gas(name,...args){
    if(!fbFunctions) throw new Error('Firebase chưa sẵn sàng.');
    let data={};
    if(name==='getAvailability') data={dateStr:args[0]};
    else if(name==='createBooking') data={payload:args[0]};
    else if(name==='lookupBooking' || name==='cancelMyBooking') data={code:args[0],phone:args[1]};
    else if(name==='adminDashboard') data={filters:args[args.length-1]||{}};
    else if(name==='adminUpdateBooking') data={bookingId:args[args.length-2],updates:args[args.length-1]||{}};
    else if(name==='adminSaveCourt') data={court:args[args.length-1]||{}};
    else if(name==='adminSaveSettings') data={settings:args[args.length-1]||{}};
    try{
      const res=await fbFunctions.httpsCallable(name)(data);
      return res.data;
    }catch(err){
      throw new Error(friendlyFirebaseError(err));
    }
  }

  function friendlyFirebaseError(err){
    const code=String(err?.code||'').toLowerCase();
    const raw=String(err?.message||'').replace(/^FirebaseError:\s*/i,'');
    const map={
      'functions/already-exists':'Khung giờ vừa được người khác đặt. Vui lòng chọn giờ khác.',
      'functions/not-found':'Không tìm thấy dữ liệu phù hợp.',
      'functions/unauthenticated':'Vui lòng đăng nhập quản trị.',
      'functions/permission-denied':'Tài khoản này chưa được cấp quyền quản trị.',
      'functions/resource-exhausted':'Hệ thống đang bận. Vui lòng thử lại sau ít phút.',
      'auth/invalid-credential':'Email hoặc mật khẩu không đúng.',
      'auth/invalid-login-credentials':'Email hoặc mật khẩu không đúng.',
      'auth/too-many-requests':'Bạn thử đăng nhập quá nhiều lần. Vui lòng chờ rồi thử lại.',
      'auth/network-request-failed':'Mạng đang không ổn định. Vui lòng kiểm tra kết nối Internet.'
    };
    return map[code]||raw||'Có lỗi kết nối máy chủ.';
  }

  function applyBrand(s){
    const name = s.businessName || 'Đặt Sân Cầu Lông';
    document.getElementById('brandName').textContent = name;
    document.getElementById('footerName').textContent = name;
    document.getElementById('hotlineLabel').textContent = s.hotline || 'Chưa cài';
    document.getElementById('brandSub').textContent = s.hotline ? ('Hotline: '+s.hotline) : 'Nhanh • rõ lịch • không trùng sân';
    document.getElementById('heroAddress').textContent = s.address || 'Lịch sân cập nhật trực tiếp, tự động chặn giờ đã có khách và tối ưu cho điện thoại.';
  }

  function setupQuickDate(){
    const el=document.getElementById('quickDate');
    el.min=state.bootstrap.today;
    const max=parseLocalDate(state.bootstrap.today); max.setDate(max.getDate()+state.bootstrap.maxAdvanceDays);
    el.max=toDateString(max); el.value=state.selectedDate;
  }

  function pickCustomDate(value){ if(!value)return; state.selectedDate=value; buildDateStrip(); loadAvailability(); }

  function buildDateStrip(){
    const root = document.getElementById('dateStrip'); root.innerHTML='';
    const start = parseLocalDate(state.bootstrap.today);
    const days = Math.min(state.bootstrap.maxAdvanceDays + 1, 21);
    for(let i=0;i<days;i++){
      const d = new Date(start); d.setDate(d.getDate()+i);
      const ds = toDateString(d);
      const btn = document.createElement('button'); btn.className='date-chip'+(ds===state.selectedDate?' active':'');
      const wd = i===0?'Hôm nay':new Intl.DateTimeFormat('vi-VN',{weekday:'short'}).format(d);
      btn.innerHTML = `<span>${wd}</span><b>${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}</b>`;
      btn.onclick = async()=>{state.selectedDate=ds;buildDateStrip();await loadAvailability();}; root.appendChild(btn);
    }
    updateSelectedDateLabel();
    const q=document.getElementById('quickDate'); if(q)q.value=state.selectedDate;
  }

  function goToday(){ state.selectedDate=state.bootstrap.today; buildDateStrip(); loadAvailability(); }
  function updateSelectedDateLabel(){
    const d=parseLocalDate(state.selectedDate); document.getElementById('todayLabel').textContent = `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}`;
  }

  async function loadAvailability(){
    const root=document.getElementById('availability'); root.innerHTML='<div class="loading"><div class="spinner"></div>Đang tải lịch sân…</div>';
    updateSelectedDateLabel();
    try{ state.availability=await gas('getAvailability',state.selectedDate); renderAvailability(); }
    catch(e){ root.innerHTML=`<div class="empty">${esc(e.message)}</div>`; }
  }

  function renderAvailability(){
    const root=document.getElementById('availability');
    if(!state.availability.courts.length){ root.innerHTML='<div class="empty">Hiện chưa có sân nào đang mở nhận lịch.</div>'; return; }
    const wrap=document.createElement('div');wrap.className='courts';
    state.availability.courts.forEach(c=>{
      const card=document.createElement('div');card.className='court-card';
      const slots=c.slots.map((s,i)=>`<button class="slot" ${s.available?'':'disabled'} onclick="selectSlot('${attr(c.id)}','${attr(s.start)}',${i})">${esc(s.start)}</button>`).join('');
      card.innerHTML=`<div class="court-top"><div><div class="court-name">${esc(c.name)}</div><div class="court-type">${esc(c.type)} • ${esc(c.openTime)}–${esc(c.closeTime)}</div></div><div class="price"><b>${money(c.pricePerSlot)}</b><span>/${c.slotMinutes} phút</span></div></div><div class="slot-grid">${slots}</div><div class="legend"><span><i class="dot free"></i>Còn trống</span><span><i class="dot busy"></i>Đã đặt / đã qua</span></div>`;
      wrap.appendChild(card);
    });
    root.innerHTML='';root.appendChild(wrap);
  }

  function selectSlot(courtId,startTime,slotIndex){
    const court=state.availability.courts.find(c=>c.id===courtId); if(!court)return;
    const durations=[]; let consecutive=0;
    for(let i=slotIndex;i<court.slots.length && consecutive<3;i++){
      if(!court.slots[i].available)break; consecutive++; durations.push(consecutive*court.slotMinutes);
    }
    state.bookingSelection={court,date:state.selectedDate,startTime,durations};
    openBookingModal();
  }

  function openBookingModal(){
    const s=state.bookingSelection,c=s.court; const lastName=localStorage.getItem('bookName')||'',lastPhone=localStorage.getItem('bookPhone')||'';
    const options=s.durations.map(d=>`<option value="${d}">${d} phút • ${money((d/c.slotMinutes)*c.pricePerSlot)}</option>`).join('');
    const root=document.getElementById('modalRoot');
    root.innerHTML=`<div class="modal-backdrop" onclick="backdropClose(event)"><div class="modal" id="bookingModal"><div class="modal-head"><h3>Xác nhận đặt sân</h3><button class="icon-btn btn-sm" onclick="closeModal()">✕</button></div><div class="modal-body"><div class="booking-summary"><div><span>SÂN</span><b>${esc(c.name)}</b></div><div><span>NGÀY</span><b>${formatDateVN(s.date)}</b></div><div><span>BẮT ĐẦU</span><b>${esc(s.startTime)}</b></div></div><div class="form-grid"><div class="field full"><label>Thời lượng</label><select id="bookDuration" class="select" onchange="updateBookPrice()">${options}</select></div><div class="field"><label>Họ tên *</label><input id="bookName" class="input" maxlength="80" value="${attr(lastName)}" placeholder="Nguyễn Văn A"></div><div class="field"><label>Số điện thoại *</label><input id="bookPhone" class="input" maxlength="16" inputmode="tel" value="${attr(lastPhone)}" placeholder="09xxxxxxxx"></div><div class="field full"><label>Ghi chú</label><textarea id="bookNote" class="textarea" maxlength="500" placeholder="Ví dụ: cần thuê vợt, đến muộn 5 phút…"></textarea></div></div><div style="display:flex;justify-content:space-between;gap:10px;align-items:center;margin-top:13px"><span class="muted">Tạm tính</span><b id="bookPrice" style="font-size:22px;color:#bfffd7"></b></div><p class="fine">${esc(state.bootstrap.settings.bookingNote||'')}</p></div><div class="modal-foot"><button class="btn" onclick="closeModal()">Quay lại</button><button id="confirmBookBtn" class="btn btn-primary" onclick="submitBooking()">Giữ lịch ngay</button></div></div></div>`;
    updateBookPrice(); setTimeout(()=>document.getElementById('bookName').focus(),80);
  }

  function updateBookPrice(){const s=state.bookingSelection,c=s.court,d=Number(document.getElementById('bookDuration').value);document.getElementById('bookPrice').textContent=money((d/c.slotMinutes)*c.pricePerSlot);}

  async function submitBooking(){
    const btn=document.getElementById('confirmBookBtn');
    const payload={date:state.bookingSelection.date,courtId:state.bookingSelection.court.id,startTime:state.bookingSelection.startTime,durationMinutes:Number(document.getElementById('bookDuration').value),customerName:document.getElementById('bookName').value,phone:document.getElementById('bookPhone').value,note:document.getElementById('bookNote').value};
    if(!payload.customerName.trim()||!payload.phone.trim()){toast('Vui lòng nhập họ tên và số điện thoại.','err');return;}
    setBusy(btn,true,'Đang giữ lịch…');
    try{
      const res=await gas('createBooking',payload); localStorage.setItem('bookName',payload.customerName.trim());localStorage.setItem('bookPhone',payload.phone.trim()); showBookingSuccess(res.booking); await loadAvailability();
    }catch(e){toast(e.message,'err');setBusy(btn,false,'Giữ lịch ngay');}
  }

  function showBookingSuccess(b){
    document.getElementById('modalRoot').innerHTML=`<div class="modal-backdrop"><div class="modal"><div class="success"><div class="check">✓</div><h3>Đã giữ lịch thành công</h3><p class="muted">Bạn lưu lại mã dưới đây để tra cứu hoặc hủy lịch khi còn ở trạng thái chờ.</p><div class="code-box">${esc(b.code)}</div><div class="result-grid"><div class="kv"><span>Sân</span><b>${esc(b.courtName)}</b></div><div class="kv"><span>Thời gian</span><b>${esc(b.startTime)}–${esc(b.endTime)}</b></div><div class="kv"><span>Ngày</span><b>${formatDateVN(b.date)}</b></div><div class="kv"><span>Tạm tính</span><b>${money(b.amount)}</b></div></div><button class="btn btn-primary" style="width:100%;margin-top:16px" onclick="closeModal()">Xong</button></div></div></div>`;
  }

  function closeModal(){document.getElementById('modalRoot').innerHTML='';}
  function backdropClose(e){if(e.target.classList.contains('modal-backdrop'))closeModal();}

  async function lookupBookingUI(){
    const code=document.getElementById('lookupCode').value,phone=document.getElementById('lookupPhone').value,root=document.getElementById('lookupResult');
    root.innerHTML='<div class="loading"><div class="spinner"></div>Đang tra cứu…</div>';
    try{const res=await gas('lookupBooking',code,phone);renderLookup(res.booking);}catch(e){root.innerHTML=`<div class="empty">${esc(e.message)}</div>`;}
  }
  function renderLookup(b){
    const canCancel=b.status==='Pending';
    document.getElementById('lookupResult').innerHTML=`<div class="result-card"><div style="display:flex;justify-content:space-between;gap:10px;align-items:flex-start"><div><div class="muted" style="font-size:11px">MÃ ĐẶT SÂN</div><h3 style="margin:4px 0">${esc(b.code)}</h3></div><span class="status s-${attr(b.status)}">${esc(STATUS_LABEL[b.status]||b.status)}</span></div><div class="result-grid"><div class="kv"><span>Sân</span><b>${esc(b.courtName)}</b></div><div class="kv"><span>Ngày</span><b>${formatDateVN(b.date)}</b></div><div class="kv"><span>Giờ</span><b>${esc(b.startTime)}–${esc(b.endTime)}</b></div><div class="kv"><span>Tạm tính</span><b>${money(b.amount)}</b></div><div class="kv"><span>Khách</span><b>${esc(b.customerName)}</b></div><div class="kv"><span>Thanh toán</span><b>${esc(PAY_LABEL[b.paymentStatus]||b.paymentStatus)}</b></div></div>${b.note?`<p class="fine">Ghi chú: ${esc(b.note)}</p>`:''}${canCancel?`<button class="btn btn-danger" style="width:100%;margin-top:12px" onclick="cancelLookupBooking('${attr(b.code)}')">Hủy lịch này</button>`:''}</div>`;
  }
  async function cancelLookupBooking(code){
    if(!confirm('Bạn chắc chắn muốn hủy lịch đang chờ xác nhận?'))return;
    try{await gas('cancelMyBooking',code,document.getElementById('lookupPhone').value);toast('Đã hủy lịch.','ok');lookupBookingUI();loadAvailability();}catch(e){toast(e.message,'err');}
  }

  function switchView(name,btn){
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));document.getElementById('view-'+name).classList.add('active');
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active')); if(btn)btn.classList.add('active'); window.scrollTo({top:0,behavior:'smooth'});
  }
