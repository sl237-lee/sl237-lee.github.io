/* js/main.js — drop-in replacement
   Features:
   - Theme toggle (dark/light) with persistence
   - Scroll progress bar
   - Reveal-on-scroll animations
   - Hero counters (count-up)
   - Project search + tag filters
   - Architecture modal (inline SVG diagrams)
   - GitHub API (recent repos + caching + refresh)
*/

(() => {
  "use strict";

  // ---------------------------
  // Helpers
  // ---------------------------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (c) => {
      switch (c) {
        case "&": return "&amp;";
        case "<": return "&lt;";
        case ">": return "&gt;";
        case "\"": return "&quot;";
        case "'": return "&#39;";
        default: return c;
      }
    });
  }

  function timeAgo(iso) {
    try {
      const d = new Date(iso);
      const s = Math.floor((Date.now() - d.getTime()) / 1000);
      const m = Math.floor(s / 60);
      const h = Math.floor(m / 60);
      const day = Math.floor(h / 24);
      if (day > 0) return `${day}d ago`;
      if (h > 0) return `${h}h ago`;
      if (m > 0) return `${m}m ago`;
      return "just now";
    } catch {
      return "";
    }
  }

  // ---------------------------
  // Theme toggle (supports html[data-theme="auto|dark|light"])
  // ---------------------------
  const root = document.documentElement;
  const themeToggle = $("#themeToggle");
  const themeIcon = $("#themeIcon");

  function preferredTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark" || saved === "light") return saved;
    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    return mq && mq.matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    // If user stores explicit theme, set it; else keep auto but resolve icon
    if (theme === "auto") {
      root.setAttribute("data-theme", "auto");
      const t = preferredTheme();
      if (themeIcon) themeIcon.textContent = t === "dark" ? "☾" : "☀";
      return;
    }
    root.setAttribute("data-theme", theme);
    if (themeIcon) themeIcon.textContent = theme === "dark" ? "☾" : "☀";
  }

  function initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark" || saved === "light") applyTheme(saved);
    else applyTheme("auto");

    // React to OS theme changes when in auto mode
    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    if (mq) {
      mq.addEventListener?.("change", () => {
        if (!localStorage.getItem("theme")) applyTheme("auto");
      });
    }
  }

  function toggleTheme() {
    const current = root.getAttribute("data-theme") || "auto";
    // If current is auto, toggle to opposite of preferred
    if (current === "auto") {
      const next = preferredTheme() === "dark" ? "light" : "dark";
      localStorage.setItem("theme", next);
      applyTheme(next);
      return;
    }
    const next = current === "dark" ? "light" : "dark";
    localStorage.setItem("theme", next);
    applyTheme(next);
  }

  initTheme();
  themeToggle?.addEventListener("click", toggleTheme);

  // ---------------------------
  // Scroll progress bar
  // ---------------------------
  const scrollbarFill = $("#scrollbarFill");
  function updateScrollBar() {
    if (!scrollbarFill) return;
    const doc = document.documentElement;
    const scrollTop = doc.scrollTop || document.body.scrollTop;
    const scrollHeight = doc.scrollHeight - doc.clientHeight;
    const pct = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
    scrollbarFill.style.width = `${pct}%`;
  }
  window.addEventListener("scroll", updateScrollBar, { passive: true });
  updateScrollBar();

  // ---------------------------
  // Toast
  // ---------------------------
  const toast = $("#toast");
  let toastTimer = null;
  function showToast(text) {
    if (!toast) return;
    toast.textContent = text || "Copied";
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 1200);
  }

  // ---------------------------
  // Copy email
  // ---------------------------
  const copyEmailBtn = $("#copyEmailBtn");
  copyEmailBtn?.addEventListener("click", async () => {
    const email = copyEmailBtn.getAttribute("data-email") || "";
    if (!email) return;
    try {
      await navigator.clipboard.writeText(email);
      showToast("Email copied");
    } catch {
      const tmp = document.createElement("textarea");
      tmp.value = email;
      document.body.appendChild(tmp);
      tmp.select();
      document.execCommand("copy");
      document.body.removeChild(tmp);
      showToast("Email copied");
    }
  });

  // Back to top
  const toTopBtn = $("#toTopBtn");
  toTopBtn?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  // ---------------------------
  // Reveal-on-scroll
  // ---------------------------
  const revealEls = $$(".reveal");
  if (revealEls.length) {
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        }
      },
      { threshold: 0.12 }
    );
    revealEls.forEach((el) => io.observe(el));
  }

  // ---------------------------
  // Count-up metrics
  // ---------------------------
  function animateCount(el) {
    const target = Number(el.getAttribute("data-countup") || "0");
    const suffix = el.getAttribute("data-suffix") || "";
    const duration = 900;
    const start = performance.now();

    function frame(now) {
      const t = clamp((now - start) / duration, 0, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const val = Math.round(target * eased);
      el.textContent = `${val}${suffix}`;
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  const countEls = $$("[data-countup]");
  if (countEls.length) {
    const countIO = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            animateCount(e.target);
            countIO.unobserve(e.target);
          }
        }
      },
      { threshold: 0.6 }
    );
    countEls.forEach((el) => countIO.observe(el));
  }

  // ---------------------------
  // Project search + filter
  // ---------------------------
  const projectGrid = $("#projectGrid");
  const projectSearch = $("#projectSearch");
  const filterBtns = $$(".chip-btn");

  function getActiveFilter() {
    const active = filterBtns.find((b) => b.classList.contains("active"));
    return active ? (active.getAttribute("data-filter") || "all") : "all";
  }

  function matchesFilter(card, filter) {
    if (filter === "all") return true;
    const tags = (card.getAttribute("data-tags") || "").toLowerCase();
    return tags.includes(filter);
  }

  function matchesSearch(card, q) {
    if (!q) return true;
    const hay = (
      (card.getAttribute("data-title") || "") +
      " " +
      (card.getAttribute("data-tags") || "") +
      " " +
      (card.textContent || "")
    ).toLowerCase();
    return hay.includes(q);
  }

  function applyProjectFiltering() {
    if (!projectGrid) return;

    const q = (projectSearch?.value || "").trim().toLowerCase();
    const filter = getActiveFilter();

    const cards = $$(".card", projectGrid);
    let visible = 0;

    for (const c of cards) {
      const ok = matchesFilter(c, filter) && matchesSearch(c, q);
      c.classList.toggle("is-hidden", !ok);
      if (ok) visible += 1;
    }

    if (projectSearch) {
      projectSearch.setAttribute("aria-label", `Search projects. ${visible} shown.`);
    }
  }

  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      applyProjectFiltering();
    });
  });

  projectSearch?.addEventListener("input", applyProjectFiltering);
  applyProjectFiltering();

  // ---------------------------
  // Architecture modal (supports the modal markup in your index.html)
  // ---------------------------
  const archModal = $("#archModal");
  const archModalTitle = $("#archModalTitle");
  const archDiagram = $("#archDiagram");
  const archModalClose = $("#archModalClose");

  function openArchModal(title, key) {
    if (!archModal || !archDiagram || !archModalTitle) return;
    archModalTitle.textContent = title || "Architecture";
    archDiagram.innerHTML = buildArchSvg(key || "default");
    archModal.classList.add("open");
    archModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeArchModal() {
    if (!archModal || !archDiagram) return;
    archModal.classList.remove("open");
    archModal.setAttribute("aria-hidden", "true");
    archDiagram.innerHTML = "";
    document.body.style.overflow = "";
  }

  archModalClose?.addEventListener("click", closeArchModal);

  archModal?.addEventListener("click", (e) => {
    const t = e.target;
    if (t && t.getAttribute && t.getAttribute("data-close") === "true") closeArchModal();
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeArchModal();
  });

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-arch]");
    if (!btn) return;
    const key = btn.getAttribute("data-arch");
    const title = btn.getAttribute("data-modal-title") || "Architecture";
    openArchModal(title, key);
  });

  function buildArchSvg(key) {
    // Produces a consistent inline SVG so it looks crisp without images.
    const base = (content, caption) => `
      <svg viewBox="0 0 1100 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Architecture diagram">
        <defs>
          <linearGradient id="g1" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="rgba(117,199,255,0.0)"/>
            <stop offset="45%" stop-color="rgba(117,199,255,0.95)"/>
            <stop offset="100%" stop-color="rgba(138,125,255,0.75)"/>
          </linearGradient>
          <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <rect x="0" y="0" width="1100" height="540" fill="transparent"/>
        ${content}
        ${caption ? `<text x="50" y="520" fill="rgba(234,242,251,0.70)" font-size="12">${escapeHtml(caption)}</text>` : ``}
      </svg>
    `;

    const box = (x, y, w, h, label, sub) => `
      <g>
        <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="16" ry="16"
              fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.14)"/>
        <text x="${x + 16}" y="${y + 30}" fill="currentColor" font-size="13" font-weight="900">
          ${escapeHtml(label)}
        </text>
        ${sub ? `<text x="${x + 16}" y="${y + 52}" fill="rgba(234,242,251,0.65)" font-size="12">${escapeHtml(sub)}</text>` : ``}
      </g>
    `;

    const arrow = (x1, y1, x2, y2) => `
      <g filter="url(#glow)" opacity="0.95">
        <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="url(#g1)" stroke-width="2"/>
        <circle cx="${x2}" cy="${y2}" r="3.5" fill="rgba(117,199,255,0.85)"></circle>
      </g>
    `;

    // Layouts
    if (key === "social") {
      return base(`
        ${box(50, 70, 290, 86, "YouTube Reporting/Analytics API", "Platform metrics")}
        ${box(380, 70, 290, 86, "Ingestion Jobs", "Connectors + retries")}
        ${box(710, 70, 340, 86, "Delta Lake (Bronze/Silver)", "ACID + schema evolution")}
        ${arrow(340, 113, 380, 113)}
        ${arrow(670, 113, 710, 113)}

        ${box(50, 210, 290, 86, "Enterprise Clickstream", "Large-scale events")}
        ${box(380, 210, 290, 86, "PySpark Transforms", "Joins + attribution")}
        ${box(710, 210, 340, 86, "DQ Gates", "Schema + null checks")}
        ${arrow(340, 253, 380, 253)}
        ${arrow(670, 253, 710, 253)}

        ${box(380, 360, 290, 86, "Serving Tables", "Curated ROI datasets")}
        ${box(710, 360, 340, 86, "Reporting/Analytics", "ROI by content type")}
        ${arrow(880, 296, 880, 360)}
        ${arrow(670, 403, 710, 403)}
      `, "Security: OAuth 2.0 secrets in Azure Key Vault • Cost: serverless compute clusters");
    }

    if (key === "tensiometry") {
      return base(`
        ${box(50, 80, 320, 86, "Synthetic Data Generator", "Young–Laplace physics")}
        ${box(410, 80, 320, 86, "Training Dataset", "10K+ droplet shapes")}
        ${box(770, 80, 280, 86, "Neural Network", "5-layer, ~1M params")}
        ${arrow(370, 123, 410, 123)}
        ${arrow(730, 123, 770, 123)}

        ${box(50, 230, 320, 86, "Droplet Image Input", "Lab images")}
        ${box(410, 230, 320, 86, "CV Pipeline", "Contours + normalization")}
        ${box(770, 230, 280, 86, "Inference", "< 1s prediction")}
        ${arrow(370, 273, 410, 273)}
        ${arrow(730, 273, 770, 273)}

        ${box(410, 380, 640, 86, "Outputs", "Surface tension + evaluation plots")}
        ${arrow(910, 316, 910, 380)}
      `, "Accuracy: MAE 0.119, R² > 0.99 • Real-time automation for high-throughput measurement");
    }

    if (key === "fraud") {
      return base(`
        ${box(50, 80, 280, 86, "Transactions", "Events / requests")}
        ${box(360, 80, 280, 86, "Kafka Stream", "Ingestion + buffering")}
        ${box(670, 80, 380, 86, "Real-time Feature Engine", "Velocity + geo + temporal")}
        ${arrow(330, 123, 360, 123)}
        ${arrow(640, 123, 670, 123)}

        ${box(50, 230, 280, 86, "Redis Feature Cache", "Sub-ms reads")}
        ${box(360, 230, 280, 86, "XGBoost Model", "Imbalance-aware")}
        ${box(670, 230, 380, 86, "FastAPI Inference", "~4ms avg latency")}
        ${arrow(330, 273, 360, 273)}
        ${arrow(640, 273, 670, 273)}

        ${box(360, 380, 690, 86, "Monitoring + Ops", "Streamlit dashboard • drift signals • Dockerized")}
        ${arrow(860, 316, 860, 380)}
      `, "Targets: low latency, high throughput, precision-recall optimized under heavy class imbalance");
    }

    if (key === "saas") {
      return base(`
        ${box(50, 80, 320, 86, "Event Generator", "Usage • billing • support")}
        ${box(410, 80, 320, 86, "PostgreSQL Warehouse", "Dockerized infra")}
        ${box(770, 80, 280, 86, "Feature Engineering", "7/30d windows")}
        ${arrow(370, 123, 410, 123)}
        ${arrow(730, 123, 770, 123)}

        ${box(50, 230, 320, 86, "Label Generation", "Leakage-safe churn/rev")}
        ${box(410, 230, 320, 86, "Training Dataset", "300K+ rows")}
        ${box(770, 230, 280, 86, "XGBoost Training", "Imbalanced learning")}
        ${arrow(370, 273, 410, 273)}
        ${arrow(730, 273, 770, 273)}

        ${box(410, 380, 640, 86, "Outputs", "Churn risk + 90-day revenue")}
        ${arrow(910, 316, 910, 380)}
      `, "Designed to mirror real production ML pipelines end-to-end (events → warehouse → features → labels → training)");
    }

    if (key === "datamax") {
      return base(`
        ${box(50, 80, 320, 86, "Source Systems", "Pharma datasets")}
        ${box(410, 80, 320, 86, "ADF / Databricks", "ETL/ELT pipelines")}
        ${box(770, 80, 280, 86, "Warehouse", "Snowflake / Redshift")}
        ${arrow(370, 123, 410, 123)}
        ${arrow(730, 123, 770, 123)}

        ${box(50, 230, 320, 86, "Data Modeling", "Domain schemas")}
        ${box(410, 230, 320, 86, "DQ + Monitoring", "Reliability")}
        ${box(770, 230, 280, 86, "Serving", "FastAPI outputs")}
        ${arrow(370, 273, 410, 273)}
        ${arrow(730, 273, 770, 273)}

        ${box(410, 380, 640, 86, "Consumers", "Analytics + downstream teams")}
        ${arrow(910, 316, 910, 380)}
      `, "Focus: scalable warehouse modeling, pipeline performance, and data quality governance");
    }

    if (key === "perception") {
      return base(`
        ${box(50, 80, 340, 86, "Sensors", "Camera + LiDAR streams")}
        ${box(430, 80, 340, 86, "Ingestion + Sync", "Timestamp alignment")}
        ${box(810, 80, 240, 86, "Dataset Builder", "Versioning + splits")}
        ${arrow(390, 123, 430, 123)}
        ${arrow(770, 123, 810, 123)}

        ${box(50, 230, 340, 86, "Training Orchestration", "Experiments + tracking")}
        ${box(430, 230, 340, 86, "Evaluation", "Failure mode analysis")}
        ${box(810, 230, 240, 86, "Model Packaging", "Artifacts + checks")}
        ${arrow(390, 273, 430, 273)}
        ${arrow(770, 273, 810, 273)}

        ${box(430, 380, 620, 86, "Real-time Inference", "Latency SLAs • health checks • safe fallbacks")}
        ${arrow(890, 316, 890, 380)}
      `, "Edge reliability: validation gates + monitoring so only quality-checked artifacts advance");
    }

    return base(`
      ${box(50, 210, 1000, 100, "Architecture", "Diagram not available")}
    `);
  }

  // ---------------------------
  // GitHub API (live repos + caching)
  // ---------------------------
  const githubGrid = $("#githubGrid");
  const githubStatus = $("#githubStatus");
  const refreshGithubBtn = $("#refreshGithubBtn");

  const GH_USER = "sl237-lee";
  const CACHE_KEY = "gh_repos_cache_v2";
  const CACHE_TTL_MS = 1000 * 60 * 60 * 6; // 6 hours

  function loadCache() {
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.ts || !parsed.data) return null;
      if (Date.now() - parsed.ts > CACHE_TTL_MS) return null;
      return parsed.data;
    } catch {
      return null;
    }
  }

  function saveCache(data) {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data }));
    } catch {}
  }

  function langDotStyle(lang) {
    // Keep simple; still visually distinct
    const L = (lang || "").toLowerCase();
    if (!L) return "background: rgba(117,199,255,0.9)";
    if (L.includes("python")) return "background: rgba(117,199,255,0.9)";
    if (L.includes("javascript")) return "background: rgba(255,213,128,0.95)";
    if (L.includes("typescript")) return "background: rgba(138,125,255,0.95)";
    if (L.includes("html")) return "background: rgba(255,213,128,0.95)";
    if (L.includes("css")) return "background: rgba(255,213,128,0.95)";
    if (L.includes("scala")) return "background: rgba(122,240,183,0.95)";
    return "background: rgba(117,199,255,0.9)";
  }

  function renderRepos(repos, statusText) {
    if (!githubGrid) return;
    githubGrid.innerHTML = "";

    const top = repos.slice(0, 6);
    for (const r of top) {
      const a = document.createElement("a");
      a.className = "repo";
      a.href = r.html_url;
      a.target = "_blank";
      a.rel = "noopener";

      const desc = (r.description || "").trim();
      const lang = r.language || "—";
      const pushed = r.pushed_at ? timeAgo(r.pushed_at) : "";

      a.innerHTML = `
        <div class="repo-name">${escapeHtml(r.name)}</div>
        <div class="repo-desc">${escapeHtml(desc || "No description")}</div>
        <div class="repo-meta">
          <div class="repo-lang">
            <span class="dot" style="${langDotStyle(lang)}"></span>
            <span>${escapeHtml(lang)}</span>
          </div>
          <div>${escapeHtml(pushed)}</div>
        </div>
      `;
      githubGrid.appendChild(a);
    }

    if (githubStatus) githubStatus.textContent = statusText || "";
  }

  async function fetchGithub(force = false) {
    if (!githubGrid || !githubStatus) return;

    if (!force) {
      const cached = loadCache();
      if (cached && Array.isArray(cached) && cached.length) {
        renderRepos(cached, "Loaded from cache");
      } else {
        githubStatus.textContent = "Loading GitHub…";
      }
    } else {
      githubStatus.textContent = "Refreshing GitHub…";
    }

    try {
      const res = await fetch(`https://api.github.com/users/${GH_USER}/repos?per_page=100&sort=pushed`, {
        headers: { "Accept": "application/vnd.github+json" }
      });

      if (!res.ok) {
        const cached = loadCache();
        if (cached && cached.length) {
          renderRepos(cached, `GitHub limited — showing cached (HTTP ${res.status})`);
          return;
        }
        githubStatus.textContent = `GitHub unavailable (HTTP ${res.status})`;
        return;
      }

      const repos = await res.json();
      const cleaned = (Array.isArray(repos) ? repos : []).filter(r => !r.fork);

      saveCache(cleaned);
      renderRepos(cleaned, "Live from GitHub");
    } catch {
      const cached = loadCache();
      if (cached && cached.length) {
        renderRepos(cached, "Offline — showing cached");
        return;
      }
      githubStatus.textContent = "GitHub unavailable";
    }
  }

  refreshGithubBtn?.addEventListener("click", () => fetchGithub(true));
  fetchGithub(false);

    // ---------------------------
  // Hero profile card tilt
  // ---------------------------
  const heroProfileCard = $("#heroProfileCard");

  if (heroProfileCard && window.matchMedia("(prefers-reduced-motion: no-preference)").matches) {
    heroProfileCard.addEventListener("mousemove", (e) => {
      const rect = heroProfileCard.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width;
      const py = (e.clientY - rect.top) / rect.height;

      const rx = (0.5 - py) * 8;
      const ry = (px - 0.5) * 10;

      heroProfileCard.style.transform = `perspective(1200px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-2px)`;
    });

    heroProfileCard.addEventListener("mouseleave", () => {
      heroProfileCard.style.transform = "perspective(1200px) rotateX(0deg) rotateY(0deg) translateY(0px)";
    });
  }
})();