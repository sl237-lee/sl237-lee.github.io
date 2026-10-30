(() => {
  'use strict';
  const root = document.documentElement;
  const themeButton = document.querySelector('#theme-toggle');
  function syncTheme() {
    const dark = root.dataset.theme !== 'light';
    themeButton.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
    document.querySelector('#theme-label').textContent = dark ? 'Light' : 'Dark';
  }
  if (!['dark', 'light'].includes(root.dataset.theme)) root.dataset.theme = 'dark';
  syncTheme();
  themeButton.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('portfolio-theme', root.dataset.theme); } catch {}
    syncTheme();
  });
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const cards = [...document.querySelectorAll('[data-category]')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  filters.forEach(button => button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    filters.forEach(item => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    let count = 0;
    cards.forEach(card => {
      card.classList.remove('filter-enter');
      card.hidden = filter !== 'all' && !(filter === 'AI' ? ['AI tooling', 'Analytics & ML'].includes(card.dataset.category) : card.dataset.category === filter);
      if (!card.hidden) {
        card.style.setProperty('--card-delay', `${count * 55}ms`);
        count++;
      }
    });
    if (!reduceMotion.matches) requestAnimationFrame(() => cards.filter(c => !c.hidden).forEach(c => c.classList.add('filter-enter')));
    document.querySelector('#project-count').textContent = `${count} project${count === 1 ? '' : 's'}`;
  }));
  if ('IntersectionObserver' in window) {
    const reveal = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('in-view'); reveal.unobserve(entry.target); }
    }), {threshold: 0.06});
    document.querySelectorAll('.section-heading, .role, .project, .expertise-grid article, .pillar, .work-case, .engineering-principles, .credentials, .contact-inner').forEach(el => {
      el.classList.add('reveal'); reveal.observe(el);
    });
    root.classList.add('motion-ready');
    window.addEventListener('pageshow', () => {
      document.querySelectorAll('.reveal').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.bottom > 0 && rect.top < innerHeight) el.classList.add('in-view');
      });
    });
    const navLinks = [...document.querySelectorAll('nav a[href^="#"]')];
    const sections = [...navLinks.map(a => document.querySelector(a.getAttribute('href'))), document.querySelector("#top")].filter(Boolean);
    const active = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) navLinks.forEach(link => {
        if (link.getAttribute('href') === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }), {rootMargin: '-15% 0px -55% 0px'});
    sections.forEach(section => active.observe(section));
  }
  let scheduled = false;
  function updateProgress() {
    const range = root.scrollHeight - window.innerHeight;
    root.style.setProperty('--progress', range > 0 ? Math.min(1, Math.max(0, window.scrollY / range)) : 0);
    scheduled = false;
  }
  window.addEventListener('scroll', () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(updateProgress); }
  }, {passive:true});
  window.addEventListener('resize', updateProgress);
  updateProgress();
  document.addEventListener('click', e => {
    if (reduceMotion.matches || e.detail === 0 || !e.target.closest('button, .button')) return;
    const ring = document.createElement('span'); ring.className = 'click-ring';
    ring.style.left = `${e.clientX - 6}px`; ring.style.top = `${e.clientY - 6}px`;
    ring.setAttribute('aria-hidden', 'true'); document.body.append(ring);
    ring.addEventListener('animationend', () => ring.remove(), {once:true});
  });
  document.querySelector('#copy-email').addEventListener('click', async () => {
    const status = document.querySelector('#copy-status');
    try { await navigator.clipboard.writeText('srlee02099@gmail.com'); status.textContent = 'Email copied'; }
    catch { status.textContent = 'Copy: srlee02099@gmail.com'; }
  });
  document.querySelector('#year').textContent = new Date().getFullYear();
})();
