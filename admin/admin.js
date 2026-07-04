/* SKINRUSH custom admin panel — thin client for /api/admin/*. */
const API = "/api/admin";
const jget = (u) => fetch(u).then((r) => r.json());
const jpost = (u, body) =>
  fetch(u, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  }).then(async (r) => ({ ok: r.ok, data: await r.json().catch(() => ({})) }));

const IMG = (h) =>
  !h ? "" : h.startsWith("http") ? h : "https://community.akamai.steamstatic.com/economy/image/" + h;
const fmt = (n) => Number(n || 0).toLocaleString("ru-RU").replace(/,/g, " ");
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const loginView = document.getElementById("loginView");
const appView = document.getElementById("appView");
const main = document.getElementById("main");

// ---------- auth ----------
async function boot() {
  const me = await jget(`${API}/me/`).catch(() => ({ authenticated: false }));
  if (me.authenticated) showApp(me.username);
  else showLogin();
}

function showLogin() {
  appView.hidden = true;
  loginView.hidden = false;
}
function showApp(username) {
  loginView.hidden = true;
  appView.hidden = false;
  document.getElementById("whoami").textContent = username || "admin";
  switchView("dashboard");
}

const loginForm = document.getElementById("loginForm");
const loginError = document.getElementById("loginError");
const loginBtn = document.getElementById("loginBtn");
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.textContent = "";
  loginBtn.disabled = true;
  const res = await jpost(`${API}/login/`, {
    username: document.getElementById("loginUser").value,
    password: document.getElementById("loginPass").value,
  });
  loginBtn.disabled = false;
  if (res.ok && res.data.authenticated) {
    document.getElementById("loginPass").value = "";
    showApp(res.data.username);
  } else {
    loginError.textContent = res.data.error || "Kirishда xatolik";
  }
});

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await jpost(`${API}/logout/`);
  showLogin();
});

// ---------- navigation ----------
document.getElementById("nav").addEventListener("click", (e) => {
  const btn = e.target.closest(".nav-item");
  if (!btn) return;
  switchView(btn.dataset.view);
});

function switchView(view) {
  document.querySelectorAll(".nav-item").forEach((b) =>
    b.classList.toggle("is-active", b.dataset.view === view)
  );
  if (view === "dashboard") renderDashboard();
  else if (view === "cases") renderCases();
}

// ---------- dashboard ----------
async function renderDashboard() {
  main.innerHTML = `<div class="page-head"><div>
      <div class="page-title">Dashboard</div>
      <div class="page-sub">Umumiy ko'rsatkichlar</div>
    </div></div>
    <div class="loading">Yuklanmoqda…</div>`;
  const s = await jget(`${API}/stats/`);
  const cards = [
    { n: s.cases, label: "Keyslar", c: "var(--violet)" },
    { n: s.skins, label: "Noyob skinlar", c: "var(--teal)" },
    { n: s.items, label: "Jami elementlar", c: "var(--blue)" },
    { n: s.drops, label: "Droplar", c: "var(--gold)" },
  ];
  main.innerHTML = `
    <div class="page-head"><div>
      <div class="page-title">Dashboard</div>
      <div class="page-sub">Umumiy ko'rsatkichlar</div>
    </div></div>
    <div class="stat-grid">
      ${cards.map((c) => `
        <div class="stat-card" style="--sc:${c.c}">
          <div class="stat-card__num">${fmt(c.n)}</div>
          <div class="stat-card__label">${c.label}</div>
        </div>`).join("")}
    </div>`;
}

// ---------- cases ----------
let casesCache = [];
async function renderCases() {
  main.innerHTML = `
    <div class="page-head">
      <div>
        <div class="page-title">Keyslar</div>
        <div class="page-sub">Barcha keyslar va ularning ichidagi skinlar</div>
      </div>
      <input class="admin-input" id="caseSearch" placeholder="Key qidirish..." />
    </div>
    <div id="casesBody"><div class="loading">Yuklanmoqda…</div></div>`;
  const search = document.getElementById("caseSearch");
  let t;
  search.addEventListener("input", () => {
    clearTimeout(t);
    t = setTimeout(() => loadCases(search.value.trim()), 200);
  });
  loadCases("");
}

async function loadCases(q) {
  const body = document.getElementById("casesBody");
  casesCache = await jget(`${API}/cases/${q ? "?q=" + encodeURIComponent(q) : ""}`);
  body.innerHTML = `
    <div class="table-wrap"><div class="table-scroll"><table>
      <thead><tr>
        <th>Key</th><th>Narx</th><th>Skinlar</th><th>Ochilgan</th>
      </tr></thead>
      <tbody>
        ${casesCache.map((c) => `
          <tr class="clickable" data-id="${c.id}">
            <td><img class="crate-thumb" src="${esc(c.image)}" alt="" onerror="this.style.visibility='hidden'"/>
                <span class="cell-name" style="margin-left:10px">${esc(c.name)}</span></td>
            <td class="coin">${fmt(c.price)}</td>
            <td>${c.items_count}</td>
            <td class="cell-muted">${fmt(c.openings)}</td>
          </tr>`).join("")}
      </tbody>
    </table></div></div>`;
  body.querySelectorAll("tr[data-id]").forEach((tr) =>
    tr.addEventListener("click", () => renderCaseDetail(+tr.dataset.id))
  );
}

async function renderCaseDetail(id) {
  main.innerHTML = `<div class="loading">Yuklanmoqda…</div>`;
  const d = await jget(`${API}/cases/${id}/`);
  const c = d.case;
  main.innerHTML = `
    <button class="back-btn" id="backBtn">‹ Keyslarga qaytish</button>
    <div class="page-head">
      <div style="display:flex;align-items:center;gap:14px">
        <img class="crate-thumb" style="width:70px;height:52px" src="${esc(c.image)}" alt="" onerror="this.style.visibility='hidden'"/>
        <div>
          <div class="page-title">${esc(c.name)}</div>
          <div class="page-sub"><span class="coin">${fmt(c.price)}</span> · ${c.items_count} skin · ${fmt(c.openings)} ochilgan</div>
        </div>
      </div>
    </div>
    <div class="table-wrap"><div class="table-scroll"><table>
      <thead><tr>
        <th>Skin</th><th>Holati</th><th>Ehtimol</th><th>Narx</th><th>Noyoblik</th>
      </tr></thead>
      <tbody>
        ${d.items.map((it) => {
          const ch = it.chance >= 0.1 ? it.chance.toFixed(2) : it.chance.toFixed(3);
          return `<tr>
            <td><img class="thumb" src="${IMG(it.image)}" alt="" onerror="this.style.visibility='hidden'"/>
                <span class="cell-name" style="margin-left:10px">${esc(it.name)}</span></td>
            <td class="cell-muted">${esc(it.wear || "—")}</td>
            <td class="pct">${ch}%</td>
            <td class="coin">${fmt(it.price)}</td>
            <td><span class="rarity-badge" style="background:${esc(it.color) || "#555"}">${esc(it.rarity || "—")}</span></td>
          </tr>`;
        }).join("")}
      </tbody>
    </table></div></div>`;
  document.getElementById("backBtn").addEventListener("click", () => switchView("cases"));
}

boot();
