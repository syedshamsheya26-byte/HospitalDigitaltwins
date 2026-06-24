document.addEventListener('DOMContentLoaded', function () {

  // ===== SIDEBAR TOGGLE (Mobile) =====
  var toggle = document.getElementById('mobileToggle');
  var sidebar = document.getElementById('sidebar');
  var backdrop = document.getElementById('sidebarBackdrop');

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      if (backdrop) backdrop.classList.toggle('show');
    });
    if (backdrop) {
      backdrop.addEventListener('click', function () {
        sidebar.classList.remove('open');
        backdrop.classList.remove('show');
      });
    }
  }

  // ===== ACTIVE NAV ITEM =====
  var currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(function (el) {
    if (el.getAttribute('href') === currentPath) {
      el.classList.add('active');
    }
  });

  // ===== AUTO DISMISS ALERTS =====
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      if (alert.parentNode) {
        alert.style.transition = 'opacity 0.3s ease';
        alert.style.opacity = '0';
        setTimeout(function () { if (alert.parentNode) alert.remove(); }, 300);
      }
    }, 5000);
  });

  // ===== COUNT-UP ANIMATION =====
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    setTimeout(function () {
      counters.forEach(function (el) {
        var target = parseFloat(el.getAttribute('data-count')) || 0;
        if (target > 0) {
          var duration = 1200;
          var startTime = null;
          function step(ts) {
            if (!startTime) startTime = ts;
            var progress = Math.min((ts - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = Math.floor(eased * target);
            var text = el.textContent;
            if (text.includes('/')) {
              var parts = text.split('/');
              el.textContent = current + '/' + parts[1];
            } else {
              el.textContent = current;
            }
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = target + (text.includes('/') ? '/' + text.split('/')[1] : '');
          }
          requestAnimationFrame(step);
        }
      });
    }, 100);
  }

  // ===== CHARTS (if canvases exist) =====
  var bedOccCanvas = document.getElementById('bedOccupancyChart');
  if (bedOccCanvas && typeof Chart !== 'undefined') {
    new Chart(bedOccCanvas, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Occupied Beds',
          data: [65, 70, 68, 72, 75, 73, 71],
          borderColor: '#1a73e8',
          backgroundColor: 'rgba(26,115,232,0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#1a73e8',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  var bedDistCanvas = document.getElementById('bedDistributionChart');
  if (bedDistCanvas && typeof Chart !== 'undefined') {
    new Chart(bedDistCanvas, {
      type: 'doughnut',
      data: {
        labels: ['ICU', 'General', 'Emergency', 'VIP'],
        datasets: [{
          data: [30, 45, 15, 10],
          backgroundColor: ['#1a73e8', '#0d9488', '#f59e0b', '#8b5cf6'],
          borderWidth: 0,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { padding: 16, usePointStyle: true, font: { size: 12 } }
          }
        }
      }
    });
  }

  // ===== TABLE SEARCH =====
  var searchInput = document.getElementById('globalSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      var q = this.value.toLowerCase();
      document.querySelectorAll('.table-wrapper table tbody tr').forEach(function (row) {
        var text = row.textContent.toLowerCase();
        row.style.display = text.indexOf(q) > -1 ? '' : 'none';
      });
    });
  }

  // ===== TABLE PAGINATION (simple) =====
  var tables = document.querySelectorAll('.table-wrapper table');
  tables.forEach(function (table) {
    var rows = table.querySelectorAll('tbody tr');
    var perPage = 8;
    if (rows.length <= perPage) return;

    var wrapper = table.closest('.table-wrapper') || table.parentElement;
    var paginationDiv = document.createElement('div');
    paginationDiv.className = 'pagination-info d-flex justify-between align-center';
    paginationDiv.innerHTML = '<span class="text-muted">Showing 1-' + Math.min(perPage, rows.length) + ' of ' + rows.length + '</span>';

    var btnGroup = document.createElement('div');
    btnGroup.className = 'd-flex gap-2';
    var prevBtn = document.createElement('button');
    prevBtn.className = 'btn btn-sm btn-ghost';
    prevBtn.innerHTML = '<i class="bi bi-chevron-left"></i> Prev';
    prevBtn.disabled = true;
    var nextBtn = document.createElement('button');
    nextBtn.className = 'btn btn-sm btn-ghost';
    nextBtn.innerHTML = 'Next <i class="bi bi-chevron-right"></i>';

    btnGroup.appendChild(prevBtn);
    btnGroup.appendChild(nextBtn);
    paginationDiv.appendChild(btnGroup);

    if (wrapper.nextElementSibling && wrapper.nextElementSibling.classList.contains('pagination-info')) {
      // already has pagination
    } else {
      wrapper.parentElement.insertBefore(paginationDiv, wrapper.nextSibling);
    }

    var currentPage = 0;
    var totalPages = Math.ceil(rows.length / perPage);

    function showPage(page) {
      currentPage = page;
      var start = page * perPage;
      var end = Math.min(start + perPage, rows.length);
      rows.forEach(function (r, i) { r.style.display = (i >= start && i < end) ? '' : 'none'; });
      paginationDiv.querySelector('span').textContent = 'Showing ' + (start + 1) + '-' + end + ' of ' + rows.length;
      prevBtn.disabled = page === 0;
      nextBtn.disabled = page >= totalPages - 1;
    }

    showPage(0);
    prevBtn.addEventListener('click', function () { if (currentPage > 0) showPage(currentPage - 1); });
    nextBtn.addEventListener('click', function () { if (currentPage < totalPages - 1) showPage(currentPage + 1); });
  });
});