/* ==========================================================================
   Hospital Digital Twin - Premium Dashboard JavaScript
   ========================================================================== */

(function () {
  'use strict';

  // ==========================================================================
  // 1. DOM READY
  // ==========================================================================
  document.addEventListener('DOMContentLoaded', function () {

    initSidebar();
    initDarkMode();
    initLiveClock();
    initSearch();
    initNotifications();
    initProfileDropdown();
    initQuickActions();
    initTableSearch();
    initTablePagination();
    initTableSort();
    initCharts();
    initCountUp();
    initCircularProgress();
    initScrollAnimations();
    initLoadingSkeleton();
    initRippleEffect();

    // Show welcome toast
    showToast('success', 'System Online', 'Hospital Digital Twin dashboard loaded successfully.');
  });

  // ==========================================================================
  // 2. SIDEBAR
  // ==========================================================================
  function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const backdrop = document.getElementById('sidebarBackdrop');
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');

    if (!sidebar) return;

    // Toggle collapse
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed');
        document.querySelector('.main-content')?.classList.toggle('expanded');
      });
    }

    // Mobile toggle
    const mobileToggle = document.getElementById('mobileSidebarToggle');
    if (mobileToggle) {
      mobileToggle.addEventListener('click', function () {
        sidebar.classList.toggle('mobile-open');
        backdrop?.classList.toggle('show');
        document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : '';
      });
    }

    if (backdrop) {
      backdrop.addEventListener('click', function () {
        sidebar.classList.remove('mobile-open');
        backdrop.classList.remove('show');
        document.body.style.overflow = '';
      });
    }

    // Active nav item
    navItems.forEach(function (item) {
      item.addEventListener('click', function () {
        navItems.forEach(function (el) { el.classList.remove('active'); });
        item.classList.add('active');

        // Close mobile sidebar
        if (window.innerWidth <= 768) {
          sidebar.classList.remove('mobile-open');
          backdrop?.classList.remove('show');
          document.body.style.overflow = '';
        }
      });
    });
  }

  // ==========================================================================
  // 3. DARK MODE
  // ==========================================================================
  function initDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;

    // Check saved preference
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      updateDarkModeIcon(toggle, true);
    }

    toggle.addEventListener('click', function () {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      if (isDark) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        updateDarkModeIcon(toggle, false);
      } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        updateDarkModeIcon(toggle, true);
      }
    });
  }

  function updateDarkModeIcon(toggle, isDark) {
    const knob = toggle.querySelector('.toggle-knob');
    if (knob) knob.textContent = isDark ? '\u2600' : '\u263E';
  }

  // ==========================================================================
  // 4. LIVE CLOCK
  // ==========================================================================
  function initLiveClock() {
    function updateClock() {
      const now = new Date();
      const timeEl = document.getElementById('liveTime');
      const dateEl = document.getElementById('liveDate');

      if (timeEl) {
        timeEl.textContent = now.toLocaleTimeString('en-US', {
          hour: '2-digit', minute: '2-digit', second: '2-digit',
          hour12: false
        });
      }

      if (dateEl) {
        dateEl.textContent = now.toLocaleDateString('en-US', {
          weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
        });
      }
    }

    updateClock();
    setInterval(updateClock, 1000);
  }

  // ==========================================================================
  // 5. SEARCH
  // ==========================================================================
  function initSearch() {
    const searchInput = document.querySelector('.search-box input');
    if (!searchInput) return;

    searchInput.addEventListener('input', function () {
      const query = this.value.toLowerCase().trim();
      // Search across all visible text in the dashboard
      const searchable = document.querySelectorAll('.stat-card, .table-card, .widget-card, .ai-insights, .chart-card');

      searchable.forEach(function (el) {
        const text = el.textContent.toLowerCase();
        if (query === '') {
          el.style.display = '';
          el.style.opacity = '1';
        } else if (text.includes(query)) {
          el.style.display = '';
          el.style.opacity = '1';
          el.style.borderColor = 'var(--primary)';
          setTimeout(function () { el.style.borderColor = ''; }, 2000);
        } else {
          el.style.display = 'none';
        }
      });
    });

    // Keyboard shortcut
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
      }
    });
  }

  // ==========================================================================
  // 6. NOTIFICATIONS
  // ==========================================================================
  function initNotifications() {
    const notifBtn = document.getElementById('notifBtn');
    const notifDropdown = document.getElementById('notifDropdown');
    const notifDot = document.querySelector('.notification-dot');

    if (!notifBtn || !notifDropdown) return;

    notifBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      notifDropdown.classList.toggle('show');

      // Mark as read
      if (notifDot) {
        notifDot.style.display = 'none';
      }
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!notifBtn.contains(e.target) && !notifDropdown.contains(e.target)) {
        notifDropdown.classList.remove('show');
      }
    });

    // Mark all read
    const markReadBtn = notifDropdown.querySelector('.notif-mark-read');
    if (markReadBtn) {
      markReadBtn.addEventListener('click', function () {
        const unreadItems = notifDropdown.querySelectorAll('.notif-item.unread');
        unreadItems.forEach(function (item) { item.classList.remove('unread'); });
      });
    }
  }

  // ==========================================================================
  // 7. PROFILE DROPDOWN
  // ==========================================================================
  function initProfileDropdown() {
    const profileBtn = document.getElementById('profileBtn');
    const profileDropdown = document.getElementById('profileDropdown');

    if (!profileBtn || !profileDropdown) return;

    profileBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      profileDropdown.classList.toggle('show');
    });

    document.addEventListener('click', function (e) {
      if (!profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
        profileDropdown.classList.remove('show');
      }
    });
  }

  // ==========================================================================
  // 8. QUICK ACTION BUTTONS
  // ==========================================================================
  function initQuickActions() {
    const qaBtns = document.querySelectorAll('.quick-action-btn');
    qaBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const label = this.querySelector('.qa-label')?.textContent || 'Action';
        showToast('info', label, 'Action triggered successfully.');
      });
    });
  }

  // ==========================================================================
  // 9. TABLE SEARCH
  // ==========================================================================
  function initTableSearch() {
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(function (input) {
      input.addEventListener('input', function () {
        const query = this.value.toLowerCase().trim();
        const table = this.closest('.table-card');
        if (!table) return;
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(function (row) {
          const text = row.textContent.toLowerCase();
          row.style.display = text.includes(query) ? '' : 'none';
        });
      });
    });
  }

  // ==========================================================================
  // 10. TABLE PAGINATION
  // ==========================================================================
  function initTablePagination() {
    const paginations = document.querySelectorAll('.table-pagination');
    paginations.forEach(function (pagination) {
      const prevBtn = pagination.querySelector('.page-prev');
      const nextBtn = pagination.querySelector('.page-next');
      const pageBtns = pagination.querySelectorAll('.page-btn');
      const pageInfo = pagination.querySelector('.page-info');
      const table = pagination.closest('.table-card');
      if (!table) return;

      const rows = table.querySelectorAll('tbody tr');
      const perPage = 5;
      let currentPage = 1;
      const totalPages = Math.max(1, Math.ceil(rows.length / perPage));

      function showPage(page) {
        currentPage = Math.max(1, Math.min(page, totalPages));
        rows.forEach(function (row, index) {
          row.style.display = (index >= (currentPage - 1) * perPage && index < currentPage * perPage) ? '' : 'none';
        });

        if (pageInfo) pageInfo.textContent = 'Page ' + currentPage + ' of ' + totalPages;
        if (prevBtn) prevBtn.disabled = currentPage <= 1;
        if (nextBtn) nextBtn.disabled = currentPage >= totalPages;

        pageBtns.forEach(function (btn, i) {
          btn.classList.toggle('active', i + 1 === currentPage);
        });
      }

      if (prevBtn) prevBtn.addEventListener('click', function () { showPage(currentPage - 1); });
      if (nextBtn) nextBtn.addEventListener('click', function () { showPage(currentPage + 1); });
      pageBtns.forEach(function (btn, i) {
        btn.addEventListener('click', function () { showPage(i + 1); });
      });

      showPage(1);
    });
  }

  // ==========================================================================
  // 11. TABLE SORT
  // ==========================================================================
  function initTableSort() {
    const headers = document.querySelectorAll('.table-card table thead th');
    headers.forEach(function (header, colIndex) {
      header.addEventListener('click', function () {
        const table = this.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isNumeric = rows.every(function (r) {
          const cell = r.children[colIndex];
          return cell && !isNaN(parseFloat(cell.textContent.trim()));
        });

        const direction = this.classList.toggle('sort-desc') ? -1 : 1;
        // Remove sort from other headers
        table.querySelectorAll('thead th').forEach(function (th) {
          if (th !== header) { th.classList.remove('sort-desc'); th.classList.remove('sort-asc'); }
        });
        this.classList.toggle('sort-asc', direction === 1);

        rows.sort(function (a, b) {
          const aVal = a.children[colIndex]?.textContent.trim() || '';
          const bVal = b.children[colIndex]?.textContent.trim() || '';
          if (isNumeric) return (parseFloat(aVal) - parseFloat(bVal)) * direction;
          return aVal.localeCompare(bVal) * direction;
        });

        rows.forEach(function (row) { tbody.appendChild(row); });
      });
    });
  }

  // ==========================================================================
  // 12. CHARTS (Chart.js)
  // ==========================================================================
  function initCharts() {
    // Color palette
    const colors = {
      blue: '#2563eb',
      cyan: '#06b6d4',
      teal: '#14b8a6',
      purple: '#8b5cf6',
      orange: '#f97316',
      red: '#ef4444',
      green: '#10b981',
      yellow: '#f59e0b',
    };

    const colorWithOpacity = function (color, opacity) {
      return 'rgba(' + parseInt(color.slice(1,3), 16) + ',' + parseInt(color.slice(3,5), 16) + ',' + parseInt(color.slice(5,7), 16) + ',' + opacity + ')';
    };

    // Chart defaults
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#94a3b8';

    // --- 12a. Bed Occupancy Trend (Line Chart) ---
    var ctx1 = document.getElementById('bedOccupancyChart');
    if (ctx1) {
      new Chart(ctx1, {
        type: 'line',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Occupied',
            data: [142, 138, 145, 152, 148, 155, 150],
            borderColor: colors.blue,
            backgroundColor: function(context) {
              var chart = context.chart;
              var ctx = chart.ctx;
              var gradient = ctx.createLinearGradient(0, 0, 0, chart.height);
              gradient.addColorStop(0, colorWithOpacity(colors.blue, 0.2));
              gradient.addColorStop(1, colorWithOpacity(colors.blue, 0.0));
              return gradient;
            },
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: colors.blue,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointHoverRadius: 6,
            borderWidth: 2.5,
          }, {
            label: 'Available',
            data: [58, 62, 55, 48, 52, 45, 50],
            borderColor: colors.teal,
            backgroundColor: function(context) {
              var chart = context.chart;
              var ctx = chart.ctx;
              var gradient = ctx.createLinearGradient(0, 0, 0, chart.height);
              gradient.addColorStop(0, colorWithOpacity(colors.teal, 0.15));
              gradient.addColorStop(1, colorWithOpacity(colors.teal, 0.0));
              return gradient;
            },
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: colors.teal,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointHoverRadius: 6,
            borderWidth: 2.5,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { intersect: false, mode: 'index' },
          plugins: {
            legend: { display: true, position: 'top', labels: { usePointStyle: true, padding: 16, font: { size: 11 } } },
            tooltip: {
              backgroundColor: '#fff',
              titleColor: '#1e293b',
              bodyColor: '#475569',
              borderColor: '#e2e8f0',
              borderWidth: 1,
              padding: 12,
              cornerRadius: 8,
              boxPadding: 4,
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 11 } } },
            y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 11 } } }
          }
        }
      });
    }

    // --- 12b. Weekly Patient Admissions (Bar Chart) ---
    var ctx2 = document.getElementById('admissionsChart');
    if (ctx2) {
      new Chart(ctx2, {
        type: 'bar',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Admissions',
            data: [24, 18, 30, 22, 28, 15, 20],
            backgroundColor: [
              colorWithOpacity(colors.blue, 0.8),
              colorWithOpacity(colors.cyan, 0.8),
              colorWithOpacity(colors.purple, 0.8),
              colorWithOpacity(colors.teal, 0.8),
              colorWithOpacity(colors.blue, 0.8),
              colorWithOpacity(colors.orange, 0.8),
              colorWithOpacity(colors.green, 0.8),
            ],
            borderColor: [
              colors.blue, colors.cyan, colors.purple,
              colors.teal, colors.blue, colors.orange, colors.green
            ],
            borderWidth: 1,
            borderRadius: 6,
            barPercentage: 0.6,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#fff', titleColor: '#1e293b', bodyColor: '#475569', borderColor: '#e2e8f0', borderWidth: 1, padding: 12, cornerRadius: 8, boxPadding: 4 }
          },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 11 } } },
            y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 11 } } }
          }
        }
      });
    }

    // --- 12c. Department Distribution (Donut Chart) ---
    var ctx3 = document.getElementById('departmentChart');
    if (ctx3) {
      new Chart(ctx3, {
        type: 'doughnut',
        data: {
          labels: ['Cardiology', 'Neurology', 'Pediatrics', 'Orthopedics', 'Emergency', 'Oncology'],
          datasets: [{
            data: [85, 62, 48, 55, 92, 38],
            backgroundColor: [colors.blue, colors.cyan, colors.purple, colors.teal, colors.orange, colors.red],
            borderWidth: 0,
            hoverOffset: 8,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '72%',
          plugins: {
            legend: { position: 'bottom', labels: { usePointStyle: true, padding: 12, font: { size: 11 } } },
            tooltip: { backgroundColor: '#fff', titleColor: '#1e293b', bodyColor: '#475569', borderColor: '#e2e8f0', borderWidth: 1, padding: 12, cornerRadius: 8 }
          }
        }
      });
    }

    // --- 12d. Appointment Analytics (Area Chart) ---
    var ctx4 = document.getElementById('appointmentChart');
    if (ctx4) {
      new Chart(ctx4, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          datasets: [{
            label: 'Appointments',
            data: [320, 280, 350, 410, 380, 420, 390, 440, 470, 430, 490, 520],
            borderColor: colors.purple,
            backgroundColor: function(context) {
              var chart = context.chart;
              var ctx = chart.ctx;
              var gradient = ctx.createLinearGradient(0, 0, 0, chart.height);
              gradient.addColorStop(0, colorWithOpacity(colors.purple, 0.2));
              gradient.addColorStop(1, colorWithOpacity(colors.purple, 0.0));
              return gradient;
            },
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointBackgroundColor: colors.purple,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            borderWidth: 2.5,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#fff', titleColor: '#1e293b', bodyColor: '#475569', borderColor: '#e2e8f0', borderWidth: 1, padding: 12, cornerRadius: 8 }
          },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 11 } } },
            y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 11 } } }
          }
        }
      });
    }

    // --- 12e. Emergency Cases Trend (Line Chart) ---
    var ctx5 = document.getElementById('emergencyChart');
    if (ctx5) {
      new Chart(ctx5, {
        type: 'line',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Emergency Cases',
            data: [12, 8, 15, 10, 18, 22, 14],
            borderColor: colors.red,
            backgroundColor: function(context) {
              var chart = context.chart;
              var ctx = chart.ctx;
              var gradient = ctx.createLinearGradient(0, 0, 0, chart.height);
              gradient.addColorStop(0, colorWithOpacity(colors.red, 0.15));
              gradient.addColorStop(1, colorWithOpacity(colors.red, 0.0));
              return gradient;
            },
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: colors.red,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointHoverRadius: 6,
            borderWidth: 2.5,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#fff', titleColor: '#1e293b', bodyColor: '#475569', borderColor: '#e2e8f0', borderWidth: 1, padding: 12, cornerRadius: 8 }
          },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 11 } } },
            y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 11 } } }
          }
        }
      });
    }
  }

  // ==========================================================================
  // 13. COUNT-UP ANIMATION
  // ==========================================================================
  function initCountUp() {
    var counters = document.querySelectorAll('.card-value');
    var animated = false;

    function animateCounters() {
      if (animated) return;
      animated = true;

      counters.forEach(function (counter) {
        var target = parseFloat(counter.getAttribute('data-target')) || parseFloat(counter.textContent.replace(/[^0-9.]/g, '')) || 0;
        var suffix = counter.getAttribute('data-suffix') || '';
        var prefix = counter.getAttribute('data-prefix') || '';
        var duration = 1500;
        var startTime = null;

        counter.textContent = prefix + '0' + suffix;

        function step(timestamp) {
          if (!startTime) startTime = timestamp;
          var progress = Math.min((timestamp - startTime) / duration, 1);
          var eased = 1 - Math.pow(1 - progress, 3);
          var current = Math.floor(eased * target);
          counter.textContent = prefix + current.toLocaleString() + suffix;
          if (progress < 1) requestAnimationFrame(step);
          else counter.textContent = prefix + target.toLocaleString() + suffix;
        }

        requestAnimationFrame(step);
      });
    }

    // Trigger on scroll
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { animateCounters(); observer.disconnect(); }
      });
    }, { threshold: 0.1 });

    var container = document.querySelector('.stat-cards-grid');
    if (container) observer.observe(container);
    else animateCounters(); // fallback
  }

  // ==========================================================================
  // 14. CIRCULAR PROGRESS (Health Score)
  // ==========================================================================
  function initCircularProgress() {
    var fill = document.querySelector('.progress-fill');
    if (!fill) return;

    var score = parseInt(fill.getAttribute('data-score')) || 92;
    var circumference = 314; // 2 * Math.PI * 50
    var offset = circumference - (score / 100) * circumference;

    // Animate after a short delay
    setTimeout(function () {
      fill.style.strokeDashoffset = offset;
    }, 500);
  }

  // ==========================================================================
  // 15. SCROLL ANIMATIONS (Intersection Observer)
  // ==========================================================================
  function initScrollAnimations() {
    var targets = document.querySelectorAll('.scroll-animate, .animate-on-scroll');

    if (targets.length === 0) return;

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible', 'animated');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05, rootMargin: '0px 0px -50px 0px' });

    targets.forEach(function (el) { observer.observe(el); });
  }

  // ==========================================================================
  // 16. LOADING SKELETON
  // ==========================================================================
  function initLoadingSkeleton() {
    var skeletons = document.querySelectorAll('.skeleton-card, .skeleton-chart');
    setTimeout(function () {
      skeletons.forEach(function (skeleton) {
        skeleton.classList.remove('skeleton', 'skeleton-card', 'skeleton-chart');
        skeleton.style.animation = 'none';
      });
    }, 800);
  }

  // ==========================================================================
  // 17. RIPPLE EFFECT
  // ==========================================================================
  function initRippleEffect() {
    var buttons = document.querySelectorAll('.quick-action-btn');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        var ripple = document.createElement('span');
        var rect = btn.getBoundingClientRect();
        var size = Math.max(rect.width, rect.height);
        var x = e.clientX - rect.left - size / 2;
        var y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = 'position:absolute;width:' + size + 'px;height:' + size + 'px;left:' + x + 'px;top:' + y + 'px;background:rgba(37,99,235,0.15);border-radius:50%;transform:scale(0);animation:ripple-effect 0.6s ease-out;pointer-events:none;';
        btn.style.position = 'relative';
        btn.style.overflow = 'hidden';
        btn.appendChild(ripple);
        setTimeout(function () { ripple.remove(); }, 600);
      });
    });
  }

  // Inject ripple keyframe
  var style = document.createElement('style');
  style.textContent = '@keyframes ripple-effect { to { transform: scale(4); opacity: 0; } }';
  document.head.appendChild(style);

  // ==========================================================================
  // 18. TOAST NOTIFICATION SYSTEM
  // ==========================================================================
  window.showToast = function (type, title, message) {
    var container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    var icons = { success: '\u2713', error: '\u2717', warning: '\u26A0', info: '\u2139' };

    var toast = document.createElement('div');
    toast.className = 'toast-item ' + type;
    toast.innerHTML = '<div class="toast-icon">' + (icons[type] || '\u2139') + '</div><div class="toast-content"><div class="toast-title">' + title + '</div><div class="toast-message">' + message + '</div></div><button class="toast-close">&times;</button>';

    toast.querySelector('.toast-close').addEventListener('click', function () { removeToast(toast); });
    container.appendChild(toast);

    setTimeout(function () { removeToast(toast); }, 4000);
  };

  function removeToast(toast) {
    toast.classList.add('removing');
    setTimeout(function () { toast.remove(); }, 300);
  }

})();
