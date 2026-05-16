// ALSONDOS ERP — Main JS

document.addEventListener('DOMContentLoaded', function () {

  // Current date in topbar
  const dateEl = document.getElementById('currentDate');
  if (dateEl) {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-GB', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
  }

  // Sidebar toggle
  window.toggleSidebar = function () {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
  };

  // Auto-dismiss alerts
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
      const bs = bootstrap.Alert.getInstance(a);
      if (bs) bs.close();
      else a.style.display = 'none';
    });
  }, 4000);

  // Animate stat values
  document.querySelectorAll('.stat-value[data-value]').forEach(el => {
    const target = parseFloat(el.dataset.value);
    const isPrice = el.dataset.prefix === '$' || el.dataset.currency;
    let start = 0;
    const duration = 1200;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start = Math.min(start + step, target);
      if (isPrice) {
        el.textContent = '$' + start.toLocaleString('en', { maximumFractionDigits: 0 });
      } else {
        el.textContent = Math.round(start).toLocaleString();
      }
      if (start >= target) clearInterval(timer);
    }, 16);
  });

  // Demo credential click to fill login form
  document.querySelectorAll('.demo-credential').forEach(el => {
    el.addEventListener('click', function () {
      const user = this.dataset.user;
      const pass = this.dataset.pass;
      const uInput = document.getElementById('username');
      const pInput = document.getElementById('password');
      if (uInput) uInput.value = user;
      if (pInput) pInput.value = pass;
    });
  });

  // Table search filter
  const tableSearch = document.getElementById('tableSearch');
  if (tableSearch) {
    tableSearch.addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('.erp-table tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // Animate chart bars
  document.querySelectorAll('.chart-bar[data-pct]').forEach(bar => {
    const pct = bar.dataset.pct;
    bar.style.height = '0%';
    setTimeout(() => { bar.style.height = pct + '%'; }, 200);
  });

});
