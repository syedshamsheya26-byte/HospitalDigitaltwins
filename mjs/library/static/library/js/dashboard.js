(function () {
  "use strict";

  const BOOKS_API = "/api/books/";
  const MEMBERS_API = "/api/members/";
  const DEBOUNCE_MS = 300;

  const tbody = document.getElementById("book-tbody");
  const emptyRow = document.getElementById("empty-row");
  const errorRow = document.getElementById("error-row");
  const errorMsg = document.getElementById("error-message");
  const spinner = document.getElementById("spinner-overlay");
  const flashContainer = document.getElementById("flash-container");
  const paginationEl = document.getElementById("book-pagination");

  const filterAvailable = document.getElementById("filter-available");
  const filterAuthor = document.getElementById("filter-author");
  const searchInput = document.getElementById("search-input");

  const memberTbody = document.getElementById("member-tbody");

  const state = {
    available: "",
    author: "",
    search: "",
    page: 1,
  };
  let totalPages = 1;

  function showSpinner() { spinner.classList.remove("d-none"); }
  function hideSpinner() { spinner.classList.add("d-none"); }

  function flash(message, type) {
    type = type || "success";
    const cls = type === "error" ? "flash-error" : "flash-success";
    const div = document.createElement("div");
    div.className = `flash alert ${cls} alert-dismissible fade show`;
    div.role = "alert";
    div.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    flashContainer.appendChild(div);
    setTimeout(() => { div.classList.remove("show"); setTimeout(() => div.remove(), 300); }, 4000);
  }

  function showEmpty() { emptyRow.classList.remove("d-none"); errorRow.classList.add("d-none"); }
  function hideEmpty() { emptyRow.classList.add("d-none"); }
  function showError(message) {
    errorMsg.textContent = message;
    errorRow.classList.remove("d-none");
    emptyRow.classList.add("d-none");
  }
  function hideError() { errorRow.classList.add("d-none"); }

  function esc(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function renderBookRow(book) {
    const tr = document.createElement("tr");
    tr.dataset.id = book.id;

    const available = book.available;
    const badge = available
      ? '<span class="badge bg-success status-badge">Available</span>'
      : '<span class="badge bg-warning text-dark status-badge">Issued</span>';

    const borrowedBy = book.borrowed_by_name ? esc(book.borrowed_by_name) : '<span class="text-muted">—</span>';
    const issueBtn = available
      ? `<button class="btn btn-sm btn-outline-success issue-btn" data-id="${book.id}" data-title="${esc(book.title)}"><i class="bi bi-box-arrow-in-right"></i> Issue</button>`
      : `<button class="btn btn-sm btn-outline-secondary return-btn" data-id="${book.id}"><i class="bi bi-box-arrow-left"></i> Return</button>`;

    tr.innerHTML = `
      <td>${esc(book.title)}</td>
      <td>${esc(book.author)}</td>
      <td><code>${esc(book.isbn)}</code></td>
      <td>${badge}</td>
      <td>${borrowedBy}</td>
      <td>
        ${issueBtn}
        <button class="btn btn-sm btn-outline-danger delete-book-btn" data-id="${book.id}"><i class="bi bi-trash"></i></button>
      </td>
    `;
    return tr;
  }

  function renderBooks(books) {
    hideError();
    const rows = tbody.querySelectorAll("tr:not(#empty-row):not(#error-row)");
    rows.forEach(r => r.remove());
    if (books.length === 0) { showEmpty(); return; }
    hideEmpty();
    books.forEach(b => tbody.appendChild(renderBookRow(b)));
  }

  function renderPagination(count) {
    totalPages = Math.ceil(count / 5) || 1;
    paginationEl.innerHTML = "";
    const prevLi = document.createElement("li");
    prevLi.className = `page-item ${state.page <= 1 ? "disabled" : ""}`;
    prevLi.innerHTML = `<a class="page-link" href="#" data-page="${state.page - 1}">&laquo; Prev</a>`;
    paginationEl.appendChild(prevLi);
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement("li");
      li.className = `page-item ${i === state.page ? "active" : ""}`;
      li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
      paginationEl.appendChild(li);
    }
    const nextLi = document.createElement("li");
    nextLi.className = `page-item ${state.page >= totalPages ? "disabled" : ""}`;
    nextLi.innerHTML = `<a class="page-link" href="#" data-page="${state.page + 1}">&raquo; Next</a>`;
    paginationEl.appendChild(nextLi);
  }

  async function loadBooks() {
    showSpinner();
    try {
      const params = new URLSearchParams();
      params.set("page", state.page);
      if (state.available) params.set("available", state.available);
      if (state.author.trim()) params.set("author", state.author.trim());
      if (state.search.trim()) params.set("search", state.search.trim());

      const r = await fetch(`${BOOKS_API}?${params}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      renderBooks(data.results);
      renderPagination(data.count);
    } catch (err) {
      showError(`Failed to load books: ${err.message}`);
      paginationEl.innerHTML = "";
    } finally {
      hideSpinner();
    }
  }

  function debouncedLoad() {
    state.available = filterAvailable.value;
    state.author = filterAuthor.value;
    state.search = searchInput.value;
    state.page = 1;
    loadBooks();
  }

  let filterTimer = null;
  filterAvailable.addEventListener("change", function () {
    clearTimeout(filterTimer);
    filterTimer = setTimeout(debouncedLoad, DEBOUNCE_MS);
  });
  filterAuthor.addEventListener("input", function () {
    clearTimeout(filterTimer);
    filterTimer = setTimeout(debouncedLoad, DEBOUNCE_MS);
  });
  searchInput.addEventListener("input", function () {
    clearTimeout(filterTimer);
    filterTimer = setTimeout(debouncedLoad, DEBOUNCE_MS);
  });
  searchInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") e.preventDefault();
  });

  paginationEl.addEventListener("click", function (e) {
    const link = e.target.closest(".page-link");
    if (!link) return;
    e.preventDefault();
    const page = parseInt(link.dataset.page, 10);
    if (isNaN(page) || page < 1 || page > totalPages) return;
    state.page = page;
    loadBooks();
  });

  // ─── Issue / Return / Delete (delegated) ───────────────────

  tbody.addEventListener("click", async function (e) {
    const issueBtn = e.target.closest(".issue-btn");
    if (issueBtn) {
      e.preventDefault();
      const bookId = issueBtn.dataset.id;
      const bookTitle = issueBtn.dataset.title;
      await openIssueModal(bookId, bookTitle);
      return;
    }

    const returnBtn = e.target.closest(".return-btn");
    if (returnBtn) {
      e.preventDefault();
      const id = returnBtn.dataset.id;
      try {
        const r = await fetch(`${BOOKS_API}${id}/return/`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        });
        if (!r.ok) {
          const err = await r.json().catch(() => ({}));
          throw new Error(err.error || `HTTP ${r.status}`);
        }
        const book = await r.json();
        updateRow(book);
        flash("Book returned successfully.");
      } catch (err) {
        flash(`Return failed: ${err.message}`, "error");
      }
      return;
    }

    const delBtn = e.target.closest(".delete-book-btn");
    if (delBtn) {
      if (!confirm("Delete this book?")) return;
      const id = delBtn.dataset.id;
      try {
        const r = await fetch(`${BOOKS_API}${id}/`, {
          method: "DELETE",
          headers: { "X-CSRFToken": getCsrf() },
        });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        flash("Book deleted.");
        loadBooks();
      } catch (err) {
        flash(`Delete failed: ${err.message}`, "error");
      }
    }
  });

  function updateRow(book) {
    const row = tbody.querySelector(`tr[data-id="${book.id}"]`);
    if (row) row.replaceWith(renderBookRow(book));
  }

  // ─── Issue Modal ───────────────────────────────────────────

  async function openIssueModal(bookId, bookTitle) {
    document.getElementById("issue-book-id").value = bookId;
    document.getElementById("issue-book-title").textContent = bookTitle;
    const select = document.getElementById("issue-member-select");
    select.innerHTML = '<option value="">— Select member —</option>';
    try {
      const r = await fetch(`${MEMBERS_API}?page_size=100`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const members = data.results || data;
      members.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m.id;
        opt.textContent = `${m.name} (${m.email})`;
        select.appendChild(opt);
      });
    } catch (err) {
      flash("Failed to load members", "error");
    }
    const modal = new bootstrap.Modal(document.getElementById("issueModal"));
    modal.show();
  }

  document.getElementById("issue-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const bookId = document.getElementById("issue-book-id").value;
    const memberId = document.getElementById("issue-member-select").value;
    if (!memberId) { flash("Please select a member", "error"); return; }
    try {
      const r = await fetch(`${BOOKS_API}${bookId}/issue/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        body: JSON.stringify({ member_id: memberId }),
      });
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${r.status}`);
      }
      const book = await r.json();
      updateRow(book);
      bootstrap.Modal.getInstance(document.getElementById("issueModal")).hide();
      flash("Book issued successfully.");
    } catch (err) {
      flash(`Issue failed: ${err.message}`, "error");
    }
  });

  // ─── Add Book ───────────────────────────────────────────────

  document.getElementById("add-book-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const body = Object.fromEntries(formData.entries());
    try {
      const r = await fetch(BOOKS_API, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const errData = await r.json().catch(() => ({}));
        throw new Error(Object.values(errData).flat().join(", ") || `HTTP ${r.status}`);
      }
      e.target.reset();
      bootstrap.Modal.getInstance(document.getElementById("addBookModal")).hide();
      state.page = 1;
      loadBooks();
      flash("Book added successfully.");
    } catch (err) {
      flash(`Add failed: ${err.message}`, "error");
    }
  });

  // ─── Add Member ─────────────────────────────────────────────

  document.getElementById("add-member-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const body = Object.fromEntries(formData.entries());
    try {
      const r = await fetch(MEMBERS_API, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const errData = await r.json().catch(() => ({}));
        throw new Error(Object.values(errData).flat().join(", ") || `HTTP ${r.status}`);
      }
      e.target.reset();
      bootstrap.Modal.getInstance(document.getElementById("addMemberModal")).hide();
      loadMembers();
      flash("Member added successfully.");
    } catch (err) {
      flash(`Add failed: ${err.message}`, "error");
    }
  });

  // ─── Members Table ──────────────────────────────────────────

  function renderMemberRow(member) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${esc(member.name)}</td>
      <td>${esc(member.email)}</td>
      <td>${member.phone ? esc(member.phone) : '<span class="text-muted">—</span>'}</td>
      <td>${member.joined_date}</td>
      <td>
        <button class="btn btn-sm btn-outline-danger delete-member-btn" data-id="${member.id}"><i class="bi bi-trash"></i></button>
      </td>
    `;
    return tr;
  }

  async function loadMembers() {
    try {
      const r = await fetch(`${MEMBERS_API}?page_size=100`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const members = data.results || data;
      memberTbody.innerHTML = "";
      members.forEach(m => memberTbody.appendChild(renderMemberRow(m)));
    } catch (err) {
      flash(`Failed to load members: ${err.message}`, "error");
    }
  }

  memberTbody.addEventListener("click", async function (e) {
    const btn = e.target.closest(".delete-member-btn");
    if (!btn) return;
    if (!confirm("Delete this member?")) return;
    const id = btn.dataset.id;
    try {
      const r = await fetch(`${MEMBERS_API}${id}/`, {
        method: "DELETE",
        headers: { "X-CSRFToken": getCsrf() },
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      loadMembers();
      flash("Member deleted.");
    } catch (err) {
      flash(`Delete failed: ${err.message}`, "error");
    }
  });

  // ─── CSRF ───────────────────────────────────────────────────

  function getCsrf() {
    const name = "csrftoken";
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : "";
  }

  // ─── Init ───────────────────────────────────────────────────

  document.addEventListener("DOMContentLoaded", function () {
    loadBooks();
    loadMembers();
  });

})();
