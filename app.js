/**
 * FEE MANAGEMENT SYSTEM – APP UTILITIES
 * Shared functions: auth, sidebar, formatting, toast, export
 */

// ===== CONSTANTS =====
const CLASSES  = ['Nursery', 'KG', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6', 'Class 7', 'Class 8'];
const SECTIONS = ['A', 'B', 'C', 'D'];
const SESSIONS = ['2026-2027', '2027-2028', '2028-2029', '2029-2030', '2025-2026', '2024-2025'];
const MONTHS   = ['April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'January', 'February', 'March'];
const PAYMENT_MODES = [
  { id: 'Cash',             icon: '💵', label: 'Cash' },
  { id: 'Online Transfer',  icon: '🏦', label: 'Online Transfer' },
  { id: 'UPI',              icon: '📱', label: 'UPI' },
  { id: 'Cheque',           icon: '📄', label: 'Cheque' },
  { id: 'Demand Draft',     icon: '🏛️', label: 'Demand Draft' },
];

// ===== AUTH =====
function getLoggedInUser() {
  return JSON.parse(sessionStorage.getItem('fms_user') || 'null');
}

function checkAuth() {
  const user = getLoggedInUser();
  if (!user) { window.location.href = 'index.html'; return null; }
  return user;
}

function logout() {
  sessionStorage.removeItem('fms_user');
  window.location.href = 'index.html';
}

function isAdmin() {
  const u = getLoggedInUser();
  return u && u.role === 'admin';
}

// ===== FORMATTING =====
function formatCurrency(amount) {
  return '₹' + (amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(str) {
  if (!str) return '—';
  try {
    return new Date(str).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch { return str; }
}

function todayISO() {
  return new Date().toISOString().split('T')[0];
}

// ===== TOAST =====
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// ===== MODAL HELPERS =====
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// Close modal on overlay click
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// ===== SIDEBAR RENDERER =====
function renderSidebar(activePage) {
  const user = checkAuth();
  if (!user) return;

  const nav = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard',     href: 'dashboard.html' },
    { id: 'students',  icon: '👥', label: 'Students',      href: 'students.html' },
    { id: 'fees',      icon: '💰', label: 'Record Fees',   href: 'fees.html' },
    { id: 'reports',   icon: '📋', label: 'Reports',       href: 'reports.html' },
  ];

  const navHtml = nav.map(item => `
    <a href="${item.href}" class="nav-item${activePage === item.id ? ' active' : ''}">
      <span class="nav-icon">${item.icon}</span>
      <span>${item.label}</span>
    </a>
  `).join('');

  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  sidebar.innerHTML = `
    <div class="sidebar-header">
      <div class="school-name">🏫 Primary School</div>
      <div class="app-name">Fee Management System</div>
    </div>
    <div class="sidebar-user">
      <div class="user-avatar">${user.name.charAt(0).toUpperCase()}</div>
      <div class="user-info">
        <div class="user-name">${escHtml(user.name)}</div>
        <div class="user-role">${user.role === 'admin' ? '⚙️ Administrator' : '📚 Teacher'}</div>
      </div>
    </div>
    <div class="sidebar-nav">
      <div class="nav-section-title">Navigation</div>
      ${navHtml}
    </div>
    <div class="sidebar-footer">
      <div class="logout-btn" onclick="logout()">🚪 <span>Logout</span></div>
    </div>
  `;

  const badge = document.getElementById('sessionBadge');
  if (badge) badge.textContent = 'Session: ' + FeeDB.getCurrentSession();
}

// ===== POPULATE SELECT HELPERS =====
function populateSelect(selectEl, options, selectedValue, placeholder) {
  if (!selectEl) return;
  selectEl.innerHTML = '';
  if (placeholder) {
    const opt = document.createElement('option');
    opt.value = ''; opt.textContent = placeholder;
    selectEl.appendChild(opt);
  }
  options.forEach(o => {
    const opt = document.createElement('option');
    if (typeof o === 'string') { opt.value = o; opt.textContent = o; }
    else { opt.value = o.value; opt.textContent = o.label; }
    if (opt.value === selectedValue) opt.selected = true;
    selectEl.appendChild(opt);
  });
}

// ===== EXPORT TO CSV =====
function exportToCSV(rows, filename) {
  const csv = rows.map(r => r.map(cell => `"${String(cell ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

// ===== HTML ESCAPE =====
function escHtml(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ===== RECEIPT RENDERER =====
function buildReceiptHTML(fee, student) {
  const school = 'Primary School';
  const items = [
    { label: 'Tuition Fee',      amount: fee.tuitionFee },
    { label: 'Registration Fee', amount: fee.registrationFee },
    { label: 'Exam Fee',         amount: fee.examFee },
    { label: 'Miscellaneous',    amount: fee.miscFee },
  ].filter(i => parseFloat(i.amount) > 0);

  const rowsHtml = items.map(i => `
    <tr>
      <td>${escHtml(i.label)}</td>
      <td class="amount-col">${formatCurrency(i.amount)}</td>
    </tr>
  `).join('');

  const refLine = fee.transactionRef
    ? `<div class="r-label">Ref / Chq No</div><div class="r-value">${escHtml(fee.transactionRef)}</div>`
    : '';

  return `
    <div class="receipt">
      <div class="receipt-header">
        <h2>🏫 ${escHtml(school)}</h2>
        <div class="school-sub">Fee Management System</div>
        <div class="receipt-title">Fee Receipt</div>
      </div>
      <div class="receipt-no">Receipt No: ${escHtml(fee.receiptNo)}</div>
      <div class="receipt-info">
        <div class="r-label">Student Name</div><div class="r-value">${escHtml(student?.name || '—')}</div>
        <div class="r-label">Father's Name</div><div class="r-value">${escHtml(student?.fatherName || '—')}</div>
        <div class="r-label">Class / Section</div><div class="r-value">${escHtml(student?.class || '—')} – ${escHtml(student?.section || '—')}</div>
        <div class="r-label">Roll No</div><div class="r-value">${escHtml(String(student?.rollNo || '—'))}</div>
        <div class="r-label">Session</div><div class="r-value">${escHtml(fee.session)}</div>
        <div class="r-label">Month</div><div class="r-value">${escHtml(fee.month)}</div>
        <div class="r-label">Payment Date</div><div class="r-value">${formatDate(fee.paymentDate)}</div>
        <div class="r-label">Payment Mode</div><div class="r-value">${escHtml(fee.paymentMode)}</div>
        ${refLine}
      </div>
      <table class="receipt-table">
        <thead><tr><th>Description</th><th class="amount-col">Amount</th></tr></thead>
        <tbody>
          ${rowsHtml}
          <tr class="receipt-total-row">
            <td><strong>Total Amount</strong></td>
            <td class="amount-col"><strong>${formatCurrency(fee.total)}</strong></td>
          </tr>
        </tbody>
      </table>
      ${fee.remarks ? `<div style="font-size:12px;color:#666;margin-top:6px;"><strong>Remarks:</strong> ${escHtml(fee.remarks)}</div>` : ''}
      <div class="signature-area">
        <div>Student / Parent Sign</div>
        <div>Authorised Signature</div>
      </div>
      <div class="receipt-footer">
        This is a computer generated receipt.<br>
        Generated on ${new Date().toLocaleString('en-IN')}
      </div>
    </div>
  `;
}
