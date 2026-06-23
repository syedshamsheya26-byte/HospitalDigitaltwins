// ═══════════════════════════════════════════════════════════════════════
// Module 6 — AJAX Dashboard JS
// Patterns: fetch + async/await • CSRF • DOM manipulation • delegation
// ═══════════════════════════════════════════════════════════════════════

// ── CSRF Token Helper (official Django docs pattern) ──────────────────
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}
const csrftoken = getCookie("csrftoken");

// ── Flash Message (Bootstrap alert, auto-dismiss) ────────────────────
function flash(msg, type = "info") {
  const div = document.createElement("div");
  div.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
  div.textContent = msg;
  document.body.appendChild(div);
  setTimeout(() => div.remove(), 3000);
}

// ── UI State Helpers ──────────────────────────────────────────────────
function showSpinner() {
  document.getElementById("spinner").classList.remove("d-none");
}
function hideSpinner() {
  document.getElementById("spinner").classList.add("d-none");
}
function showEmpty(msg) {
  const tbody = document.querySelector("#students-tbody");
  tbody.innerHTML = `<tr id="empty-row"><td colspan="5" class="text-center text-muted py-4">${msg}</td></tr>`;
}
function showError(msg) {
  const tbody = document.querySelector("#students-tbody");
  tbody.innerHTML = `<tr id="empty-row"><td colspan="5" class="text-center text-danger py-4">${msg}</td></tr>`;
}

// ── Safe Row Builder (createElement + textContent — XSS-proof) ────────
function addRow(student) {
  const tbody = document.querySelector("#students-tbody");
  const emptyRow = document.getElementById("empty-row");
  if (emptyRow) emptyRow.remove();

  const tr = document.createElement("tr");
  tr.id = `student-row-${student.id}`;

  for (const val of [student.roll, student.name, student.email, student.department__name || ""]) {
    const td = document.createElement("td");
    td.textContent = val;
    tr.appendChild(td);
  }

  const tdActions = document.createElement("td");
  tdActions.innerHTML = `
    <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${student.id}" data-name="${student.name}">
      <i class="bi bi-trash"></i>
    </button>`;
  tr.appendChild(tdActions);

  tbody.appendChild(tr);
}

function renderStudents(students) {
  const tbody = document.querySelector("#students-tbody");
  tbody.innerHTML = "";
  const countEl = document.querySelector("#student-count");
  const statEl = document.querySelector("#stat-students");
  if (countEl) countEl.textContent = `${students.length} student${students.length !== 1 ? "s" : ""}`;
  if (statEl) statEl.textContent = students.length;
  if (students.length === 0) {
    showEmpty("No students found.");
    return;
  }
  students.forEach(addRow);
}

// ── Debounce (§3.2 — search-as-you-type) ──────────────────────────────
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// ── Fetch Students (GET) ──────────────────────────────────────────────
async function loadStudents(query = "") {
  showSpinner();
  try {
    const url = query
      ? `/api/students/?search=${encodeURIComponent(query)}`
      : "/api/students/";
    const r = await fetch(url);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    renderStudents(data.students);
  } catch (err) {
    showError("Could not load students. Check server connection.");
  } finally {
    hideSpinner();
  }
}

// ── Live Search (debounced) ──────────────────────────────────────────
const runSearch = debounce((q) => {
  loadStudents(q);
}, 300);

// ── Create Student (POST via JSON) ────────────────────────────────────
async function handleAddStudent(form) {
  const btn = form.querySelector("[type=submit]");
  btn.disabled = true;
  btn.textContent = "Saving…";

  try {
    const r = await fetch("/api/students/add/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({
        roll: form.roll.value.trim(),
        name: form.name.value.trim(),
        email: form.email.value.trim(),
      }),
    });
    const body = await r.json();
    if (r.ok) {
      addRow(body);
      form.reset();
      flash("Student added successfully ✅", "success");
      document.querySelector("#addStudentModal .btn-close")?.click();
    } else {
      showFieldErrors(form, body.errors ?? body);
    }
  } catch {
    flash("Network error — try again", "danger");
  } finally {
    btn.disabled = false;
    btn.textContent = "Add Student";
  }
}

// ── Inline Field Errors (§2.5) ────────────────────────────────────────
function showFieldErrors(form, errors) {
  form.querySelectorAll(".invalid-feedback").forEach((el) => el.remove());
  form.querySelectorAll(".is-invalid").forEach((el) => el.classList.remove("is-invalid"));
  for (const [field, msgs] of Object.entries(errors)) {
    const input = form[field];
    if (!input) continue;
    input.classList.add("is-invalid");
    const fb = document.createElement("div");
    fb.className = "invalid-feedback";
    fb.textContent = msgs.join(" ");
    input.after(fb);
  }
}

// ── Delete Student (delegated — §1.10, §2.4) ──────────────────────────
async function deleteStudent(id, name) {
  if (!confirm(`Delete student "${name}"?`)) return;
  try {
    const r = await fetch(`/api/students/${id}/delete/`, {
      method: "DELETE",
      headers: { "X-CSRFToken": csrftoken },
    });
    if (r.status === 204) {
      document.querySelector(`#student-row-${id}`)?.remove();
      flash("Student deleted.", "warning");
      if (document.querySelector("#students-tbody").children.length === 0) {
        showEmpty("No students found.");
      }
    } else {
      flash("Delete failed.", "danger");
    }
  } catch {
    flash("Network error — try again", "danger");
  }
}

// ── Initialise — DOMContentLoaded (§1.9) ──────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadStudents();

  // Live search listener
  const searchInput = document.querySelector("#search-students");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => runSearch(e.target.value.trim()));
  }

  // Create form — intercept submit (preventDefault!)
  const addForm = document.querySelector("#add-student-form");
  if (addForm) {
    addForm.addEventListener("submit", (e) => {
      e.preventDefault();
      handleAddStudent(e.target);
    });
  }

  // Delete — delegation on the tbody (§1.10)
  const tbody = document.querySelector("#students-tbody");
  if (tbody) {
    tbody.addEventListener("click", (e) => {
      const btn = e.target.closest(".delete-btn");
      if (btn) {
        deleteStudent(btn.dataset.id, btn.dataset.name);
      }
    });
  }
});
