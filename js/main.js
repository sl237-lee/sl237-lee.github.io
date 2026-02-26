// js/main.js
(() => {
    const root = document.documentElement;
  
    // Reveal on scroll
    const observer = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) e.target.classList.add("is-visible");
      }
    }, { threshold: 0.12 });
  
    document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
  
    // Theme toggle (auto/light/dark)
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const prefersDarkMQ = window.matchMedia("(prefers-color-scheme: dark)");
  
    function getSystemTheme() {
      return prefersDarkMQ.matches ? "dark" : "light";
    }
  
    function applyTheme(mode) {
      if (mode === "auto") {
        const sys = getSystemTheme();
        root.setAttribute("data-theme", sys);
        if (themeIcon) themeIcon.textContent = sys === "dark" ? "🌙" : "🌞";
      } else {
        root.setAttribute("data-theme", mode);
        if (themeIcon) themeIcon.textContent = mode === "dark" ? "🌙" : "🌞";
      }
    }
  
    let mode = localStorage.getItem("theme") || "auto";
    applyTheme(mode);
  
    prefersDarkMQ.addEventListener?.("change", () => {
      if ((localStorage.getItem("theme") || "auto") === "auto") applyTheme("auto");
    });
  
    themeToggle?.addEventListener("click", () => {
      mode = mode === "auto" ? "light" : mode === "light" ? "dark" : "auto";
      localStorage.setItem("theme", mode);
      applyTheme(mode);
      toast(`Theme: ${mode}`);
    });
  
    // Toast
    const toastEl = document.getElementById("toast");
    let toastTimer;
  
    function toast(message) {
      if (!toastEl) return;
      toastEl.textContent = message;
      toastEl.classList.add("show");
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toastEl.classList.remove("show"), 1500);
    }
  
    // Copy email
    const email = "srlee02099@gmail.com";
    const copyBtn = document.getElementById("copyEmailBtn");
    const emailLink = document.getElementById("emailLink");
  
    async function copyText(text) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch {
        return false;
      }
    }
  
    copyBtn?.addEventListener("click", async () => {
      const ok = await copyText(email);
      if (ok) toast(`Copied: ${email}`);
      else window.location.href = `mailto:${email}`;
    });
  
    emailLink?.addEventListener("click", async (e) => {
      e.preventDefault();
      const ok = await copyText(email);
      if (ok) toast(`Copied: ${email}`);
      else window.location.href = `mailto:${email}`;
    });
  
    // Back to top
    const toTopBtn = document.getElementById("toTopBtn");
    toTopBtn?.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  })();