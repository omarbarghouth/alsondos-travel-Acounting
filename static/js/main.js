/* ═══════════════════════════════════════════════════
   ALSONDOS ERP — main.js
   ═══════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {

  // ── Topbar date ──────────────────────────────────────
  const dateEl = document.getElementById('topbar-date');
  if (dateEl) {
    dateEl.textContent = new Date().toLocaleDateString('en-GB',
      { weekday:'short', day:'numeric', month:'short', year:'numeric' });
  }

  // ── Sidebar toggle ───────────────────────────────────
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('sb-overlay');
  const toggleBtn = document.getElementById('sidebar-toggle');
  const open  = () => { sidebar.classList.add('open');  overlay.classList.add('open'); };
  const close = () => { sidebar.classList.remove('open'); overlay.classList.remove('open'); };
  if (toggleBtn) toggleBtn.addEventListener('click', open);
  if (overlay)   overlay.addEventListener('click', close);

  // ── Flash auto-dismiss ───────────────────────────────
  document.querySelectorAll('.flash-close').forEach(b =>
    b.addEventListener('click', () => b.closest('.flash-msg')?.remove()));
  setTimeout(() => {
    document.querySelectorAll('.flash-msg').forEach(el => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 420);
    });
  }, 5000);

  // ── Profit auto-calc ─────────────────────────────────
  const costEl   = document.getElementById('net_cost');
  const sellEl   = document.getElementById('sell_price');
  const profitDisp = document.getElementById('profit_display');
  const profitInp  = document.getElementById('profit');

  function calcProfit() {
    const cost   = parseFloat(costEl?.value) || 0;
    const sell   = parseFloat(sellEl?.value) || 0;
    const profit = sell - cost;
    if (profitDisp) profitDisp.textContent = fmtJOD(profit);
    if (profitInp)  profitInp.value = profit.toFixed(3);
    // Visual cue for negative profit
    const box = profitDisp?.closest('.profit-display');
    if (box) box.style.background = profit < 0
      ? 'linear-gradient(135deg,#7f1d1d,#991b1b)'
      : 'linear-gradient(135deg,var(--navy),var(--navy-light))';
  }
  costEl?.addEventListener('input', calcProfit);
  sellEl?.addEventListener('input', calcProfit);
  calcProfit();

  // ── Service-type selector ────────────────────────────
  const serviceBtns  = document.querySelectorAll('.service-btn');
  const serviceInput = document.getElementById('service_type');
  const PKG_COMPONENTS = {
    Package:       ['pkg-hotel','pkg-flight','pkg-transfer','pkg-tour','pkg-visa'],
    Hotel:         ['pkg-hotel'],
    Flight:        ['pkg-flight'],
    Transfer:      ['pkg-transfer'],
    Tour:          ['pkg-tour'],
    Visa:          ['pkg-visa'],
    Insurance:     [],
    Transportation:[],
  };

  function showPkgSections(type) {
    const show = PKG_COMPONENTS[type] || [];
    document.querySelectorAll('.pkg-section').forEach(sec => {
      sec.classList.toggle('visible', show.includes(sec.dataset.pkg));
    });
  }

  serviceBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      serviceBtns.forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      const t = btn.dataset.service;
      if (serviceInput) serviceInput.value = t;
      showPkgSections(t);
    });
  });

  // Init from existing value (edit mode)
  if (serviceInput?.value) {
    serviceBtns.forEach(b => {
      if (b.dataset.service === serviceInput.value) b.classList.add('selected');
    });
    showPkgSections(serviceInput.value);
  }

  // ── Delete confirm modal ─────────────────────────────
  const deleteModal  = document.getElementById('delete-modal');
  const deleteForm   = document.getElementById('delete-form');
  const deleteName   = document.getElementById('delete-name');
  const deleteCancel = document.getElementById('delete-cancel');

  document.querySelectorAll('[data-delete-url]').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      if (deleteModal) {
        deleteModal.classList.add('open');
        if (deleteForm) deleteForm.action = btn.dataset.deleteUrl;
        if (deleteName) deleteName.textContent = btn.dataset.deleteName || 'this record';
      }
    });
  });
  deleteCancel?.addEventListener('click', () => deleteModal?.classList.remove('open'));
  deleteModal?.addEventListener('click', e => {
    if (e.target === deleteModal) deleteModal.classList.remove('open');
  });

  // ── Table client search ──────────────────────────────
  const tblSearch = document.getElementById('table-search');
  if (tblSearch) {
    tblSearch.addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('.erp-table tbody tr').forEach(r => {
        r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ── Nights auto-calc ─────────────────────────────────
  const ciEl = document.getElementById('hotel_checkin');
  const coEl = document.getElementById('hotel_checkout');
  const nEl  = document.getElementById('hotel_nights');
  function calcNights() {
    if (!ciEl || !coEl || !nEl) return;
    const ci = new Date(ciEl.value), co = new Date(coEl.value);
    if (ci && co && co > ci)
      nEl.value = Math.round((co - ci) / 86400000);
  }
  ciEl?.addEventListener('change', calcNights);
  coEl?.addEventListener('change', calcNights);

  // ── Payment remaining display ────────────────────────
  const payAmt      = document.getElementById('pay_amount');
  const remDisplay  = document.getElementById('remaining-display');
  const owedEl      = document.getElementById('total-owed');
  const totalOwed   = parseFloat(owedEl?.dataset.amount || 0);
  payAmt?.addEventListener('input', () => {
    const rem = totalOwed - (parseFloat(payAmt.value) || 0);
    if (remDisplay) {
      remDisplay.textContent = fmtJOD(rem);
      remDisplay.style.color = rem <= 0 ? 'var(--success)' : 'var(--red-mid)';
    }
  });

  // ── KPI number animation ─────────────────────────────
  document.querySelectorAll('.kpi-value[data-num]').forEach(el => {
    const target = parseFloat(el.dataset.num) || 0;
    const isJod  = el.dataset.jod === '1';
    if (target === 0) return;
    let current = 0;
    const step  = target / (900 / 16);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = isJod ? fmtJOD(current) : Math.round(current).toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 16);
  });

  // ── Print trigger ────────────────────────────────────
  document.querySelectorAll('[data-print]').forEach(b =>
    b.addEventListener('click', () => window.print()));

  // ── Utility: format JOD ──────────────────────────────
  function fmtJOD(n) {
    return (isNaN(n) ? 0 : n).toLocaleString('en',
      { minimumFractionDigits:3, maximumFractionDigits:3 }) + ' JOD';
  }
});
