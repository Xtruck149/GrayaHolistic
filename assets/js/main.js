document.addEventListener('DOMContentLoaded', () => {

  /* ---- Delivery zone & lead-time checker (index.html + services.html) ----
     Placeholder figures — adjust to real logistics before launch.
     The kitchen is based in Bingerville, so times/minimums scale with
     actual distance from there, not from a generic Abidjan center. */
  const DELIVERY_ZONES = {
    bingerville:{ label: 'Bingerville', time: '15–20 min', cutoff: '21h30', min: '2 000 FCFA' },
    riviera:    { label: 'Riviera',     time: '20–30 min', cutoff: '21h00', min: '3 000 FCFA' },
    cocody:     { label: 'Cocody',      time: '30–40 min', cutoff: '21h00', min: '4 000 FCFA' },
    plateau:    { label: 'Plateau',     time: '35–50 min', cutoff: '20h30', min: '5 000 FCFA' },
    marcory:    { label: 'Marcory',     time: '40–55 min', cutoff: '20h30', min: '6 000 FCFA' },
    treichville:{ label: 'Treichville', time: '40–55 min', cutoff: '20h30', min: '6 000 FCFA' },
    zone4:      { label: 'Zone 4',      time: '40–55 min', cutoff: '20h30', min: '6 000 FCFA' },
    bassam:     { label: 'Grand-Bassam',time: '45–65 min', cutoff: '20h00', min: '6 000 FCFA' },
    yopougon:   { label: 'Yopougon',    time: '60–90 min', cutoff: '19h30', min: '8 000 FCFA' }
  };
  document.querySelectorAll('.delivery-checker').forEach(widget => {
    const select = widget.querySelector('.delivery-zone-select');
    const result = widget.querySelector('.delivery-result');
    const emptyMsg = widget.querySelector('.delivery-empty');
    if (!select || !result) return;
    select.addEventListener('change', () => {
      const zone = DELIVERY_ZONES[select.value];
      if (!zone) {
        result.hidden = true;
        if (emptyMsg) emptyMsg.hidden = false;
        return;
      }
      if (emptyMsg) emptyMsg.hidden = true;
      result.querySelector('.js-delivery-time').textContent = zone.time;
      result.querySelector('.js-delivery-cutoff').textContent = zone.cutoff;
      result.querySelector('.js-delivery-min').textContent = zone.min;
      const cta = result.querySelector('.js-delivery-cta');
      if (cta) {
        cta.href = 'https://wa.me/2250101736812?text=' + encodeURIComponent(
          `Bonjour Graya Holistic, je suis à ${zone.label} et je souhaite passer une commande.`
        );
      }
      result.hidden = false;
    });
  });

  /* ---- Order builder: "+ Ajouter" on priced menu rows -> WhatsApp cart (menu.html) ---- */
  (() => {
    const priceRows = Array.from(document.querySelectorAll('.menu-row')).filter(row => row.querySelector('.menu-price'));
    if (!priceRows.length) return;

    let cart = [];
    try { cart = JSON.parse(localStorage.getItem('graya-cart') || '[]'); } catch (e) { cart = []; }

    const bar = document.createElement('div');
    bar.className = 'cart-bar';
    bar.hidden = true;
    bar.innerHTML = `
      <span class="cart-bar-summary"><span id="cart-count">0</span> article(s) — <span id="cart-total">0</span> FCFA</span>
      <button type="button" class="btn btn-primary btn-sm" id="cart-open-btn">Voir ma commande</button>
    `;
    document.body.appendChild(bar);

    const modal = document.createElement('div');
    modal.className = 'cart-modal';
    modal.innerHTML = `
      <div class="cart-modal-inner">
        <button type="button" class="cart-modal-close" aria-label="Fermer">&times;</button>
        <h3>Votre commande</h3>
        <div class="cart-items" id="cart-items"></div>
        <div class="cart-total-row">Total : <strong id="cart-modal-total">0 FCFA</strong></div>
        <div class="form-field">
          <label for="cart-date">Date de livraison souhaitée</label>
          <input type="date" id="cart-date">
        </div>
        <div class="form-field">
          <label for="cart-time">Créneau horaire</label>
          <select id="cart-time">
            <option value="Dès que possible">Dès que possible</option>
            <option value="12h - 14h">12h – 14h</option>
            <option value="19h - 21h">19h – 21h</option>
          </select>
        </div>
        <a href="#" class="btn btn-primary" id="cart-send-btn" target="_blank" rel="noopener">Envoyer la commande via WhatsApp</a>
      </div>
    `;
    document.body.appendChild(modal);

    const countEl = bar.querySelector('#cart-count');
    const totalEl = bar.querySelector('#cart-total');
    const itemsEl = modal.querySelector('#cart-items');
    const modalTotalEl = modal.querySelector('#cart-modal-total');
    const sendBtn = modal.querySelector('#cart-send-btn');

    function save() { localStorage.setItem('graya-cart', JSON.stringify(cart)); }
    function total() { return cart.reduce((sum, i) => sum + i.price * i.qty, 0); }
    function fmt(n) { return n.toLocaleString('fr-FR'); }

    function render() {
      const count = cart.reduce((sum, i) => sum + i.qty, 0);
      countEl.textContent = count;
      totalEl.textContent = fmt(total());
      bar.hidden = count === 0;

      itemsEl.innerHTML = cart.map((item, i) => `
        <div class="cart-item">
          <span class="cart-item-name">${item.name}</span>
          <div class="cart-item-qty">
            <button type="button" class="cart-qty-btn" data-action="dec" data-i="${i}" aria-label="Retirer un">−</button>
            <span>${item.qty}</span>
            <button type="button" class="cart-qty-btn" data-action="inc" data-i="${i}" aria-label="Ajouter un">+</button>
          </div>
          <span class="cart-item-price">${fmt(item.price * item.qty)} FCFA</span>
        </div>
      `).join('') || '<p class="text-muted">Votre commande est vide.</p>';
      modalTotalEl.textContent = fmt(total()) + ' FCFA';
      save();
    }

    priceRows.forEach(row => {
      const h4 = row.querySelector('h4');
      const priceEl = row.querySelector('.menu-price');
      if (!h4 || !priceEl) return;
      const name = h4.childNodes[0] ? h4.childNodes[0].textContent.trim() : h4.textContent.trim();
      const price = parseInt(priceEl.textContent.replace(/[^\d]/g, ''), 10);
      if (!name || !price) return;

      const addBtn = document.createElement('button');
      addBtn.type = 'button';
      addBtn.className = 'menu-add-btn';
      addBtn.setAttribute('aria-label', 'Ajouter ' + name + ' à la commande');
      addBtn.textContent = '+ Ajouter';
      addBtn.addEventListener('click', () => {
        const existing = cart.find(i => i.name === name);
        if (existing) existing.qty++; else cart.push({ name, price, qty: 1 });
        render();
        addBtn.textContent = 'Ajouté ✓';
        setTimeout(() => { addBtn.textContent = '+ Ajouter'; }, 1200);
      });
      const actions = document.createElement('div');
      actions.className = 'menu-row-actions';
      row.insertBefore(actions, priceEl);
      actions.appendChild(priceEl);
      actions.appendChild(addBtn);
    });

    modal.querySelectorAll('.cart-qty-btn, .cart-item').length; // no-op, delegate below
    itemsEl.addEventListener('click', e => {
      const btn = e.target.closest('.cart-qty-btn');
      if (!btn) return;
      const i = parseInt(btn.dataset.i, 10);
      if (btn.dataset.action === 'inc') cart[i].qty++;
      else { cart[i].qty--; if (cart[i].qty <= 0) cart.splice(i, 1); }
      render();
    });

    function openModal() { modal.classList.add('open'); document.body.style.overflow = 'hidden'; }
    function closeModal() { modal.classList.remove('open'); document.body.style.overflow = ''; }
    bar.querySelector('#cart-open-btn').addEventListener('click', openModal);
    modal.querySelector('.cart-modal-close').addEventListener('click', closeModal);
    modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });

    sendBtn.addEventListener('click', e => {
      e.preventDefault();
      if (!cart.length) return;
      const date = modal.querySelector('#cart-date').value;
      const time = modal.querySelector('#cart-time').value;
      const lines = [
        'Bonjour Graya Holistic, je souhaite commander :',
        ...cart.map(i => `• ${i.qty} × ${i.name} — ${fmt(i.price * i.qty)} FCFA`),
        `Total : ${fmt(total())} FCFA`,
        date ? `Date souhaitée : ${date}` : '',
        `Créneau : ${time}`
      ].filter(Boolean).join('\n');
      window.open('https://wa.me/2250101736812?text=' + encodeURIComponent(lines), '_blank', 'noopener');
      cart = [];
      render();
      closeModal();
    });

    render();
  })();

  /* ---- Interactive wallpaper: ambient mesh nudged by pointer/touch + scroll ---- */
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const root = document.documentElement;
    let rafId = null, latestX = null, latestY = null;
    const applyMeshOffset = () => {
      rafId = null;
      if (latestX === null) return;
      const nx = (latestX / window.innerWidth - 0.5) * 2;
      const ny = (latestY / window.innerHeight - 0.5) * 2;
      const scrollPull = Math.min(window.scrollY / 30, 24);
      root.style.setProperty('--mesh-px', (nx * 16).toFixed(1));
      root.style.setProperty('--mesh-py', (ny * 10 + scrollPull).toFixed(1));
    };
    const queueMeshUpdate = (x, y) => {
      latestX = x; latestY = y;
      if (rafId === null) rafId = requestAnimationFrame(applyMeshOffset);
    };
    window.addEventListener('pointermove', e => queueMeshUpdate(e.clientX, e.clientY), { passive: true });
    window.addEventListener('scroll', () => {
      if (latestX === null) { latestX = window.innerWidth / 2; latestY = window.innerHeight / 2; }
      if (rafId === null) rafId = requestAnimationFrame(applyMeshOffset);
    }, { passive: true });
  }

  /* ---- Mobile navigation ---- */
  const burger = document.querySelector('.burger');
  const navLinks = document.querySelector('.nav-links');
  const overlay = document.querySelector('.nav-mobile-overlay');

  function closeNav() {
    if (navLinks) navLinks.classList.remove('open');
    if (burger) burger.setAttribute('aria-expanded', 'false');
    if (overlay) overlay.classList.remove('visible');
    document.body.style.overflow = '';
  }
  function openNav() {
    if (navLinks) navLinks.classList.add('open');
    if (burger) burger.setAttribute('aria-expanded', 'true');
    if (overlay) overlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
  }

  if (burger) {
    burger.addEventListener('click', () => {
      const isOpen = navLinks && navLinks.classList.contains('open');
      isOpen ? closeNav() : openNav();
    });
  }
  if (overlay) overlay.addEventListener('click', closeNav);
  if (navLinks) {
    navLinks.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNav));
  }

  /* ---- Header scroll state ---- */
  const header = document.querySelector('.site-header');
  if (header) {
    const onHeaderScroll = () => {
      header.classList.toggle('scrolled', window.scrollY > 20);
    };
    window.addEventListener('scroll', onHeaderScroll, { passive: true });
    onHeaderScroll();
  }

  /* ---- Scroll progress bar ---- */
  const progress = document.createElement('div');
  progress.className = 'scroll-progress';
  document.body.appendChild(progress);

  /* ---- Back to top button ---- */
  const toTop = document.createElement('button');
  toTop.className = 'to-top';
  toTop.setAttribute('aria-label', 'Retour en haut');
  toTop.innerHTML = '&#8593;';
  toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  document.body.appendChild(toTop);

  /* ---- Persistent floating WhatsApp button ---- */
  const waFab = document.createElement('a');
  waFab.className = 'whatsapp-fab';
  waFab.href = 'https://wa.me/2250101736812?text=' + encodeURIComponent("Bonjour Graya Holistic, j'ai une question.");
  waFab.target = '_blank';
  waFab.rel = 'noopener';
  waFab.setAttribute('aria-label', 'Écrire sur WhatsApp');
  waFab.innerHTML = '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.39 1.26 4.81L2 22l5.41-1.42a9.87 9.87 0 0 0 4.63 1.18h.01c5.46 0 9.9-4.45 9.9-9.91C21.95 6.45 17.5 2 12.04 2zm5.78 14.03c-.24.68-1.4 1.3-1.93 1.38-.5.08-1.12.11-1.81-.11-.42-.13-.96-.31-1.65-.61-2.9-1.25-4.79-4.17-4.94-4.36-.14-.19-1.18-1.57-1.18-3 0-1.42.75-2.12 1.02-2.41.26-.29.57-.36.76-.36.19 0 .38 0 .55.01.18.01.41-.07.64.49.24.58.81 2 .88 2.14.07.14.11.31.02.5-.09.19-.14.31-.27.48-.14.17-.29.37-.41.5-.14.14-.28.29-.12.57.16.28.71 1.17 1.52 1.9 1.05.94 1.93 1.23 2.21 1.37.28.14.44.12.6-.07.16-.19.68-.79.86-1.06.18-.27.36-.22.6-.13.24.09 1.53.72 1.79.85.26.13.43.19.5.3.07.11.07.62-.17 1.3z"/></svg>';
  document.body.appendChild(waFab);

  const onScroll = () => {
    const h = document.documentElement;
    const pct = (h.scrollTop) / (h.scrollHeight - h.clientHeight) * 100;
    progress.style.width = pct + '%';
    toTop.classList.toggle('visible', h.scrollTop > 600);
    waFab.classList.toggle('visible', h.scrollTop > 300);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- Smooth scroll for anchor links ---- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const id = this.getAttribute('href');
      if (!id || id.length < 2) return;
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        const headerH = header ? header.offsetHeight : 0;
        const top = target.getBoundingClientRect().top + window.pageYOffset - headerH - 20;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* ---- Hero photo rotator (homepage split hero) ---- */
  const heroRotator = document.querySelector('[data-hero-rotator]');
  if (heroRotator) {
    const rotatorImg = document.getElementById('hero-rotator-img');
    const rotatorSource = heroRotator.querySelector('source');
    const rotatorCaption = document.getElementById('hero-rotator-caption');
    fetch('assets/img/gallery/manifest.json')
      .then(r => r.ok ? r.json() : [])
      .then(photos => {
        if (!Array.isArray(photos) || photos.length < 2) return;
        const shuffled = photos.slice().sort(() => Math.random() - 0.5).slice(0, 8);
        let idx = 0;
        const show = i => {
          const p = shuffled[i];
          rotatorImg.classList.add('fading');
          rotatorCaption.classList.remove('visible');
          setTimeout(() => {
            if (rotatorSource) rotatorSource.srcset = 'assets/img/gallery/' + p.file + '.webp';
            rotatorImg.src = 'assets/img/gallery/' + p.file + '.jpg';
            rotatorImg.alt = p.alt || '';
            rotatorCaption.textContent = p.caption || '';
            rotatorImg.classList.remove('fading');
            rotatorCaption.classList.add('visible');
          }, 400);
        };
        show(idx);
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          setInterval(() => {
            idx = (idx + 1) % shuffled.length;
            show(idx);
          }, 4500);
        }
      })
      .catch(() => {});
  }

  /* ---- Hero floating orbs (also on the 404 error page) ---- */
  const hero = document.querySelector('.hero, .error-page');
  if (hero && !hero.querySelector('.hero-orb')) {
    ['o1', 'o2', 'o3'].forEach(cls => {
      const orb = document.createElement('span');
      orb.className = 'hero-orb ' + cls;
      hero.appendChild(orb);
    });
  }

  /* ---- Scroll-down hint under a tall hero ---- */
  if (hero && hero.classList.contains('hero--tall')) {
    const scrollHint = document.createElement('button');
    scrollHint.type = 'button';
    scrollHint.className = 'scroll-hint';
    scrollHint.setAttribute('aria-label', 'Défiler vers le bas');
    scrollHint.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';
    scrollHint.addEventListener('click', () => {
      const next = hero.nextElementSibling;
      if (next) next.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    hero.appendChild(scrollHint);
  }

  /* ---- Decorative bamboo stalks — hero corners, CTA bands, footer ---- */
  if (!document.getElementById('bamboo-culm-grad')) {
    const gradDefs = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    gradDefs.setAttribute('aria-hidden', 'true');
    gradDefs.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
    gradDefs.innerHTML = `
      <defs>
        <linearGradient id="bamboo-culm-grad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" style="stop-color:var(--bamboo-culm-dark)"/>
          <stop offset="38%" style="stop-color:var(--bamboo-culm)"/>
          <stop offset="68%" style="stop-color:var(--bamboo-culm)"/>
          <stop offset="100%" style="stop-color:var(--bamboo-culm-dark)"/>
        </linearGradient>
      </defs>`;
    document.body.appendChild(gradDefs);
  }
  const bambooSVG = `
    <svg viewBox="0 0 130 220" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <g class="bamboo-stalk" transform="translate(18,0)">
        <rect x="-8" y="30" width="16" height="190" rx="8"/>
        <rect x="-11" y="62" width="22" height="6" rx="3" class="bamboo-node"/>
        <rect x="-11" y="104" width="22" height="6" rx="3" class="bamboo-node"/>
        <rect x="-11" y="146" width="22" height="6" rx="3" class="bamboo-node"/>
        <rect x="-11" y="188" width="22" height="6" rx="3" class="bamboo-node"/>
      </g>
      <g class="bamboo-stalk" transform="translate(58,0) rotate(-4)">
        <rect x="-9" y="0" width="18" height="220" rx="9"/>
        <rect x="-12" y="36" width="24" height="6" rx="3" class="bamboo-node"/>
        <rect x="-12" y="82" width="24" height="6" rx="3" class="bamboo-node"/>
        <rect x="-12" y="128" width="24" height="6" rx="3" class="bamboo-node"/>
        <rect x="-12" y="174" width="24" height="6" rx="3" class="bamboo-node"/>
      </g>
      <g class="bamboo-stalk" transform="translate(78,0) rotate(2)">
        <rect x="-6" y="66" width="12" height="154" rx="6"/>
        <rect x="-9" y="90" width="18" height="5" rx="2.5" class="bamboo-node"/>
        <rect x="-9" y="126" width="18" height="5" rx="2.5" class="bamboo-node"/>
        <rect x="-9" y="162" width="18" height="5" rx="2.5" class="bamboo-node"/>
      </g>
      <g class="bamboo-stalk" transform="translate(96,0) rotate(3)">
        <rect x="-7" y="52" width="14" height="168" rx="7"/>
        <rect x="-10" y="80" width="20" height="6" rx="3" class="bamboo-node"/>
        <rect x="-10" y="120" width="20" height="6" rx="3" class="bamboo-node"/>
        <rect x="-10" y="160" width="20" height="6" rx="3" class="bamboo-node"/>
      </g>
      <g class="bamboo-leaves" transform="translate(58,34)">
        <path class="bamboo-leaf--light" d="M0,0 Q-34,-14 -54,-46 Q-20,-38 0,0 Z" transform="rotate(-18)"/>
        <path class="bamboo-vein" d="M0,0 Q-30,-24 -40,-42" transform="rotate(-18)"/>
        <path class="bamboo-leaf" d="M0,0 Q-30,-22 -34,-58 Q-6,-42 0,0 Z" transform="rotate(6)"/>
        <path class="bamboo-vein" d="M0,0 Q-20,-34 -22,-52" transform="rotate(6)"/>
        <path class="bamboo-leaf--light" d="M0,0 Q26,-16 44,-48 Q14,-38 0,0 Z" transform="rotate(14)"/>
        <path class="bamboo-vein" d="M0,0 Q22,-26 30,-44" transform="rotate(14)"/>
        <path class="bamboo-leaf" d="M0,0 Q30,-24 30,-60 Q4,-42 0,0 Z" transform="rotate(-8)"/>
        <path class="bamboo-vein" d="M0,0 Q16,-34 18,-54" transform="rotate(-8)"/>
        <path class="bamboo-leaf--light" d="M0,0 Q10,-30 6,-64 Q-8,-46 0,0 Z" transform="rotate(2)"/>
        <path class="bamboo-vein" d="M0,0 Q2,-38 -1,-58" transform="rotate(2)"/>
      </g>
      <g class="bamboo-leaves" transform="translate(18,28)">
        <path class="bamboo-leaf" d="M0,0 Q-22,-10 -36,-34 Q-12,-26 0,0 Z" transform="rotate(-20)"/>
        <path class="bamboo-vein" d="M0,0 Q-18,-18 -24,-32" transform="rotate(-20)"/>
        <path class="bamboo-leaf--light" d="M0,0 Q20,-12 30,-36 Q8,-26 0,0 Z" transform="rotate(16)"/>
        <path class="bamboo-vein" d="M0,0 Q14,-20 18,-33" transform="rotate(16)"/>
        <path class="bamboo-leaf" d="M0,0 Q-8,-24 -4,-42 Q6,-30 0,0 Z" transform="rotate(-4)"/>
        <path class="bamboo-vein" d="M0,0 Q0,-24 0,-38" transform="rotate(-4)"/>
      </g>
      <g class="bamboo-leaves" transform="translate(78,62)">
        <path class="bamboo-leaf--light" d="M0,0 Q-18,-8 -30,-28 Q-10,-22 0,0 Z" transform="rotate(-14)"/>
        <path class="bamboo-vein" d="M0,0 Q-14,-16 -19,-26" transform="rotate(-14)"/>
        <path class="bamboo-leaf" d="M0,0 Q16,-10 24,-30 Q6,-22 0,0 Z" transform="rotate(12)"/>
        <path class="bamboo-vein" d="M0,0 Q11,-17 14,-27" transform="rotate(12)"/>
      </g>
    </svg>`;

  function addBambooDeco(container, corners) {
    if (!container || container.querySelector('.bamboo-deco')) return;
    corners.forEach(pos => {
      const wrap = document.createElement('div');
      wrap.className = 'bamboo-deco bamboo-deco--' + pos;
      wrap.innerHTML = bambooSVG;
      container.appendChild(wrap);
    });
  }

  if (hero) {
    addBambooDeco(hero, hero.classList.contains('error-page') ? ['br'] : ['bl', 'tr']);
  }
  document.querySelectorAll('.cta-band').forEach(band => addBambooDeco(band, ['bl', 'br']));
  const siteFooter = document.querySelector('.site-footer');
  if (siteFooter) addBambooDeco(siteFooter, ['bl', 'tr']);

  /* ---- Pole-block accordion ---- */
  document.querySelectorAll('.pole-block-head').forEach(head => {
    head.setAttribute('role', 'button');
    head.setAttribute('aria-expanded', 'false');
    head.setAttribute('tabindex', '0');
    head.addEventListener('click', () => {
      const block = head.closest('.pole-block');
      const isOpen = block.classList.contains('is-open');
      block.classList.toggle('is-open');
      head.setAttribute('aria-expanded', String(!isOpen));
    });
    head.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); head.click(); }
    });
  });

  /* ---- Accordion (FAQ, etc.) ---- */
  document.querySelectorAll('.accordion-trigger').forEach(trigger => {
    trigger.setAttribute('aria-expanded', 'false');
    trigger.addEventListener('click', () => {
      const item = trigger.closest('.accordion-item');
      const body = item.querySelector('.accordion-body');
      const isOpen = item.classList.contains('is-open');
      item.classList.toggle('is-open');
      trigger.setAttribute('aria-expanded', String(!isOpen));
      if (!isOpen) {
        body.style.maxHeight = body.scrollHeight + 'px';
      } else {
        body.style.maxHeight = '0';
      }
    });
  });

  /* ---- Tab filtering ---- */
  document.querySelectorAll('.tabs').forEach(tabGroup => {
    const tabs = tabGroup.querySelectorAll('.tab');
    const targetSelector = tabGroup.dataset.target;
    const items = targetSelector ? document.querySelectorAll(targetSelector) : [];
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const filter = tab.dataset.filter;
        items.forEach(item => {
          if (filter === 'all' || item.dataset.category === filter) {
            item.style.display = '';
            item.style.opacity = '0';
            requestAnimationFrame(() => { item.style.opacity = '1'; });
          } else {
            item.style.display = 'none';
          }
        });
      });
    });
  });

  /* ---- Scroll reveal observer ---- */
  const autoReveal = document.querySelectorAll(
    '.pillars, .poles-list, .atouts-grid, .featured-grid, .parcours-steps, .team-grid, .partner-grid, .name-cloud, .grid-3, .grid-4, .value-cards, .stats-row, .logo-grid'
  );
  autoReveal.forEach(el => el.classList.add('reveal-stagger'));

  const soloReveal = document.querySelectorAll(
    '.section-header, .about-grid, .founder-card, .hero-quote, .accred-badge, .notice-box, .pole-block-head, .quote-block, .split-layout, .form-grid, .contact-split'
  );
  soloReveal.forEach(el => el.classList.add('reveal'));

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    document.querySelectorAll('.reveal, .reveal-stagger, .reveal-left, .reveal-right, .reveal-scale').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('.reveal, .reveal-stagger, .reveal-left, .reveal-right, .reveal-scale').forEach(el => el.classList.add('is-visible'));
  }

  /* ---- Animated counters ---- */
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const cio = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.count, 10);
          const suffix = el.dataset.suffix || '';
          const prefix = el.dataset.prefix || '';
          let current = 0;
          const step = Math.max(1, Math.floor(target / 60));
          const timer = setInterval(() => {
            current += step;
            if (current >= target) { current = target; clearInterval(timer); }
            el.textContent = prefix + current.toLocaleString() + suffix;
          }, 20);
          cio.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(el => cio.observe(el));
  }

  /* ---- Contact form: send via WhatsApp (site has no email backend) ---- */
  const contactForm = document.querySelector('.contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', e => {
      e.preventDefault();
      const name = contactForm.querySelector('#name').value.trim();
      const email = contactForm.querySelector('#email').value.trim();
      const subjectSelect = contactForm.querySelector('#subject');
      const subject = subjectSelect.options[subjectSelect.selectedIndex]?.textContent || '';
      const message = contactForm.querySelector('#message').value.trim();
      const lines = [
        'Bonjour Graya Holistic,',
        `Nom : ${name}`,
        `Email : ${email}`,
        subject ? `Sujet : ${subject}` : '',
        `Message : ${message}`
      ].filter(Boolean).join('\n');
      window.open('https://wa.me/2250101736812?text=' + encodeURIComponent(lines), '_blank', 'noopener');

      let msg = contactForm.querySelector('.form-success-msg');
      if (!msg) {
        msg = document.createElement('div');
        msg.className = 'form-success-msg';
        msg.style.cssText = 'background:rgba(61,125,85,0.12);border:1px solid rgba(61,125,85,0.35);border-radius:var(--radius-sm);padding:16px 20px;margin-bottom:20px;font-weight:600;color:var(--olive-dark);font-size:0.92rem;';
        contactForm.parentNode.insertBefore(msg, contactForm);
      }
      msg.textContent = 'Votre message est pr\u00eat sur WhatsApp \u2014 il ne reste qu\u2019\u00e0 l\u2019envoyer !';
      contactForm.reset();
    });
  }

  /* ---- Magnetic tilt on elevated cards (fine pointer + motion allowed only) ---- */
  const finePointer = window.matchMedia('(pointer: fine)').matches;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (finePointer && !reducedMotion) {
    document.querySelectorAll('.card--elevated, .formation-card, .founder-card').forEach(card => {
      card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        card.style.transform = `perspective(800px) rotateX(${(-y * 6).toFixed(2)}deg) rotateY(${(x * 8).toFixed(2)}deg) translateY(-6px)`;
      });
      card.addEventListener('mouseleave', () => { card.style.transform = ''; });
    });
  }

  /* ---- Marquee: duplicate content once so the -50% loop is seamless ---- */
  document.querySelectorAll('.marquee-track').forEach(track => {
    if (!track.dataset.doubled) {
      track.innerHTML += track.innerHTML;
      track.dataset.doubled = 'true';
    }
  });

  /* ---- Photo gallery, fed by assets/img/gallery/manifest.json ---- */
  let lightboxWired = false;
  let lightboxShow = null;
  let lightboxClose = null;
  let lightboxLastFocused = null;

  function buildLightbox() {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', 'Galerie photo');
    box.innerHTML = `
      <button class="lightbox-close" aria-label="Fermer">&times;</button>
      <button class="lightbox-prev" aria-label="Photo précédente">&#8249;</button>
      <div>
        <img src="" alt="">
        <div class="lightbox-caption"></div>
      </div>
      <button class="lightbox-next" aria-label="Photo suivante">&#8250;</button>
    `;
    document.body.appendChild(box);
    return box;
  }

  function setupGallery(grid, photos) {
    const box = document.querySelector('.lightbox') || buildLightbox();
    let current = 0;

    function show(i) {
      current = (i + photos.length) % photos.length;
      const p = photos[current];
      box.querySelector('img').src = 'assets/img/gallery/' + p.file + '.jpg';
      box.querySelector('img').alt = p.alt || '';
      box.querySelector('.lightbox-caption').textContent = p.caption || '';
    }
    function close() {
      box.classList.remove('open');
      document.body.style.overflow = '';
      if (lightboxLastFocused) { lightboxLastFocused.focus(); lightboxLastFocused = null; }
    }
    function open(i, triggerEl) {
      lightboxLastFocused = triggerEl || document.activeElement;
      show(i);
      box.classList.add('open');
      document.body.style.overflow = 'hidden';
      box.querySelector('.lightbox-close').focus();
    }

    lightboxShow = show;
    lightboxClose = close;

    if (!lightboxWired) {
      lightboxWired = true;
      box.addEventListener('click', e => { if (e.target === box) lightboxClose(); });
      box.querySelector('.lightbox-close').addEventListener('click', () => lightboxClose());
      box.querySelector('.lightbox-prev').addEventListener('click', () => lightboxShow(current - 1));
      box.querySelector('.lightbox-next').addEventListener('click', () => lightboxShow(current + 1));
      document.addEventListener('keydown', e => {
        if (!box.classList.contains('open')) return;
        if (e.key === 'Escape') { lightboxClose(); return; }
        if (e.key === 'ArrowRight') { lightboxShow(current + 1); return; }
        if (e.key === 'ArrowLeft') { lightboxShow(current - 1); return; }
        if (e.key === 'Tab') {
          const focusables = Array.from(box.querySelectorAll('button'));
          const first = focusables[0], last = focusables[focusables.length - 1];
          if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
          else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
      });
    }

    grid.querySelectorAll('.gallery-card').forEach(card => {
      if (card.dataset.wired) return;
      card.dataset.wired = '1';
      card.addEventListener('click', () => open(parseInt(card.dataset.index, 10), card));
      card.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(parseInt(card.dataset.index, 10), card); }
      });
    });
  }

  function galleryCardHTML(p, i) {
    const label = 'Agrandir la photo : ' + (p.caption || p.alt || 'photo');
    return `
      <div class="gallery-card reveal-scale" data-index="${i}" data-category="${p.category || 'autres'}" role="button" tabindex="0" aria-label="${label}">
        <div class="gallery-media">
          <picture>
            <source srcset="assets/img/gallery/${p.file}.webp" type="image/webp">
            <img src="assets/img/gallery/${p.file}.jpg" alt="${p.alt || ''}" decoding="async">
          </picture>
        </div>
        ${p.caption ? `<span class="gallery-caption">${p.caption}</span>` : ''}
      </div>
    `;
  }

  function wireGalleryReveal(container) {
    const els = container.querySelectorAll('.reveal-scale:not(.is-visible)');
    if ('IntersectionObserver' in window) {
      const galleryIo = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) { entry.target.classList.add('is-visible'); galleryIo.unobserve(entry.target); }
        });
      }, { threshold: 0.1 });
      els.forEach(el => galleryIo.observe(el));
    } else {
      els.forEach(el => el.classList.add('is-visible'));
    }
  }

  document.querySelectorAll('[data-gallery]').forEach(grid => {
    fetch('assets/img/gallery/manifest.json')
      .then(r => r.ok ? r.json() : [])
      .then(photos => {
        if (!Array.isArray(photos) || !photos.length) {
          grid.innerHTML = '<div class="gallery-empty">Photos à venir — bientôt notre galerie gourmande !</div>';
          return;
        }
        const limit = parseInt(grid.dataset.galleryLimit || '8', 10);
        const showAll = !limit || photos.length <= limit;
        const initialCount = showAll ? photos.length : limit;

        grid.innerHTML = photos.slice(0, initialCount).map((p, i) => galleryCardHTML(p, i)).join('');
        wireGalleryReveal(grid);
        setupGallery(grid, photos);

        if (!showAll) {
          const moreBtn = document.createElement('button');
          moreBtn.type = 'button';
          moreBtn.className = 'btn btn-outline-dark gallery-more-btn';
          moreBtn.textContent = `Voir ${photos.length - initialCount} photos de plus`;
          moreBtn.addEventListener('click', () => {
            grid.insertAdjacentHTML('beforeend', photos.slice(initialCount).map((p, i) => galleryCardHTML(p, i + initialCount)).join(''));
            wireGalleryReveal(grid);
            setupGallery(grid, photos);
            moreBtn.remove();
          });
          grid.insertAdjacentElement('afterend', moreBtn);
        }
      })
      .catch(() => {
        grid.innerHTML = '<div class="gallery-empty">Photos à venir — bientôt notre galerie gourmande !</div>';
      });
  });

  /* ---- Confetti burst on the WhatsApp reservation buttons ---- */
  if (!reducedMotion) {
    const confettiColors = ['#C9932A', '#C14E36', '#3D7D55', '#7D4A6C', '#2C7A78'];
    function burstConfetti(x, y) {
      for (let i = 0; i < 14; i++) {
        const piece = document.createElement('span');
        piece.className = 'confetti-piece';
        const angle = Math.random() * Math.PI * 2;
        const dist = 50 + Math.random() * 60;
        piece.style.setProperty('--dx', (Math.cos(angle) * dist).toFixed(0) + 'px');
        piece.style.setProperty('--dy', (Math.sin(angle) * dist - 30).toFixed(0) + 'px');
        piece.style.setProperty('--rot', (Math.random() * 720 - 360).toFixed(0) + 'deg');
        piece.style.background = confettiColors[i % confettiColors.length];
        piece.style.left = x + 'px';
        piece.style.top = y + 'px';
        document.body.appendChild(piece);
        piece.addEventListener('animationend', () => piece.remove());
      }
    }
    document.querySelectorAll('a.btn-primary[href*="wa.me"], .whatsapp-fab').forEach(btn => {
      btn.addEventListener('click', e => burstConfetti(e.clientX, e.clientY));
    });
  }

  /* ---- "Surprends-moi" random dish picker ---- */
  const surpriseBtn = document.getElementById('surprise-btn');
  if (surpriseBtn) {
    surpriseBtn.addEventListener('click', async () => {
      const card = document.getElementById('surprise-card');
      const img = document.getElementById('surprise-img');
      const caption = document.getElementById('surprise-caption');
      const cta = document.getElementById('surprise-cta');

      surpriseBtn.disabled = true;
      card.classList.remove('landed');
      card.classList.add('spinning');
      caption.textContent = 'On cherche…';

      const panda = document.getElementById('panda-mascot');
      if (panda) {
        panda.classList.remove('excited');
        void panda.offsetWidth;
        panda.classList.add('excited');
      }

      let photos;
      try {
        photos = await (await fetch('assets/img/gallery/manifest.json')).json();
      } catch (e) {
        photos = [];
      }
      if (!Array.isArray(photos) || !photos.length) {
        caption.textContent = 'Galerie indisponible pour le moment';
        card.classList.remove('spinning');
        surpriseBtn.disabled = false;
        return;
      }

      const tickDelay = reducedMotion ? 0 : 90;
      const maxTicks = reducedMotion ? 1 : 16;
      let ticks = 0;

      await new Promise(resolve => {
        const tick = () => {
          const p = photos[Math.floor(Math.random() * photos.length)];
          img.src = 'assets/img/gallery/' + p.file + '.jpg';
          ticks++;
          if (ticks >= maxTicks) { resolve(); return; }
          setTimeout(tick, tickDelay);
        };
        tick();
      });

      const final = photos[Math.floor(Math.random() * photos.length)];
      img.src = 'assets/img/gallery/' + final.file + '.jpg';
      img.alt = final.alt || '';
      const dishName = final.caption || final.alt || 'ce plat';
      caption.textContent = dishName;
      card.classList.remove('spinning');
      card.classList.add('landed');

      cta.href = 'https://wa.me/2250101736812?text=' + encodeURIComponent(
        `Bonjour Graya Holistic, le hasard m'a proposé « ${dishName} » — je voudrais le commander !`
      );
      cta.hidden = false;
      surpriseBtn.disabled = false;
      surpriseBtn.textContent = '🎲 Rejouer';
    });
  }

  /* ---- Gallery category filters ---- */
  document.querySelectorAll('.gallery-filters').forEach(filterBar => {
    const grid = filterBar.nextElementSibling;
    if (!grid) return;
    filterBar.addEventListener('click', e => {
      const btn = e.target.closest('.gallery-filter');
      if (!btn) return;
      filterBar.querySelectorAll('.gallery-filter').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      const filter = btn.dataset.filter;
      grid.querySelectorAll('.gallery-card').forEach(card => {
        const match = filter === 'all' || card.dataset.category === filter;
        card.hidden = !match;
      });
    });
  });

  /* ---- Active nav link based on current page ---- */
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href').split('/').pop();
    if (href === currentPath) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    }
  });

});
