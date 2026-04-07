// Auto-detect API base URL from current page location, with fallback
const API_BASE = window.location.origin !== "null" && window.location.origin !== ""
  ? window.location.origin
  : "http://10.93.25.100:8000";
const API = API_BASE;

let tas = [];
let taBookings = {};
let selectedTA = null;
let adminSelectedTA = null;
let weekStart = getMonday(new Date());
let currentMonth = new Date();
let calendarMode = "week";
let sidebarView = "bookings";

// Admin auth
let adminToken = localStorage.getItem("queueless_admin_token") || null;
let adminUsername = localStorage.getItem("queueless_admin_user") || null;
let adminLoggedIn = false;

// ==================== Auth ====================

function authHeaders() {
  const h = { "Content-Type": "application/json" };
  if (adminToken) h["Authorization"] = `Bearer ${adminToken}`;
  return h;
}

function setAdminAuth(token, username) {
  adminToken = token;
  adminUsername = username;
  adminLoggedIn = true;
  localStorage.setItem("queueless_admin_token", token);
  localStorage.setItem("queueless_admin_user", username);
}

function clearAdminAuth() {
  adminToken = null;
  adminUsername = null;
  adminLoggedIn = false;
  localStorage.removeItem("queueless_admin_token");
  localStorage.removeItem("queueless_admin_user");
}

async function tryRestoreSession() {
  if (!adminToken) return;
  try {
    const res = await fetch(`${API}/admin/me`, { headers: { "Authorization": `Bearer ${adminToken}` } });
    if (res.ok) {
      const data = await res.json();
      setAdminAuth(adminToken, data.username);
    } else {
      clearAdminAuth();
    }
  } catch (e) { /* ignore */ }
}

async function adminLogin(username, password) {
  const res = await fetch(`${API}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Login failed.");
  setAdminAuth(data.token, data.username);
  return data;
}

async function adminLogout() {
  if (adminToken) {
    fetch(`${API}/admin/logout`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${adminToken}` },
    }).catch(() => {});
  }
  clearAdminAuth();
}

