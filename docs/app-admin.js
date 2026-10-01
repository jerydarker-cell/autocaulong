function openAdmin(){
    document.getElementById('adminTab').classList.remove('hidden'); switchView('admin',document.getElementById('adminTab'));
    if(state.adminToken) enterAdminWithToken().catch(()=>clearAdminSession());
  }

  async function adminLoginUI(btn){
    const email=document.getElementById('adminEmail').value.trim();
    const password=document.getElementById('adminPassword').value;
    if(!email||!password){toast('Nhập email và mật khẩu quản trị.','err');return;}
    setBusy(btn,true,'Đang đăng nhập…');
    try{
      await fbAuth.signInWithEmailAndPassword(email,password);
      state.adminToken='firebase-auth';
      document.getElementById('adminPassword').value='';
      await enterAdminWithToken();
      toast('Đăng nhập quản trị thành công.','ok');
    }catch(e){
      await fbAuth.signOut().catch(()=>{}); state.adminToken='';
      toast(e.message||'Đăng nhập thất bại.','err');
    }finally{setBusy(btn,false,'Đăng nhập');}
  }
  async function enterAdminWithToken(){
    if(!fbAuth.currentUser) throw new Error('Vui lòng đăng nhập quản trị.');
    document.getElementById('adminLogin').classList.add('hidden');document.getElementById('adminPanel').classList.remove('hidden');document.getElementById('adminDate').value=state.selectedDate||state.bootstrap.today;await loadAdmin();
  }
  function clearAdminSession(){state.adminToken='';document.getElementById('adminPanel').classList.add('hidden');document.getElementById('adminLogin').classList.remove('hidden');}
  async function adminLogoutUI(){try{await fbAuth.signOut();}catch(e){}clearAdminSession();toast('Đã đăng xuất.','ok');}

  async function loadAdmin(){
    if(!state.adminToken)return;
    const root=document.getElementById('adminBookings');root.innerHTML='<div class="loading"><div class="spinner"></div>Đang tải dữ liệu…</div>';
    try{
      const filters={date:document.getElementById('adminDate').value,status:document.getElementById('adminStatus').value,search:document.getElementById('adminSearch').value};
      const data=await gas('adminDashboard',state.adminToken,filters);state.adminData=data;renderAdmin(data);
    }catch(e){ if(/đăng nhập|unauthenticated|permission/i.test(e.message)){clearAdminSession();} toast(e.message,'err'); }
  }
  function debouncedAdminSearch(){clearTimeout(state.adminTimer);state.adminTimer=setTimeout(loadAdmin,350);}

  function renderAdmin(data){
    document.getElementById('stToday').textContent=data.summary.todayCount;document.getElementById('stPending').textContent=data.summary.pendingCount;document.getElementById('stConfirmed').textContent=data.summary.confirmedCount;document.getElementById('stRevenue').textContent=money(data.summary.paidRevenue);
    const root=document.getElementById('adminBookings');
    if(!data.bookings.length)root.innerHTML='<div class="empty">Không có lịch đặt phù hợp bộ lọc.</div>';
    else root.innerHTML=data.bookings.map(b=>`<div class="booking-row"><div><h4>${esc(b.customerName)} • ${esc(b.code)}</h4><p>${esc(b.phone)}${b.note?' • '+esc(b.note):''}</p></div><div><h4>${esc(b.courtName)}</h4><p>${formatDateVN(b.date)} • ${esc(b.startTime)}–${esc(b.endTime)} • ${money(b.amount)}</p></div><div><span class="status s-${attr(b.status)}">${esc(STATUS_LABEL[b.status]||b.status)}</span> <span class="status s-${attr(b.paymentStatus)}">${esc(PAY_LABEL[b.paymentStatus]||b.paymentStatus)}</span></div><div class="row-actions"><select class="small-select" onchange="adminUpdate('${attr(b.id)}','status',this.value)">${['Pending','Confirmed','Completed','Cancelled'].map(x=>`<option ${x===b.status?'selected':''}>${x}</option>`).join('')}</select><select class="small-select" onchange="adminUpdate('${attr(b.id)}','paymentStatus',this.value)">${['Unpaid','Paid','Refunded'].map(x=>`<option ${x===b.paymentStatus?'selected':''}>${x}</option>`).join('')}</select></div></div>`).join('');
    renderAdminCourts(data.courts); renderAdminSettings(data.settings);
  }

  async function adminUpdate(id,key,value){try{const u={};u[key]=value;await gas('adminUpdateBooking',state.adminToken,id,u);toast('Đã cập nhật.','ok');await loadAdmin();await loadAvailability();}catch(e){toast(e.message,'err');await loadAdmin();}}

  function renderAdminCourts(courts){
    document.getElementById('adminCourts').innerHTML=courts.map(c=>`<div class="court-admin-item"><div><b>${esc(c.name)}</b><div class="fine">${esc(c.type)}</div></div><div><b>${esc(c.openTime)}–${esc(c.closeTime)}</b><div class="fine">${c.slotMinutes} phút/slot</div></div><div><b>${money(c.pricePerSlot)}</b><div class="fine">${c.active?'Đang mở':'Đang tắt'}</div></div><div style="text-align:right"><button class="btn btn-sm" onclick="openCourtEditor('${attr(c.id)}')">Sửa</button></div></div>`).join('');
  }

  function openCourtEditor(id=''){
    const c=id&&state.adminData?state.adminData.courts.find(x=>x.id===id):null;
    const x=c||{id:'',name:'',type:'Tiêu chuẩn',openTime:'05:00',closeTime:'23:00',slotMinutes:60,pricePerSlot:80000,active:true};
    document.getElementById('modalRoot').innerHTML=`<div class="modal-backdrop" onclick="backdropClose(event)"><div class="modal"><div class="modal-head"><h3>${c?'Sửa sân':'Thêm sân'}</h3><button class="icon-btn btn-sm" onclick="closeModal()">✕</button></div><div class="modal-body"><input id="courtId" type="hidden" value="${attr(x.id)}"><div class="form-grid"><div class="field"><label>Tên sân</label><input id="courtName" class="input" value="${attr(x.name)}"></div><div class="field"><label>Loại sân</label><input id="courtType" class="input" value="${attr(x.type)}"></div><div class="field"><label>Mở cửa</label><input id="courtOpen" class="input" type="time" value="${attr(x.openTime)}"></div><div class="field"><label>Đóng cửa</label><input id="courtClose" class="input" type="time" value="${attr(x.closeTime)}"></div><div class="field"><label>Phút / slot</label><select id="courtSlot" class="select">${[30,60,90].map(v=>`<option value="${v}" ${v===Number(x.slotMinutes)?'selected':''}>${v} phút</option>`).join('')}</select></div><div class="field"><label>Giá / slot</label><input id="courtPrice" class="input" type="number" inputmode="numeric" value="${Number(x.pricePerSlot)}"></div><div class="field full"><label><input id="courtActive" type="checkbox" ${x.active?'checked':''}> Đang nhận lịch</label></div></div></div><div class="modal-foot"><button class="btn" onclick="closeModal()">Hủy</button><button class="btn btn-primary" onclick="saveCourtUI()">Lưu sân</button></div></div></div>`;
  }

  async function saveCourtUI(){
    const payload={id:document.getElementById('courtId').value,name:document.getElementById('courtName').value,type:document.getElementById('courtType').value,openTime:document.getElementById('courtOpen').value,closeTime:document.getElementById('courtClose').value,slotMinutes:Number(document.getElementById('courtSlot').value),pricePerSlot:Number(document.getElementById('courtPrice').value),active:document.getElementById('courtActive').checked};
    try{await gas('adminSaveCourt',state.adminToken,payload);closeModal();toast('Đã lưu cấu hình sân.','ok');await loadAdmin();state.bootstrap=await gas('getBootstrap');applyBrand(state.bootstrap.settings);await loadAvailability();}catch(e){toast(e.message,'err');}
  }

  function renderAdminSettings(s){document.getElementById('setBusiness').value=s.businessName||'';document.getElementById('setHotline').value=s.hotline||'';document.getElementById('setAddress').value=s.address||'';document.getElementById('setNote').value=s.bookingNote||'';}
  async function saveSettingsUI(){
    const s={businessName:document.getElementById('setBusiness').value,hotline:document.getElementById('setHotline').value,address:document.getElementById('setAddress').value,bookingNote:document.getElementById('setNote').value};
    try{const res=await gas('adminSaveSettings',state.adminToken,s);state.bootstrap.settings=res.settings;applyBrand(res.settings);toast('Đã lưu thông tin hệ thống.','ok');}catch(e){toast(e.message,'err');}
  }
  async function changePinUI(){
    const oldPassword=document.getElementById('oldPassword').value,newPassword=document.getElementById('newPassword').value;
    const user=fbAuth.currentUser;
    if(!user||!user.email){toast('Vui lòng đăng nhập lại.','err');return;}
    if(newPassword.length<6){toast('Mật khẩu mới phải có ít nhất 6 ký tự.','err');return;}
    try{
      const cred=firebase.auth.EmailAuthProvider.credential(user.email,oldPassword);
      await user.reauthenticateWithCredential(cred);
      await user.updatePassword(newPassword);
      document.getElementById('oldPassword').value='';document.getElementById('newPassword').value='';
      toast('Đổi mật khẩu thành công.','ok');
    }catch(e){toast(e.message||'Không đổi được mật khẩu.','err');}
  }

  function setBusy(btn,busy,text){if(!btn)return;btn.disabled=busy;btn.dataset.old=btn.dataset.old||btn.textContent;btn.textContent=busy?text:(text||btn.dataset.old);}
  function money(v){return new Intl.NumberFormat('vi-VN').format(Number(v||0))+'đ';}
  function parseLocalDate(s){const [y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d);}
  function toDateString(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
  function formatDateVN(s){const d=parseLocalDate(s);return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()}`;}
  function esc(v){return String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));}
  function attr(v){return esc(v).replace(/`/g,'&#096;');}
  function toast(msg,type='ok'){const r=document.getElementById('toastWrap'),d=document.createElement('div');d.className='toast '+type;d.textContent=msg;r.appendChild(d);setTimeout(()=>d.remove(),3500);}
  function showFatal(e){document.getElementById('availability').innerHTML=`<div class="empty"><b>Không tải được ứng dụng.</b><br>${esc(e.message||e)}</div>`;}

