/* js/main.js — full updated deployed version
   Features:
   - Theme toggle with persistence
   - Scroll progress bar
   - Reveal-on-scroll animations
   - Hero counters
   - Project search + filters
   - Architecture modal
   - GitHub live repos + cache
*/

(() => {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => {
      switch (char) {
        case "&": return "&amp;";
        case "<": return "&lt;";
        case ">": return "&gt;";
        case '"': return "&quot;";
        case "'": return "&#39;";
        default: return char;
      }
    });
  }

  function timeAgo(isoString) {
    try {
      const date = new Date(isoString);
      const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);

      if (days > 0) return `${days}d ago`;
      if (hours > 0) return `${hours}h ago`;
      if (minutes > 0) return `${minutes}m ago`;
      return "just now";
    } catch {
      return "";
    }
  }

  /* ---------------------------
     Theme toggle
  --------------------------- */
  const root = document.documentElement;
  const themeToggle = $("#themeToggle");
  const themeIcon = $("#themeIcon");

  function getSystemTheme() {
    const media = window.matchMedia?.("(prefers-color-scheme: dark)");
    return media && media.matches ? "dark" : "light";
  }

  function getSavedTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark" || saved === "light") return saved;
    return "auto";
  }

  function syncThemeIcon(theme) {
    const effectiveTheme = theme === "auto" ? getSystemTheme() : theme;
    if (themeIcon) {
      themeIcon.textContent = effectiveTheme === "dark" ? "☾" : "☀";
    }
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    syncThemeIcon(theme);
  }

  function initTheme() {
    applyTheme(getSavedTheme());

    const media = window.matchMedia?.("(prefers-color-scheme: dark)");
    if (media && typeof media.addEventListener === "function") {
      media.addEventListener("change", () => {
        if (getSavedTheme() === "auto") {
          syncThemeIcon("auto");
        }
      });
    }
  }

  function toggleTheme() {
    const current = getSavedTheme();

    if (current === "auto") {
      const next = getSystemTheme() === "dark" ? "light" : "dark";
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

  /* ---------------------------
     Scroll progress bar
  --------------------------- */
  const scrollbarFill = $("#scrollbarFill");

  function updateScrollBar() {
    if (!scrollbarFill) return;

    const doc = document.documentElement;
    const scrollTop = doc.scrollTop || document.body.scrollTop;
    const scrollHeight = doc.scrollHeight - doc.clientHeight;
    const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
    scrollbarFill.style.width = `${progress}%`;
  }

  window.addEventListener("scroll", updateScrollBar, { passive: true });
  updateScrollBar();

  /* ---------------------------
     Toast
  --------------------------- */
  const toast = $("#toast");
  let toastTimer = null;

  function showToast(message) {
    if (!toast) return;

    toast.textContent = message || "Copied";
    toast.classList.add("show");

    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove("show");
    }, 1400);
  }

  /* ---------------------------
     Copy email
  --------------------------- */
  const copyEmailBtn = $("#copyEmailBtn");

  copyEmailBtn?.addEventListener("click", async () => {
    const email = copyEmailBtn.getAttribute("data-email") || "";
    if (!email) return;

    try {
      await navigator.clipboard.writeText(email);
      showToast("Email copied");
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = email;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      showToast("Email copied");
    }
  });

  /* ---------------------------
     Back to top
  --------------------------- */
  const toTopBtn = $("#toTopBtn");
  toTopBtn?.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  /* ---------------------------
     Reveal on scroll
  --------------------------- */
  const revealElements = $$(".reveal");

  if (revealElements.length) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("in");
          revealObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.12 }
    );

    revealElements.forEach((element) => revealObserver.observe(element));
  }

  /* ---------------------------
     Hero counters
  --------------------------- */
  function animateCounter(element) {
    const target = Number(element.getAttribute("data-countup") || "0");
    const suffix = element.getAttribute("data-suffix") || "";
    const duration = 900;
    const startTime = performance.now();

    function tick(now) {
      const progress = clamp((now - startTime) / duration, 0, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = Math.round(target * eased);
      element.textContent = `${value}${suffix}`;

      if (progress < 1) {
        requestAnimationFrame(tick);
      }
    }

    requestAnimationFrame(tick);
  }

  const counterElements = $$("[data-countup]");

  if (counterElements.length) {
    const counterObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.55 }
    );

    counterElements.forEach((element) => counterObserver.observe(element));
  }

  /* ---------------------------
     Project search + filters
  --------------------------- */
  const projectGrid = $("#projectGrid");
  const projectSearch = $("#projectSearch");
  const filterButtons = $$(".chip-btn");

  function getActiveFilter() {
    const active = filterButtons.find((button) => button.classList.contains("active"));
    return active ? (active.getAttribute("data-filter") || "all") : "all";
  }

  function cardMatchesFilter(card, filter) {
    if (filter === "all") return true;
    const tags = (card.getAttribute("data-tags") || "").toLowerCase();
    return tags.includes(filter.toLowerCase());
  }

  function cardMatchesSearch(card, query) {
    if (!query) return true;

    const haystack = [
      card.getAttribute("data-title") || "",
      card.getAttribute("data-tags") || "",
      card.textContent || ""
    ].join(" ").toLowerCase();

    return haystack.includes(query);
  }

  function applyProjectFilters() {
    if (!projectGrid) return;

    const query = (projectSearch?.value || "").trim().toLowerCase();
    const filter = getActiveFilter();
    const cards = $$(".card", projectGrid);

    let visibleCount = 0;

    cards.forEach((card) => {
      const visible = cardMatchesFilter(card, filter) && cardMatchesSearch(card, query);
      card.classList.toggle("is-hidden", !visible);
      if (visible) visibleCount += 1;
    });

    if (projectSearch) {
      projectSearch.setAttribute("aria-label", `Search projects. ${visibleCount} shown.`);
    }
  }

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      filterButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      applyProjectFilters();
    });
  });

  projectSearch?.addEventListener("input", applyProjectFilters);
  applyProjectFilters();

  /* ---------------------------
     Architecture modal
  --------------------------- */
  const archModal = $("#archModal");
  const archModalTitle = $("#archModalTitle");
  const archDiagram = $("#archDiagram");
  const archModalClose = $("#archModalClose");

  function openArchModal(title, key) {
    if (!archModal || !archModalTitle || !archDiagram) return;

    archModalTitle.textContent = title || "Architecture";
    archDiagram.innerHTML = buildArchitectureSvg(key || "default");

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

  archModal?.addEventListener("click", (event) => {
    const target = event.target;
    if (target && target.getAttribute && target.getAttribute("data-close") === "true") {
      closeArchModal();
    }
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeArchModal();
    }
  });

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("button[data-arch]");
    if (!trigger) return;

    const key = trigger.getAttribute("data-arch") || "default";
    const title = trigger.getAttribute("data-modal-title") || "Architecture";
    openArchModal(title, key);
  });

  function buildArchitectureSvg(key) {
    const wrap = (content, caption = "") => `
      <svg viewBox="0 0 1100 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Architecture diagram">
        <defs>
          <linearGradient id="archLine" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#75c7ff"/>
            <stop offset="100%" stop-color="#8a7dff"/>
          </linearGradient>
          <filter id="archGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="3" result="blur"></feGaussianBlur>
            <feMerge>
              <feMergeNode in="blur"></feMergeNode>
              <feMergeNode in="SourceGraphic"></feMergeNode>
            </feMerge>
          </filter>
        </defs>
        <rect x="0" y="0" width="1100" height="540" fill="transparent"></rect>
        ${content}
        ${
          caption
            ? `<text x="48" y="518" fill="rgba(234,242,251,0.70)" font-size="12">${escapeHtml(caption)}</text>`
            : ""
        }
      </svg>
    `;

    const box = (x, y, w, h, title, subtitle = "") => `
      <g>
        <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="16" ry="16"
          fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.12)"></rect>
        <text x="${x + 16}" y="${y + 30}" fill="currentColor" font-size="13" font-weight="900">
          ${escapeHtml(title)}
        </text>
        ${
          subtitle
            ? `<text x="${x + 16}" y="${y + 52}" fill="rgba(234,242,251,0.65)" font-size="12">${escapeHtml(subtitle)}</text>`
            : ""
        }
      </g>
    `;

    const line = (x1, y1, x2, y2) => `
      <g filter="url(#archGlow)">
        <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="url(#archLine)" stroke-width="2"></line>
        <circle cx="${x2}" cy="${y2}" r="3.5" fill="#75c7ff"></circle>
      </g>
    `;

    switch (key) {
      case "social":
        return wrap(`
          ${box(50, 70, 290, 86, "YouTube Reporting/Analytics API", "Platform metrics")}
          ${box(380, 70, 290, 86, "Ingestion Jobs", "Connectors + retries")}
          ${box(710, 70, 340, 86, "Delta Lake (Bronze/Silver)", "ACID + schema evolution")}
          ${line(340, 113, 380, 113)}
          ${line(670, 113, 710, 113)}

          ${box(50, 210, 290, 86, "Enterprise Clickstream", "High-volume behavior data")}
          ${box(380, 210, 290, 86, "PySpark Transforms", "Joins + attribution logic")}
          ${box(710, 210, 340, 86, "DQ Validation", "Schema + null checks")}
          ${line(340, 253, 380, 253)}
          ${line(670, 253, 710, 253)}

          ${box(380, 360, 290, 86, "Serving Tables", "Curated ROI datasets")}
          ${box(710, 360, 340, 86, "Campaign Analytics", "Influencer + Native ROI")}
          ${line(880, 296, 880, 360)}
          ${line(670, 403, 710, 403)}
        `, "Serverless Databricks ELT with OAuth 2.0, idempotent upserts, and marketing ROI analytics.");

      case "tensiometry":
        return wrap(`
          ${box(50, 80, 320, 86, "Synthetic Data Generator", "Young–Laplace equations")}
          ${box(410, 80, 320, 86, "Training Dataset", "10K+ droplet shapes")}
          ${box(770, 80, 280, 86, "Deep Neural Network", "5 layers, ~1M params")}
          ${line(370, 123, 410, 123)}
          ${line(730, 123, 770, 123)}

          ${box(50, 230, 320, 86, "Droplet Image Input", "Real image samples")}
          ${box(410, 230, 320, 86, "CV Pipeline", "Contours + preprocessing")}
          ${box(770, 230, 280, 86, "Inference", "<1s prediction")}
          ${line(370, 273, 410, 273)}
          ${line(730, 273, 770, 273)}

          ${box(410, 380, 640, 86, "Outputs", "Surface tension prediction + research evaluation")}
          ${line(910, 316, 910, 380)}
        `, "Physics-informed ML pipeline for rapid, automated surface tension estimation.");

      case "fraud":
        return wrap(`
          ${box(50, 80, 280, 86, "Transaction Stream", "Incoming events")}
          ${box(360, 80, 280, 86, "Kafka", "Streaming ingestion")}
          ${box(670, 80, 380, 86, "Feature Engineering", "Velocity + geo + temporal")}
          ${line(330, 123, 360, 123)}
          ${line(640, 123, 670, 123)}

          ${box(50, 230, 280, 86, "Redis Cache", "Low-latency features")}
          ${box(360, 230, 280, 86, "XGBoost Model", "Imbalance-aware training")}
          ${box(670, 230, 380, 86, "FastAPI Inference", "~4ms average latency")}
          ${line(330, 273, 360, 273)}
          ${line(640, 273, 670, 273)}

          ${box(360, 380, 690, 86, "Monitoring", "Dashboard, drift checks, Dockerized ops")}
          ${line(860, 316, 860, 380)}
        `, "Streaming fraud detection system optimized for low latency, reliability, and monitoring.");

      case "saas":
        return wrap(`
          ${box(50, 80, 320, 86, "Event Generator", "Usage, billing, support")}
          ${box(410, 80, 320, 86, "PostgreSQL Warehouse", "Dockerized storage")}
          ${box(770, 80, 280, 86, "Feature Layer", "7/30-day aggregates")}
          ${line(370, 123, 410, 123)}
          ${line(730, 123, 770, 123)}

          ${box(50, 230, 320, 86, "Label Generation", "Leakage-safe churn/revenue")}
          ${box(410, 230, 320, 86, "Training Dataset", "300K+ observations")}
          ${box(770, 230, 280, 86, "XGBoost Training", "Highly imbalanced learning")}
          ${line(370, 273, 410, 273)}
          ${line(730, 273, 770, 273)}

          ${box(410, 380, 640, 86, "Outputs", "Churn risk + 90-day revenue forecast")}
          ${line(910, 316, 910, 380)}
        `, "End-to-end ML platform mirroring production SaaS analytics and churn modeling workflows.");

      case "datamax":
        return wrap(`
          ${box(50, 80, 320, 86, "Enterprise Data Sources", "Pharma domains")}
          ${box(410, 80, 320, 86, "ADF / Databricks", "ETL/ELT pipelines")}
          ${box(770, 80, 280, 86, "Warehouse", "Snowflake / Redshift")}
          ${line(370, 123, 410, 123)}
          ${line(730, 123, 770, 123)}

          ${box(50, 230, 320, 86, "Data Models", "Scalable domain schemas")}
          ${box(410, 230, 320, 86, "DQ + Monitoring", "Validation framework")}
          ${box(770, 230, 280, 86, "Serving APIs", "FastAPI endpoints")}
          ${line(370, 273, 410, 273)}
          ${line(730, 273, 770, 273)}

          ${box(410, 380, 640, 86, "Consumers", "Analytics + business stakeholders")}
          ${line(910, 316, 910, 380)}
        `, "Cloud DWBI platform with large-scale modeling, pipeline engineering, and governance.");

      case "perception":
        return wrap(`
          ${box(50, 80, 340, 86, "Camera + LiDAR", "Multimodal sensor feeds")}
          ${box(430, 80, 340, 86, "Ingestion + Sync", "Timestamp alignment")}
          ${box(810, 80, 240, 86, "Dataset Builder", "Versioning + splits")}
          ${line(390, 123, 430, 123)}
          ${line(770, 123, 810, 123)}

          ${box(50, 230, 340, 86, "Training Orchestration", "Experiment workflows")}
          ${box(430, 230, 340, 86, "Evaluation", "Failure analysis")}
          ${box(810, 230, 240, 86, "Model Packaging", "Artifacts + checks")}
          ${line(390, 273, 430, 273)}
          ${line(770, 273, 810, 273)}

          ${box(430, 380, 620, 86, "Inference Runtime", "Latency SLAs + safe fallbacks")}
          ${line(890, 316, 890, 380)}
        `, "Perception data platform for synchronized multimodal training and reliable inference.");

      default:
        return wrap(`
          ${box(50, 210, 1000, 100, "Architecture", "Diagram not available")}
        `);
    }
  }

  /* ---------------------------
     GitHub repos with cache
  --------------------------- */
  const githubGrid = $("#githubGrid");
  const githubStatus = $("#githubStatus");
  const refreshGithubBtn = $("#refreshGithubBtn");

  const GITHUB_USER = "sl237-lee";
  const CACHE_KEY = "portfolio_github_cache_v3";
  const CACHE_TTL_MS = 1000 * 60 * 60 * 6;

  function loadGithubCache() {
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return null;

      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.timestamp || !Array.isArray(parsed.data)) return null;
      if (Date.now() - parsed.timestamp > CACHE_TTL_MS) return null;

      return parsed.data;
    } catch {
      return null;
    }
  }

  function saveGithubCache(data) {
    try {
      localStorage.setItem(
        CACHE_KEY,
        JSON.stringify({
          timestamp: Date.now(),
          data
        })
      );
    } catch {
      // ignore storage errors
    }
  }

  function languageDotStyle(language) {
    const lang = String(language || "").toLowerCase();

    if (lang.includes("python")) return "background:#4da3ff";
    if (lang.includes("javascript")) return "background:#ffd166";
    if (lang.includes("typescript")) return "background:#8a7dff";
    if (lang.includes("html")) return "background:#f4b860";
    if (lang.includes("css")) return "background:#7af0b7";
    if (lang.includes("scala")) return "background:#ff7a7a";
    if (lang.includes("jupyter")) return "background:#f08c3a";

    return "background:#75c7ff";
  }

  function renderRepos(repos, statusText) {
    if (!githubGrid) return;

    githubGrid.innerHTML = "";

    const visibleRepos = repos.slice(0, 4);

    visibleRepos.forEach((repo) => {
      const card = document.createElement("a");
      card.className = "repo";
      card.href = repo.html_url;
      card.target = "_blank";
      card.rel = "noopener";

      const language = repo.language || "Unknown";
      const pushed = repo.pushed_at ? timeAgo(repo.pushed_at) : "";
      const description = (repo.description || "").trim() || "No description";

      card.innerHTML = `
        <div class="repo-name">${escapeHtml(repo.name)}</div>
        <div class="repo-desc">${escapeHtml(description)}</div>
        <div class="repo-meta">
          <div class="repo-lang">
            <span class="dot" style="${languageDotStyle(language)}"></span>
            <span>${escapeHtml(language)}</span>
          </div>
          <div>${escapeHtml(pushed)}</div>
        </div>
      `;

      githubGrid.appendChild(card);
    });

    if (githubStatus) {
      githubStatus.textContent = statusText || "";
    }
  }

  async function fetchGithub(forceRefresh = false) {
    if (!githubGrid || !githubStatus) return;

    if (!forceRefresh) {
      const cached = loadGithubCache();
      if (cached && cached.length) {
        renderRepos(cached, "Loaded from cache");
      } else {
        githubStatus.textContent = "Loading GitHub…";
      }
    } else {
      githubStatus.textContent = "Refreshing GitHub…";
    }

    try {
      const response = await fetch(
        `https://api.github.com/users/${GITHUB_USER}/repos?per_page=100&sort=pushed`,
        {
          headers: {
            "Accept": "application/vnd.github+json"
          }
        }
      );

      if (!response.ok) {
        const cached = loadGithubCache();
        if (cached && cached.length) {
          renderRepos(cached, `GitHub limited — showing cached (HTTP ${response.status})`);
          return;
        }

        githubStatus.textContent = `GitHub unavailable (HTTP ${response.status})`;
        return;
      }

      const repos = await response.json();
      const cleaned = (Array.isArray(repos) ? repos : []).filter((repo) => !repo.fork);

      saveGithubCache(cleaned);
      renderRepos(cleaned, "Live from GitHub");
    } catch {
      const cached = loadGithubCache();
      if (cached && cached.length) {
        renderRepos(cached, "Offline — showing cached");
        return;
      }

      githubStatus.textContent = "GitHub unavailable";
    }
  }

  refreshGithubBtn?.addEventListener("click", () => fetchGithub(true));
  fetchGithub(false);
})();