// ==================== Init ====================
async function init() {
  tas = await fetchJSON(`${API}/tas`);
  await Promise.all(tas.map(async (ta) => {
    taBookings[ta.id] = await fetchJSON(`${API}/tas/${ta.id}/bookings`);
  }));

  await tryRestoreSession();
  renderTAList();
  renderTAListAdmin();
  updateAdminUI();

  if (tas.length > 0) selectTA(tas[0]);

  // Week navigation
  document.getElementById("prevWeek").addEventListener("click", () => {
    weekStart = addDays(weekStart, -7);
    renderCalendar();
    renderSidebarBookings();
  });
  document.getElementById("nextWeek").addEventListener("click", () => {
    weekStart = addDays(weekStart, 7);
    renderCalendar();
    renderSidebarBookings();
  });

  document.getElementById("prevMonth").addEventListener("click", () => {
    currentMonth.setMonth(currentMonth.getMonth() - 1);
    renderMonthCalendar();
  });
  document.getElementById("nextMonth").addEventListener("click", () => {
    currentMonth.setMonth(currentMonth.getMonth() + 1);
    renderMonthCalendar();
  });

  // View toggle
  document.getElementById("viewWeek").addEventListener("click", () => {
    calendarMode = "week";
    document.getElementById("viewWeek").classList.add("active");
    document.getElementById("viewMonth").classList.remove("active");
    document.getElementById("weekNav").style.display = "flex";
    document.getElementById("monthNav").style.display = "none";
    renderCalendar();
  });
  document.getElementById("viewMonth").addEventListener("click", () => {
    calendarMode = "month";
    document.getElementById("viewMonth").classList.add("active");
    document.getElementById("viewWeek").classList.remove("active");
    document.getElementById("monthNav").style.display = "flex";
    document.getElementById("weekNav").style.display = "none";
    renderMonthCalendar();
  });

  // Sidebar tabs
  document.querySelectorAll(".sidebar-nav button").forEach((btn) => {
    btn.addEventListener("click", () => {
      sidebarView = btn.dataset.view;
      document.querySelectorAll(".sidebar-nav button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("sidebarBookings").style.display = sidebarView === "bookings" ? "" : "none";
      document.getElementById("sidebarHistory").style.display = sidebarView === "history" ? "" : "none";
      document.getElementById("sidebarAdmin").style.display = sidebarView === "admin" ? "" : "none";
      document.getElementById("bookingFormCard").style.display = sidebarView === "bookings" ? "" : "none";

      if (sidebarView === "history") {
        if (adminLoggedIn) loadHistory();
        else renderAdminLoginRequired("history");
      }
      if (sidebarView === "admin") {
        document.getElementById("adminPanelMain").classList.add("active");
        if (!adminLoggedIn) renderAdminLoginPanel();
        else loadAdminData();
      } else {
        document.getElementById("adminPanelMain").classList.remove("active");
      }
    });
  });

  // Admin tabs
  document.querySelectorAll(".admin-tab-bar button").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".admin-tab-bar button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      document.querySelectorAll(".admin-tab-content").forEach((c) => c.classList.remove("active"));
      document.getElementById("tab" + capitalize(btn.dataset.tab)).classList.add("active");
    });
  });

  // Login form
  document.getElementById("adminLoginForm").addEventListener("submit", handleAdminLogin);

  // Logout button
  document.getElementById("adminLogoutBtn").addEventListener("click", handleAdminLogout);

  // Change password
  document.getElementById("adminChangePwBtn").addEventListener("click", handleChangePassword);

  // Admin: add hour
  document.getElementById("addAdminHour").addEventListener("click", addAdminHour);
  document.getElementById("addBlocked").addEventListener("click", addBlockedDate);
  document.getElementById("saveNotifConfig").addEventListener("click", saveNotificationConfig);

  document.getElementById("bookingForm").addEventListener("submit", handleBooking);
}

// ==================== Admin Login ====================

async function handleAdminLogin(e) {
  e.preventDefault();
  const username = document.getElementById("adminLoginUser").value.trim();
  const password = document.getElementById("adminLoginPass").value;
  const errEl = document.getElementById("adminLoginError");
  errEl.textContent = "";

  try {
    await adminLogin(username, password);
    errEl.textContent = "";
    updateAdminUI();
    loadAdminData();
  } catch (err) {
    errEl.textContent = err.message;
  }
}

function handleAdminLogout() {
  adminLogout();
  updateAdminUI();
  renderAdminLoginPanel();
}

function updateAdminUI() {
  const loginSection = document.getElementById("adminLoginSection");
  const adminContent = document.getElementById("adminContentWrapper");
  const historySidebar = document.getElementById("historyLoginOverlay");

  if (adminLoggedIn) {
    loginSection.style.display = "none";
    adminContent.style.display = "";
    if (historySidebar) historySidebar.style.display = "none";
    document.getElementById("adminUserBadge").textContent = `🔓 ${adminUsername}`;
  } else {
    loginSection.style.display = "";
    adminContent.style.display = "none";
  }
}

function renderAdminLoginPanel() {
  const el = document.getElementById("adminPanel");
  el.innerHTML = `
    <div style="padding:12px 0;">
      <p style="font-size:13px;color:#ad1457;margin-bottom:10px;font-weight:700;">🔒 Admin Login Required</p>
      <p style="font-size:11px;color:#888;margin-bottom:8px;">Login to manage hours, block dates, and configure notifications.</p>
    </div>`;
}

function renderAdminLoginRequired(forSection) {
  const el = document.getElementById("historyList");
  if (forSection === "history") {
    el.innerHTML = `<div style="padding:16px;text-align:center;">
      <p style="font-size:13px;color:#ad1457;font-weight:700;">🔒 Admin login required</p>
      <p style="font-size:11px;color:#888;margin-top:4px;">Go to the Admin tab and login to view history.</p>
    </div>`;
  }
}

// ==================== TA Selection List ====================
function renderTAList() {
  const el = document.getElementById("taList");
  el.innerHTML = tas
    .map((ta) => `
    <li class="ta-item${selectedTA && selectedTA.id === ta.id ? " active" : ""}" data-id="${ta.id}">
      <div class="ta-name">${escapeHtml(ta.name)}</div>
      <div class="ta-subject">${escapeHtml(ta.subject)}</div>
    </li>`).join("");

  el.querySelectorAll(".ta-item").forEach((item) => {
    item.addEventListener("click", () => {
      const ta = tas.find((t) => t.id === parseInt(item.dataset.id, 10));
      selectTA(ta);
    });
  });
}

function renderTAListAdmin() {
  const el = document.getElementById("taListAdmin");
  el.innerHTML = tas
    .map((ta) => `
    <li class="ta-item${adminSelectedTA && adminSelectedTA.id === ta.id ? " active" : ""}" data-id="${ta.id}">
      <div class="ta-name">${escapeHtml(ta.name)}</div>
      <div class="ta-subject">${escapeHtml(ta.subject)}</div>
    </li>`).join("");

  el.querySelectorAll(".ta-item").forEach((item) => {
    item.addEventListener("click", () => {
      adminSelectedTA = tas.find((t) => t.id === parseInt(item.dataset.id, 10));
      renderTAListAdmin();
      if (adminLoggedIn) loadAdminData();
    });
  });
}

async function selectTA(ta) {
  selectedTA = ta;
  document.getElementById("taTitle").textContent = `📅 ${ta.name} — ${ta.subject}`;
  renderTAList();
  renderSidebarBookings();
  if (calendarMode === "week") await renderCalendar();
  else renderMonthCalendar();
}

// ==================== Sidebar Bookings ====================
function renderSidebarBookings() {
  const nameEl = document.getElementById("taBookingsName");
  const listEl = document.getElementById("taBookingsList");
  const userEmail = localStorage.getItem("queueless_email") || "";

  if (!selectedTA) {
    nameEl.textContent = "";
    listEl.innerHTML = '<div class="ta-empty">Select a TA to see bookings</div>';
    return;
  }

  nameEl.textContent = selectedTA.name;

  const bookings = (taBookings[selectedTA.id] || []).filter((b) => {
    const bDate = new Date(b.start);
    const ws = new Date(weekStart);
    const we = addDays(ws, 7);
    return bDate >= ws && bDate < we;
  }).sort((a, b) => new Date(a.start) - new Date(b.start));

  if (bookings.length === 0) {
    listEl.innerHTML = '<div class="ta-empty">No bookings this week</div>';
    return;
  }

  listEl.innerHTML = bookings.map((b) => {
    const d = b.start.split("T")[0];
    const t = b.start.split("T")[1].substring(0, 5);
    const dayName = new Date(b.start).toLocaleDateString("en-GB", { weekday: "short" });
    const isOwn = b.email === userEmail;
    return `
      <div class="sidebar-slot${isOwn ? " own" : ""}">
        <div class="ss-info">
          <div class="ss-name">${escapeHtml(b.name)}</div>
          <div class="ss-time">${dayName}, ${d} · ${t} · ${b.duration} min</div>
        </div>
        ${isOwn ? `<button class="cancel-btn" onclick="cancelBooking(${b.id}, ${selectedTA.id})">✕</button>` : ""}
      </div>`;
  }).join("");
}

// ==================== Calendar (Week View) ====================
async function renderCalendar() {
  const cal = document.getElementById("calendar");
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const weekEnd = addDays(weekStart, 6);
  document.getElementById("weekLabel").textContent = `${fmt(weekStart)} — ${fmt(weekEnd)}`;

  let bookings = [];
  let blockedDates = [];
  if (selectedTA) {
    bookings = taBookings[selectedTA.id] || [];
    try {
      const res = await fetch(`${API}/admin/blocked/${selectedTA.id}`, { headers: authHeaders() });
      if (res.ok) blockedDates = await res.json();
    } catch (e) { blockedDates = []; }
  }

  const today = new Date(); today.setHours(0, 0, 0, 0);
  const userEmail = localStorage.getItem("queueless_email") || "";
  const blockedSet = new Set(blockedDates.map((bd) => bd.date));

  let html = days.map((d) => `<div class="cal-header">${d}</div>`).join("");

  for (let i = 0; i < 7; i++) {
    const day = addDays(weekStart, i);
    const dayStr = isoDate(day);
    const isToday = day.getTime() === today.getTime();
    const isBlocked = blockedSet.has(dayStr);
    const dayBookings = bookings.filter((b) => b.start.split("T")[0] === dayStr);

    let slotsHtml = "";
    if (isBlocked) {
      slotsHtml = '<div class="blocked-label">🚫 Blocked</div>';
    } else if (dayBookings.length > 0) {
      slotsHtml = dayBookings.map((b) => {
        const t = b.start.split("T")[1].substring(0, 5);
        const isOwn = b.email === userEmail;
        return `
          <div class="cal-slot${isOwn ? " own" : ""}">
            <button class="cancel-btn" ${isOwn ? `onclick="cancelBooking(${b.id}, ${b.ta_id})"` : "disabled style='opacity:.3;cursor:default'"}>✕</button>
            <div class="slot-name">${escapeHtml(b.name)}</div>
            <div class="slot-time">${t} · ${b.duration} min</div>
          </div>`;
      }).join("");
    } else {
      slotsHtml = '<div class="empty-day">—</div>';
    }

    html += `<div class="cal-day${isToday ? " today" : ""}${isBlocked ? " blocked" : ""}">
        <div class="day-date">${day.getDate()}</div>${slotsHtml}</div>`;
  }
  cal.innerHTML = html;
}

// ==================== Calendar (Month View) ====================
async function renderMonthCalendar() {
  const container = document.getElementById("monthCalendar");
  const year = currentMonth.getFullYear();
  const month = currentMonth.getMonth();

  const monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  document.getElementById("monthLabel").textContent = `${monthNames[month]} ${year}`;

  let bookings = [];
  let blockedDates = [];
  if (selectedTA) {
    bookings = taBookings[selectedTA.id] || [];
    try {
      const res = await fetch(`${API}/admin/blocked/${selectedTA.id}`, { headers: authHeaders() });
      if (res.ok) blockedDates = await res.json();
    } catch (e) { blockedDates = []; }
  }

  const blockedSet = new Set(blockedDates.map((bd) => bd.date));
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  const firstDay = new Date(year, month, 1);
  let startDay = firstDay.getDay();
  startDay = startDay === 0 ? 6 : startDay - 1;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrev = new Date(year, month, 0).getDate();
  const totalCells = Math.ceil((startDay + daysInMonth) / 7) * 7;

  let html = dayNames.map((d) => `<div class="month-header-cell">${d}</div>`).join("");

  for (let i = 0; i < totalCells; i++) {
    let dayNum, isOther = false;
    if (i < startDay) { dayNum = daysInPrev - startDay + 1 + i; isOther = true; }
    else if (i >= startDay + daysInMonth) { dayNum = i - startDay - daysInMonth + 1; isOther = true; }
    else { dayNum = i - startDay + 1; }

    const dayDate = isOther ? new Date(year, month + (i < startDay ? -1 : 1), dayNum) : new Date(year, month, dayNum);
    const dayStr = isoDate(dayDate);
    const isToday = !isOther && dayDate.getTime() === today.getTime();
    const isBlocked = blockedSet.has(dayStr);
    const dayBookings = bookings.filter((b) => b.start.split("T")[0] === dayStr);

    let dotsHtml = "";
    if (dayBookings.length > 0) {
      dotsHtml = dayBookings.slice(0, 5).map(() => '<span class="md-dot"></span>').join("");
      if (dayBookings.length > 5) dotsHtml += `<div class="md-count">+${dayBookings.length - 5} more</div>`;
    }

    html += `<div class="month-day${isToday ? " today" : ""}${isOther ? " other-month" : ""}${isBlocked ? " blocked" : ""}">
        <div class="md-date">${dayNum}</div>
        ${isBlocked ? '<div class="blocked-label">🚫</div>' : dotsHtml}</div>`;
  }
  container.innerHTML = `<div class="month-grid">${html}</div>`;
}

// ==================== Booking Form ====================
async function handleBooking(e) {
  e.preventDefault();
  const msg = document.getElementById("message");
  msg.className = ""; msg.style.display = "none";

  if (!selectedTA) { showMessage("Please select a TA first.", "error"); return; }

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const telegram = document.getElementById("telegram").value.trim();
  const date = document.getElementById("date").value;
  const time = document.getElementById("time").value;
  const duration = document.getElementById("duration").value;

  if (!email.endsWith("@innopolis.university")) {
    showMessage("Email must end with @innopolis.university", "error"); return;
  }

  try {
    const res = await fetch(`${API}/book`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, telegram, date, time, duration: parseInt(duration, 10), ta_id: selectedTA.id }),
    });
    const data = await res.json();
    if (res.ok) {
      showMessage(data.message || "Booking created!", "success");
      localStorage.setItem("queueless_email", email);
      document.getElementById("bookingForm").reset();
      taBookings[selectedTA.id] = await fetchJSON(`${API}/tas/${selectedTA.id}/bookings`);
      weekStart = getMonday(new Date(`${date}T00:00:00`));
      if (calendarMode === "week") renderCalendar(); else renderMonthCalendar();
      renderSidebarBookings();
    } else {
      showMessage(data.error || "Booking failed.", "error");
    }
  } catch (err) {
    showMessage("Could not connect to the server.", "error");
    console.error(err);
  }
}

async function cancelBooking(id, taId) {
  const email = localStorage.getItem("queueless_email") || "";
  try {
    const res = await fetch(`${API}/bookings/${id}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const data = await res.json();
    if (res.ok) {
      taBookings[taId] = await fetchJSON(`${API}/tas/${taId}/bookings`);
      if (calendarMode === "week") renderCalendar(); else renderMonthCalendar();
      renderSidebarBookings();
    } else { alert(data.error || "Could not cancel."); }
  } catch (err) { alert("Connection error."); console.error(err); }
}

// ==================== Admin Data ====================
async function loadAdminData() {
  if (!adminSelectedTA || !adminLoggedIn) return;

  try {
    const res = await fetch(`${API}/admin/hours/${adminSelectedTA.id}`, { headers: authHeaders() });
    if (res.ok) renderAdminHours(await res.json());
  } catch (e) { console.error(e); }

  try {
    const res = await fetch(`${API}/admin/blocked/${adminSelectedTA.id}`, { headers: authHeaders() });
    if (res.ok) renderAdminBlocked(await res.json());
  } catch (e) { console.error(e); }

  try {
    const res = await fetch(`${API}/admin/notifications`, { headers: authHeaders() });
    if (res.ok) renderNotifConfig(await res.json());
  } catch (e) { console.error(e); }
}

function renderAdminHours(hours) {
  const el = document.getElementById("adminHoursList");
  const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  if (!hours || hours.length === 0) {
    el.innerHTML = '<p class="ta-empty">No hours defined — all times are available by default.</p>';
    return;
  }
  el.innerHTML = hours.map((h) => `
    <div class="admin-row">
      <span>${dayNames[h.day_of_week]}</span>
      <span>${h.start_time} — ${h.end_time}</span>
      <button class="remove-btn" onclick="removeAdminHour(${h.id})">✕</button>
    </div>`).join("");
}

async function addAdminHour() {
  if (!adminSelectedTA || !adminLoggedIn) { alert("Login as admin first."); return; }
  const dayOfWeek = parseInt(document.getElementById("adminHourDay").value, 10);
  const startTime = document.getElementById("adminHourStart").value;
  const endTime = document.getElementById("adminHourEnd").value;
  if (!startTime || !endTime) { alert("Start and end time required."); return; }

  try {
    const res = await fetch(`${API}/admin/hours`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ ta_id: adminSelectedTA.id, day_of_week: dayOfWeek, start_time: startTime, end_time: endTime }),
    });
    if (res.ok) loadAdminData();
    else { const d = await res.json(); alert(d.error || "Failed."); }
  } catch (e) { alert("Connection error."); }
}

async function removeAdminHour(id) {
  try {
    const res = await fetch(`${API}/admin/hours/${id}`, { method: "DELETE", headers: authHeaders() });
    if (res.ok) loadAdminData(); else alert("Failed.");
  } catch (e) { alert("Connection error."); }
}

function renderAdminBlocked(blocked) {
  const el = document.getElementById("adminBlockedList");
  if (!blocked || blocked.length === 0) {
    el.innerHTML = '<p class="ta-empty">No blocked dates.</p>'; return;
  }
  el.innerHTML = blocked.map((b) => `
    <div class="blocked-item">
      <span class="bi-date">${b.date}</span>
      ${b.reason ? `<span class="bi-reason">(${escapeHtml(b.reason)})</span>` : ""}
      <button class="remove-btn" onclick="removeBlockedDate(${b.id})">✕</button>
    </div>`).join("");
}

async function addBlockedDate() {
  if (!adminSelectedTA || !adminLoggedIn) { alert("Login as admin first."); return; }
  const date = document.getElementById("adminBlockDate").value;
  const reason = document.getElementById("adminBlockReason").value.trim();
  if (!date) { alert("Date is required."); return; }

  try {
    const res = await fetch(`${API}/admin/blocked`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ ta_id: adminSelectedTA.id, date, reason }),
    });
    if (res.ok) {
      document.getElementById("adminBlockDate").value = "";
      document.getElementById("adminBlockReason").value = "";
      loadAdminData();
      if (selectedTA) { if (calendarMode === "week") renderCalendar(); else renderMonthCalendar(); }
    } else { const d = await res.json(); alert(d.error || "Failed."); }
  } catch (e) { alert("Connection error."); }
}

async function removeBlockedDate(id) {
  try {
    const res = await fetch(`${API}/admin/blocked/${id}`, { method: "DELETE", headers: authHeaders() });
    if (res.ok) {
      loadAdminData();
      if (selectedTA) { if (calendarMode === "week") renderCalendar(); else renderMonthCalendar(); }
    } else alert("Failed.");
  } catch (e) { alert("Connection error."); }
}

function renderNotifConfig(config) {
  document.getElementById("ncEmailEnabled").checked = config.email_enabled === "true";
  document.getElementById("ncEmailFrom").value = config.email_from || "";
  document.getElementById("ncEmailPassword").value = config.email_password || "";
  document.getElementById("ncEmailTo").value = config.email_to || "";
  document.getElementById("ncTelegramEnabled").checked = config.telegram_enabled === "true";
  document.getElementById("ncTelegramToken").value = config.telegram_bot_token || "";
  document.getElementById("ncTelegramChatId").value = config.telegram_chat_id || "";
}

async function saveNotificationConfig() {
  const payload = {
    email_enabled: document.getElementById("ncEmailEnabled").checked ? "true" : "false",
    email_from: document.getElementById("ncEmailFrom").value.trim(),
    email_password: document.getElementById("ncEmailPassword").value,
    email_to: document.getElementById("ncEmailTo").value.trim(),
    telegram_enabled: document.getElementById("ncTelegramEnabled").checked ? "true" : "false",
    telegram_bot_token: document.getElementById("ncTelegramToken").value.trim(),
    telegram_chat_id: document.getElementById("ncTelegramChatId").value.trim(),
  };

  try {
    const res = await fetch(`${API}/admin/notifications`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });
    if (res.ok) alert("Notification settings saved.");
    else { const d = await res.json(); alert(d.error || "Failed."); }
  } catch (e) { alert("Connection error."); }
}

// ==================== History ====================
async function loadHistory() {
  const el = document.getElementById("historyList");
  el.innerHTML = '<div class="ta-empty">Loading...</div>';

  if (!adminLoggedIn) { renderAdminLoginRequired("history"); return; }

  try {
    const url = selectedTA ? `${API}/admin/history?ta_id=${selectedTA.id}&limit=50` : `${API}/admin/history?limit=50`;
    const res = await fetch(url, { headers: authHeaders() });
    const entries = await res.json();

    if (!entries || entries.length === 0) {
      el.innerHTML = '<div class="ta-empty">No history entries yet.</div>'; return;
    }

    el.innerHTML = entries.map((e) => {
      const when = new Date(e.performed_at).toLocaleString("en-GB");
      const timeStr = e.start ? e.start.split("T")[1].substring(0, 5) : "";
      const dateStr = e.start ? e.start.split("T")[0] : "";
      return `
        <div class="history-entry ${e.action}">
          <div class="he-action ${e.action}">${e.action === "created" ? "✅" : "❌"} ${e.action} ${e.ta_name ? "· " + escapeHtml(e.ta_name) : ""}</div>
          <div class="he-info">
            ${escapeHtml(e.name)} (${escapeHtml(e.email)}) · ${dateStr} ${timeStr} · ${e.duration} min<br>
            <span style="color:#999;">${when} by ${e.performed_by ? escapeHtml(e.performed_by) : "system"}</span>
          </div>
        </div>`;
    }).join("");
  } catch (e) {
    el.innerHTML = '<div class="ta-empty">Failed to load history.</div>';
    console.error(e);
  }
}

async function handleChangePassword() {
  if (!adminLoggedIn) return;
  const current = document.getElementById("adminCurrentPw").value;
  const newPw = document.getElementById("adminNewPw").value;
  const confirm = document.getElementById("adminConfirmPw").value;
  const msgEl = document.getElementById("adminPwMessage");

  if (!current || !newPw || !confirm) { msgEl.textContent = "All fields required."; msgEl.className = "error"; return; }
  if (newPw !== confirm) { msgEl.textContent = "New passwords do not match."; msgEl.className = "error"; return; }
  if (newPw.length < 6) { msgEl.textContent = "Password must be at least 6 characters."; msgEl.className = "error"; return; }

  try {
    const res = await fetch(`${API}/admin/change-password`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ current_password: current, new_password: newPw }),
    });
    const data = await res.json();
    if (res.ok) {
      msgEl.textContent = data.message;
      msgEl.className = "success";
      document.getElementById("adminCurrentPw").value = "";
      document.getElementById("adminNewPw").value = "";
      document.getElementById("adminConfirmPw").value = "";
    } else {
      msgEl.textContent = data.error || "Failed.";
      msgEl.className = "error";
    }
  } catch (e) {
    msgEl.textContent = "Connection error.";
    msgEl.className = "error";
  }
}

// ==================== Helpers ====================
function showMessage(text, type) {
  const msg = document.getElementById("message");
  msg.textContent = text; msg.className = type; msg.style.display = "block";
}

function fetchJSON(url) {
  return fetch(url).then((r) => r.json()).catch(() => []);
}

function getMonday(d) {
  const date = new Date(d);
  const day = date.getDay();
  const diff = (day === 0 ? -6 : 1) - day;
  date.setDate(date.getDate() + diff);
  date.setHours(0, 0, 0, 0);
  return date;
}

function addDays(d, n) { const r = new Date(d); r.setDate(r.getDate() + n); return r; }
function isoDate(d) { return d.toISOString().split("T")[0]; }
function fmt(d) { return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" }); }
function escapeHtml(str) { const el = document.createElement("div"); el.textContent = str; return el.innerHTML; }
function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

// ==================== Start ====================
init();
