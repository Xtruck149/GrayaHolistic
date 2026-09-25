"""Builds every HTML page of the Graya Holistic site + assets/js/data.js.

    python3 tools/build.py

Content that changes often (menu, prices, zones, hours, contacts) lives in tools/site_data.py.
The generated pages are plain static HTML: they can still be edited by hand, but the next build
overwrites them, so prefer editing this file and site_data.py."""
import html, json, os, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import site_data as D

ROOT = Path(__file__).resolve().parent.parent
V = "30"  # cache-busting version for css/js
e = html.escape


# ------------------------------------------------------------------ helpers
def fcfa(n):
    return f"{n:,}".replace(",", " ") + " FCFA"

def wa(text):
    from urllib.parse import quote
    return f"https://wa.me/{D.WHATSAPP}?text={quote(text)}"

def pic(stem, alt, cls="", w=640, h=640, lazy=True, folder="plats", extra=""):
    lz = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    webp = f"assets/img/{folder}/{stem}.webp"
    if folder == "bamboo":  # full-bleed background photos: responsive, lighter variants
        webp = f'assets/img/bamboo/{stem}-720.webp 720w, assets/img/bamboo/{stem}-1400.webp 1200w" sizes="100vw'
    return (f'<picture><source srcset="{webp}" type="image/webp">'
            f'<img src="assets/img/{folder}/{stem}.jpg" alt="{e(alt)}"{c} width="{w}" height="{h}"{lz}{extra}></picture>')

ICON = {
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.39 1.26 4.81L2 22l5.41-1.42a9.87 9.87 0 0 0 4.63 1.18h.01c5.46 0 9.9-4.45 9.9-9.91C21.95 6.45 17.5 2 12.04 2zm5.78 14.03c-.24.68-1.4 1.3-1.93 1.38-.5.08-1.12.11-1.81-.11-.42-.13-.96-.31-1.65-.61-2.9-1.25-4.79-4.17-4.94-4.36-.14-.19-1.18-1.57-1.18-3 0-1.42.75-2.12 1.02-2.41.26-.29.57-.36.76-.36l.55.01c.18.01.41-.07.64.49.24.58.81 2 .88 2.14.07.14.11.31.02.5-.09.19-.14.31-.27.48l-.41.5c-.14.14-.28.29-.12.57.16.28.71 1.17 1.52 1.9 1.05.94 1.93 1.23 2.21 1.37.28.14.44.12.6-.07.16-.19.68-.79.86-1.06.18-.27.36-.22.6-.13.24.09 1.53.72 1.79.85.26.13.43.19.5.3.07.11.07.62-.17 1.3z"/></svg>',
    "bag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 8h14l-1.3 11.2a2 2 0 0 1-2 1.8H8.3a2 2 0 0 1-2-1.8L5 8Z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M4 8h16M4 16h16"/></svg>',
    "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    "carte": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 3h10a2 2 0 0 1 2 2v16l-7-3-7 3V5a2 2 0 0 1 2-2Z"/><path d="M9.5 8h5M9.5 11.5h5"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 21v-8h2.5l.5-3H15V8.2c0-.9.3-1.5 1.6-1.5H18V4.1C17.7 4 16.8 4 15.8 4c-2.1 0-3.5 1.3-3.5 3.6V10H10v3h2.3v8"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r=".6" fill="currentColor" stroke="none"/></svg>',
}

ALL_ITEMS = {it["id"]: (sec, it) for sec in D.MENU for it in sec["items"]}

def add_buttons(it, cls="add"):
    if "sizes" in it:
        return "".join(
            f'<button type="button" class="{cls}" data-add data-id="{it["id"]}-{k}" data-name="{e(it["name"])} ({lbl.lower()})" data-price="{p}">'
            f'{lbl} · {fcfa(p)}<span class="sr-only"> — ajouter {e(it["name"])} au panier</span></button>'
            for k, lbl, p in it["sizes"])
    return (f'<button type="button" class="{cls}" data-add data-id="{it["id"]}" data-name="{e(it["name"])}" data-price="{it["price"]}">'
            f'Ajouter<span class="sr-only"> {e(it["name"])} au panier</span></button>')

def price_label(it):
    return f"dès {fcfa(it['sizes'][0][2])}" if "sizes" in it else fcfa(it["price"])


# ------------------------------------------------------------------ layout
NAV = [("menu.html", "La carte"), ("traiteur.html", "Traiteur"), ("notre-cuisine.html", "Notre cuisine"),
       ("a-propos.html", "La maison"), ("engagement.html", "Engagement"), ("contact.html", "Contact")]

def head(p):
    url = D.BASE_URL + ("" if p["file"] == "index.html" else p["file"])
    lds = "".join(f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n' for ld in p.get("ld", []))
    robots = '<meta name="robots" content="noindex">\n' if p.get("noindex") else ""
    base = '<base href="/GrayaHolistic/">\n' if p["file"] == "404.html" else ""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
{base}<script>document.documentElement.classList.add('js')</script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(p['title'])}</title>
<meta name="description" content="{e(p['desc'])}">
{robots}<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0D1C14">
<link rel="icon" href="assets/img/favicon.ico" sizes="any">
<link rel="icon" href="assets/img/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="assets/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_CI">
<meta property="og:site_name" content="Graya Holistic">
<meta property="og:title" content="{e(p['title'])}">
<meta property="og:description" content="{e(p['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{D.BASE_URL}assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/bodoni-moda-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/jost-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
{'<link rel="preload" href="assets/img/logo-lockup.webp" as="image" type="image/webp">' + chr(10) if p["file"] == "index.html" else ""}<link rel="stylesheet" href="assets/css/style.css?v={V}">
{lds}</head>
"""

def header(active):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{f}"{cur if f == active else ""}>{t}</a>' for f, t in NAV)
    return f"""<body>
<a href="#main" class="skip-link">Aller au contenu</a>
<header class="site-header">
  <div class="shell header-row">
    <a href="index.html" class="brand" aria-label="Graya Holistic, accueil">
      <picture><source srcset="assets/img/logo-plate-160.webp" type="image/webp"><img src="assets/img/logo-plate-160.png" alt="" width="160" height="128"></picture>
      <span>Graya Holistic</span>
    </a>
    <nav class="nav" id="site-nav" aria-label="Navigation principale">{links}</nav>
    <a href="menu.html" class="btn btn--gold btn--sm header-cta">Commander</a>
    <button type="button" class="cart-btn" data-cart-open aria-label="Ouvrir le panier">{ICON['bag']}<span class="cart-count" data-cart-count hidden>0</span></button>
    <button type="button" class="burger" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="site-nav">{ICON['menu']}</button>
  </div>
</header>
"""

def footer():
    phones = "".join(f'<a href="tel:{t}">{e(d)}</a>' for t, d in D.PHONES)
    hours = "".join(f"<p>{e(h['label'])} : {h['opens'].replace(':', ' h ')} – {h['closes'].replace(':', ' h ')}</p>" for h in D.HOURS).replace(" h 00", " h")
    return f"""<footer class="site-footer">
  <img class="deco deco--footer" src="assets/img/deco/bamboo-grove.svg" alt="" aria-hidden="true" loading="lazy">
  <div class="shell">
    <div class="footer-grid">
      <div class="footer-brand">
        <picture><source srcset="assets/img/logo-lockup.webp" type="image/webp"><img src="assets/img/logo-lockup.png" alt="Graya Holistic, Côte d'Ivoire — Le goût du bien-être" width="548" height="644" loading="lazy"></picture>
      </div>
      <div><h2>Commander</h2><a href="menu.html">La carte</a><a href="traiteur.html">Traiteur</a><a href="services.html">Nos services</a><a href="faq.html">Questions fréquentes</a></div>
      <div><h2>La maison</h2><a href="notre-cuisine.html">Notre cuisine</a><a href="a-propos.html">Qui sommes-nous</a><a href="engagement.html">Engagement</a><a href="contact.html">Contact</a></div>
      <div><h2>Nous joindre</h2>{phones}<a href="{wa('Bonjour Graya Holistic,')}">WhatsApp</a><a href="mailto:{D.EMAIL}">{e(D.EMAIL)}</a><p>{e(D.AREA_LABEL)}</p>{hours}
        <div class="social"><a href="{D.SOCIAL['Facebook']}" aria-label="Facebook" target="_blank" rel="noopener">{ICON['fb']}</a><a href="{D.SOCIAL['Instagram']}" aria-label="Instagram" target="_blank" rel="noopener">{ICON['ig']}</a></div>
      </div>
    </div>
    <div class="footer-bottom"><span>© <span data-year>2026</span> Graya Holistic®. Labellisé ÉCO BMT™.</span><span>Bien manger, bien vivre, bien-être</span></div>
  </div>
</footer>
<script src="assets/js/data.js?v={V}" defer></script>
<script src="assets/js/main.js?v={V}" defer></script>
</body>
</html>
"""

def page_hero(title, lead, crumb, photo="bamboo-sunlit-path", kicker=None):
    k = f'<p class="kicker">{kicker}</p>' if kicker else ""
    return f"""<section class="page-hero" data-stalk="{e(crumb)}">
  <div class="page-hero-bg" data-parallax>{pic(photo, "", folder="bamboo", w=1200, h=1800, lazy=False)}</div>
  <img class="deco deco--hero-l" src="assets/img/deco/bamboo-grove.svg" alt="" aria-hidden="true">
  <div class="shell">
    <nav class="crumbs" aria-label="Fil d'Ariane"><a href="index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">{e(crumb)}</span></nav>
    {k}<h1>{title}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>
"""

def cta(title, text, primary=("menu.html", "Voir la carte"), wa_text="Bonjour Graya Holistic, j'ai une question."):
    return f"""<section class="band cta">
  <img class="deco deco--cta-l" src="assets/img/deco/bamboo-culm.svg" alt="" aria-hidden="true" loading="lazy">
  <img class="deco deco--cta-r" src="assets/img/deco/bamboo-culm.svg" alt="" aria-hidden="true" loading="lazy">
  <div class="shell">
    <img class="sprig" src="assets/img/deco/bamboo-sprig.svg" alt="" aria-hidden="true" width="160" height="60" loading="lazy">
    <h2>{title}</h2>
    <p>{text}</p>
    <div class="actions"><a href="{primary[0]}" class="btn btn--gold">{primary[1]}</a><a href="{wa(wa_text)}" class="btn btn--ghost">{ICON['wa']}Écrire sur WhatsApp</a></div>
  </div>
</section>
"""

def crumbs_ld(name, file):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": D.BASE_URL},
        {"@type": "ListItem", "position": 2, "name": name, "item": D.BASE_URL + file}]}

def restaurant_ld():
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return {
        "@context": "https://schema.org", "@type": "Restaurant", "@id": D.BASE_URL + "#restaurant",
        "name": "Graya Holistic", "alternateName": "Graya Holistic — Cuisine Holistique Consciente",
        "url": D.BASE_URL, "logo": D.BASE_URL + "assets/img/logo-plate.png", "image": D.BASE_URL + "assets/img/og-image.jpg",
        "description": "Atelier culinaire et traiteur à Bingerville (Abidjan) : cuisine holistique consciente, livrée dans le grand Abidjan.",
        "servesCuisine": ["Ivoirienne", "Africaine", "Cuisine holistique"], "priceRange": "500 – 5 000 FCFA",
        "currenciesAccepted": "XOF", "hasMenu": D.BASE_URL + "menu.html", "acceptsReservations": False,
        "address": {"@type": "PostalAddress", "addressLocality": D.CITY, "addressRegion": D.REGION, "addressCountry": "CI"},
        "areaServed": [z for z, _ in D.ZONES],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": [days[d] for d in h["days"]], "opens": h["opens"], "closes": h["closes"]} for h in D.HOURS],
        "telephone": D.PHONES[0][0], "email": D.EMAIL, "sameAs": list(D.SOCIAL.values()),
    }


# ------------------------------------------------------------------ blocks
def dish_card(item_id):
    sec, it = ALL_ITEMS[item_id]
    return f"""<article class="dish">
        <div class="dish-img" data-unveil>{pic(it['img'], it['name'])}</div>
        <h3>{e(it['name'])}</h3><p class="sub">{e(it['sub'])}</p>
        <p>{e(it['desc'])}</p>
        <div class="dish-foot"><span class="price">{price_label(it)}</span>{add_buttons(it)}</div>
      </article>"""

def carte_item(it):
    img = pic(it["img"], "", cls="item-img", w=640, h=800 if it["img"].startswith("jus") else 640) if it["img"] else ""
    return f"""<li class="item{'' if it['img'] else ' item--noimg'}" id="plat-{it['id']}" data-dish="{it['id']}">
          {img}<div>
            <div class="item-line"><h3>{e(it['name'])}</h3><span class="leader" aria-hidden="true"></span><span class="price">{price_label(it)}</span></div>
            <p class="sub">{e(it['sub'])}</p><p>{e(it['desc'])}</p>
            <div class="item-actions">{add_buttons(it)}</div>
          </div>
        </li>"""

def hours_dl():
    rows = "".join(f"<dt>{e(h['label'])}</dt><dd>{h['opens'].replace(':', ' h ')} – {h['closes'].replace(':', ' h ')}</dd>" for h in D.HOURS)
    return f'<dl class="hours">{rows.replace(" h 00", " h")}<dt>Traiteur</dt><dd>Sur demande</dd></dl>'

def zones_ul():
    return '<ul class="zones">' + "".join(f"<li>{e(z)}</li>" for z, _ in D.ZONES) + "</ul>"

GALLERY = '<div class="gallery" data-gallery{attrs}></div><noscript><p class="lead">Activez JavaScript pour voir la galerie.</p></noscript>'


# ------------------------------------------------------------------ pages
def page_index():
    dishes = "\n      ".join(dish_card(i) for i in D.SIGNATURE)
    return f"""<main id="main">
<section class="hero" data-stalk="Accueil">
  <div class="hero-bg" data-parallax>{pic('bamboo-sunlit-path', '', folder='bamboo', w=1200, h=1800, lazy=False)}</div>
  <img class="deco deco--hero-l" src="assets/img/deco/bamboo-grove.svg" alt="" aria-hidden="true">
  <img class="deco deco--hero-r" src="assets/img/deco/bamboo-grove.svg" alt="" aria-hidden="true">
  <div class="shell hero-inner">
    <div class="hero-logo">
      <picture><source srcset="assets/img/logo-lockup.webp" type="image/webp"><img src="assets/img/logo-lockup.png" alt="Graya Holistic, Côte d'Ivoire — Le goût du bien-être" width="548" height="644" fetchpriority="high"></picture>
    </div>
    <div class="hero-copy">
      <h1>Cuisine holistique consciente, cuisinée à Bingerville et livrée dans tout Abidjan</h1>
      <p class="lead">Une gastronomie qui nourrit le corps, apaise l'esprit et élève l'âme, avec des plantes et épices locales.</p>
      <div class="actions">
        <a href="menu.html" class="btn btn--gold">Voir la carte</a>
        <a href="{wa('Bonjour Graya Holistic, je souhaite passer une commande.')}" class="btn btn--ghost">{ICON['wa']}Commander sur WhatsApp</a>
      </div>
    </div>
  </div>
  <div class="shell hero-facts">
    <span><strong>Lun – Sam, 11 h – 21 h 30</strong>Dimanche 12 h – 20 h</span>
    <span><strong>{len(D.ZONES)} zones livrées</strong>de Bingerville à Yopougon</span>
    <span><strong>Labellisé ÉCO BMT™</strong>Restauration responsable</span>
  </div>
</section>

<section class="band" data-stalk="Nos racines">
  <div class="shell manifesto">
    <blockquote>« Graya Holistic transforme l'alimentation en un acte de soin, de conscience et de dignité. »<cite>Une initiative pionnière en Côte d'Ivoire</cite></blockquote>
    <ul class="roots">
      <li><div><h2 class="h3">Savoirs culinaires africains</h2><p>Un héritage gastronomique transmis et réinventé, ancré dans la culture ivoirienne.</p></div></li>
      <li><div><h2 class="h3">Plantes &amp; épices locales</h2><p>Des ingrédients du terroir choisis pour leurs vertus nutritives et thérapeutiques.</p></div></li>
      <li><div><h2 class="h3">Bien-être holistique</h2><p>Le corps, l'esprit et l'émotion replacés au centre du repas.</p></div></li>
    </ul>
  </div>
</section>

<section class="band band--canopee" data-stalk="La carte">
  <img class="deco deco--band-r" src="assets/img/deco/bamboo-grove.svg" alt="" aria-hidden="true" loading="lazy">
  <div class="shell">
    <div class="section-head">
      <div><p class="kicker">La carte</p><h2>Quatre plats pour commencer</h2></div>
      <p>Chaque création porte un nom et une histoire. Ajoutez-la au panier, choisissez votre zone : la commande part sur WhatsApp.</p>
    </div>
    <div class="dishes">
      {dishes}
    </div>
    <div class="actions mt-xl"><a href="menu.html" class="btn btn--ghost">Voir toute la carte</a></div>
  </div>
</section>

<section class="band band--photo" data-stalk="Notre approche">
  <div class="photo" data-parallax>{pic('bamboo-grove-golden', '', folder='bamboo', w=1200, h=1920)}</div>
  <div class="shell">
    <div class="section-head"><div><p class="kicker">Notre approche</p><h2>Une cuisine qui soigne autant qu'elle nourrit</h2></div></div>
    <ul class="pillars">
      <li><h3>Cuisine consciente</h3><p>Cuisiner avec intention, conscience et énergie pour nourrir le corps et l'esprit.</p></li>
      <li><h3>Art comestible thérapeutique</h3><p>L'assiette comme expérience sensorielle et émotionnelle, source d'apaisement.</p></li>
      <li><h3>Phytothérapie</h3><p>Plantes médicinales et épices traditionnelles, choisies pour leurs vertus.</p></li>
      <li><h3>Éco-thérapie</h3><p>Des recettes pensées pour soutenir le bien-être et l'énergie positive.</p></li>
    </ul>
  </div>
</section>

<section class="band band--papier" data-stalk="Traiteur">
  <div class="shell split">
    <div class="split-media" data-unveil>
      {pic('plat-08', 'Grillades et frites maison dressées pour un buffet', folder='gallery', w=605, h=1080)}
      {pic('plat-18', 'Salade fraîcheur, tomates cerises et concombre', cls='inset', folder='gallery', w=605, h=1080)}
    </div>
    <div>
      <p class="kicker">Traiteur événementiel</p>
      <h2>Vos réceptions, cuisinées en conscience</h2>
      <p>Mariages, séminaires, anniversaires ou déjeuners d'équipe : nous composons avec vous un menu sur mesure, sain et généreux, livré le jour J.</p>
      <ul class="checklist">
        <li>Un menu construit selon vos invités et votre budget</li>
        <li>Les jus thérapeutiques Nectar d'Eden en option</li>
        <li>Un atelier bien-être possible pour vos équipes</li>
      </ul>
      <a href="traiteur.html" class="btn btn--gold">Demander un devis</a>
    </div>
  </div>
</section>

<section class="band" data-stalk="Galerie">
  <div class="shell">
    <div class="section-head"><div><p class="kicker">En images</p><h2>La galerie gourmande</h2></div><p>Saveurs, couleurs et gestes conscients, tels qu'ils sortent de notre cuisine.</p></div>
    {GALLERY.format(attrs=' data-limit="8"')}
    <div class="actions mt-xl"><a href="notre-cuisine.html#galerie" class="btn btn--ghost">Voir toute la galerie</a></div>
  </div>
</section>

<section class="band band--canopee" data-stalk="Livraison">
  <div class="shell info">
    <div>
      <p class="kicker">Livraison</p>
      <h2>De Bingerville à tout le grand Abidjan</h2>
      <p class="lead">Notre cuisine est à Bingerville. Les frais dépendent de la distance et s'ajoutent automatiquement à votre panier.</p>
      {zones_ul()}
    </div>
    {hours_dl()}
  </div>
</section>

{cta("À table, où que vous soyez", "Composez votre panier en deux minutes, ou écrivez-nous directement.")}
</main>
"""

def page_menu():
    chips = '<button type="button" class="chip" data-filter="all" aria-pressed="true">Toute la carte</button>' + "".join(
        f'<button type="button" class="chip" data-filter="{s["id"]}" aria-pressed="false">{e(s["title"])}</button>' for s in D.MENU)
    secs = ""
    for s in D.MENU:
        items = "\n        ".join(carte_item(it) for it in s["items"])
        logo = ('<img class="nectar" src="assets/img/nectar-deden.webp" alt="Nectar d\'Eden, jus naturel thérapeutique" width="320" height="320" loading="lazy">'
                if s["id"] == "jus" else "")
        secs += f"""
    <section class="carte-section" id="{s['id']}" data-cat="{s['id']}" data-stalk="{e(s['title'])}">
      <div class="carte-title">{logo}<h2>{e(s['title'])}</h2><p>{e(s['intro'])}</p></div>
      <ul class="items">
        {items}
      </ul>
    </section>"""
    return f"""<main id="main">
{page_hero("La carte", "Brochettes signature, spécialités au feu de bois, soupes, accompagnements, jus thérapeutiques et thé digestif. Prix en FCFA.", "La carte", photo="bamboo-stalks-vivid")}
<div class="carte-nav"><div class="shell">
  <div class="chips" role="group" aria-label="Filtrer la carte">{chips}</div>
  <button type="button" class="btn btn--ghost btn--sm" data-chef>Laisser le chef choisir</button>
</div></div>
<div class="shell carte">{secs}
</div>
<section class="band">
  <div class="shell">
    <blockquote class="signature">« Quand la cuisine devient soin, l'assiette devient langage, et le repas, un acte de bien-être. »<cite>Signature Graya Holistic®</cite></blockquote>
  </div>
</section>
{cta("Une question sur un plat ?", "Allergies, quantités pour un groupe, disponibilité du jour : écrivez-nous, nous répondons vite.", primary=("traiteur.html", "Commander pour un groupe"))}
</main>
"""

def page_traiteur():
    return f"""<main id="main">
{page_hero("Traiteur événementiel", "Un menu sur mesure, sain et généreux, pour vos événements privés, professionnels ou institutionnels, cuisiné à Bingerville et livré dans tout Abidjan.", "Traiteur", photo="bamboo-grove-golden")}

<section class="band band--papier" data-stalk="Occasions">
  <div class="shell split">
    <div>
      <p class="kicker">Pour quelles occasions</p>
      <h2>Chaque réception mérite une cuisine qui prend soin</h2>
      <p>Mariages et dots, anniversaires, baptêmes, séminaires, déjeuners d'équipe, réceptions institutionnelles : nous adaptons les quantités, le service et les saveurs à votre public.</p>
      <ul class="checklist">
        <li>Plats de notre carte ou créations sur mesure</li>
        <li>Jus thérapeutiques Nectar d'Eden, au verre ou en bouteille</li>
        <li>Atelier bien-être possible pour vos équipes</li>
        <li>Préférences respectées : sans porc, végétarien, peu épicé…</li>
      </ul>
    </div>
    <div class="split-media" data-unveil>
      {pic('plat-07', 'Brochettes mixtes sur la braise', folder='gallery', w=605, h=1080)}
      {pic('soupe-kedjenou', 'Kedjenou mijoté en canari', cls='inset')}
    </div>
  </div>
</section>

<section class="band" data-stalk="Déroulé">
  <div class="shell">
    <div class="section-head"><div><p class="kicker">Comment ça se passe</p><h2>Trois étapes jusqu'au jour J</h2></div></div>
    <ol class="steps-list">
      <li><h3>Vous décrivez votre événement</h3><p>Date, nombre d'invités, type de service et vos envies, avec le formulaire ci-dessous.</p></li>
      <li><h3>Nous vous proposons un menu</h3><p>Nous revenons vers vous sur WhatsApp avec une proposition et un devis.</p></li>
      <li><h3>Nous cuisinons et livrons</h3><p>Tout est préparé le jour même dans notre cuisine de Bingerville, puis livré à l'heure convenue.</p></li>
    </ol>
  </div>
</section>

<section class="band band--canopee" id="devis" data-stalk="Demande de devis">
  <div class="shell devis">
    <div class="devis-intro">
      <p class="kicker">Demande de devis</p>
      <h2>Parlez-nous de votre événement</h2>
      <p class="lead">Deux minutes suffisent. Votre demande s'ouvre dans WhatsApp, prête à envoyer.</p>
    </div>
    <form class="quote-form" data-quote novalidate>
      <ol class="stepper" aria-label="Étapes de la demande">
        <li aria-current="step">Événement</li><li>Repas</li><li>Coordonnées</li>
      </ol>

      <fieldset data-step="1">
        <legend class="sr-only">Votre événement</legend>
        <div class="field"><label for="q-type">Type d'événement</label>
          <select id="q-type" name="type" required><option value="">Choisir</option><option>Mariage ou dot</option><option>Anniversaire</option><option>Baptême ou cérémonie familiale</option><option>Séminaire ou réunion</option><option>Déjeuner d'équipe</option><option>Réception institutionnelle</option><option>Autre</option></select></div>
        <div class="grid-2">
          <div class="field"><label for="q-date">Date</label><input id="q-date" name="date" type="date" required></div>
          <div class="field"><label for="q-time">Heure de service</label><input id="q-time" name="time" type="time" value="12:30" required></div>
        </div>
        <div class="grid-2">
          <div class="field"><label for="q-guests">Nombre d'invités</label><input id="q-guests" name="guests" type="number" min="5" max="2000" inputmode="numeric" placeholder="ex. 60" required></div>
          <div class="field"><label for="q-place">Commune ou lieu</label><input id="q-place" name="place" type="text" placeholder="ex. Cocody, Riviera 3" required></div>
        </div>
      </fieldset>

      <fieldset data-step="2" hidden>
        <legend class="sr-only">Le repas</legend>
        <div class="field"><span class="label" id="q-service-l">Type de service</span>
          <div class="options" role="radiogroup" aria-labelledby="q-service-l">
            <label><input type="radio" name="service" value="Buffet" required><span>Buffet</span></label>
            <label><input type="radio" name="service" value="Cocktail dînatoire"><span>Cocktail dînatoire</span></label>
            <label><input type="radio" name="service" value="Repas servi à table"><span>Repas servi à table</span></label>
            <label><input type="radio" name="service" value="Coffrets repas individuels"><span>Coffrets individuels</span></label>
          </div></div>
        <div class="field"><label for="q-budget">Budget par personne (indicatif)</label>
          <select id="q-budget" name="budget"><option value="">Je ne sais pas encore</option><option>Moins de 5 000 FCFA</option><option>5 000 – 10 000 FCFA</option><option>10 000 – 20 000 FCFA</option><option>Plus de 20 000 FCFA</option></select></div>
        <div class="field"><span class="label" id="q-pref-l">Préférences</span>
          <div class="options options--multi" role="group" aria-labelledby="q-pref-l">
            <label><input type="checkbox" name="pref" value="Sans porc"><span>Sans porc</span></label>
            <label><input type="checkbox" name="pref" value="Options végétariennes"><span>Végétarien</span></label>
            <label><input type="checkbox" name="pref" value="Peu épicé"><span>Peu épicé</span></label>
            <label><input type="checkbox" name="pref" value="Jus Nectar d'Eden"><span>Jus Nectar d'Eden</span></label>
            <label><input type="checkbox" name="pref" value="Atelier bien-être"><span>Atelier bien-être</span></label>
          </div></div>
      </fieldset>

      <fieldset data-step="3" hidden>
        <legend class="sr-only">Vos coordonnées</legend>
        <div class="grid-2">
          <div class="field"><label for="q-name">Nom complet</label><input id="q-name" name="name" type="text" autocomplete="name" required></div>
          <div class="field"><label for="q-phone">Téléphone</label><input id="q-phone" name="phone" type="tel" autocomplete="tel" placeholder="07 00 00 00 00" required></div>
        </div>
        <div class="field"><label for="q-msg">Précisions (facultatif)</label><textarea id="q-msg" name="message" rows="4" placeholder="Thème, plats souhaités, allergies…"></textarea></div>
        <div class="summary" data-summary aria-live="polite"></div>
      </fieldset>

      <p class="form-error" data-error role="alert" hidden></p>
      <div class="form-nav">
        <button type="button" class="btn btn--ghost" data-prev hidden>Retour</button>
        <button type="button" class="btn btn--gold" data-next>Continuer</button>
        <button type="submit" class="btn btn--gold" data-submit hidden>{ICON['wa']}Envoyer la demande sur WhatsApp</button>
      </div>
    </form>
  </div>
</section>

{cta("Une question avant de vous lancer ?", "Écrivez-nous : nous vous aidons à estimer quantités et formules.", primary=("faq.html", "Lire les questions fréquentes"), wa_text="Bonjour Graya Holistic, j'ai une question sur le traiteur.")}
</main>
"""

def page_cuisine():
    return f"""<main id="main">
{page_hero("Cuisine Holistique Consciente™", "Une gastronomie qui nourrit le corps, apaise l'esprit et élève l'âme, en harmonie avec la nature.", "Notre cuisine")}

<section class="band" data-stalk="Nos créations">
  <div class="shell">
    <div class="rows">
      <article class="row">
        <div class="row-media" data-unveil>{pic('soupe-du-pecheur', 'La Soupe du Pêcheur')}</div>
        <div><p class="kicker">Les plats</p><h2>Savoureux et équilibrés</h2><p>Des créations élaborées à partir d'ingrédients frais, locaux et de saison. Chaque plat est conçu pour respecter votre santé et sublimer les saveurs naturelles.</p><a href="menu.html" class="btn btn--ghost mt-lg">Voir les plats</a></div>
      </article>
      <article class="row row--flip">
        <div class="row-media" data-unveil>{pic('jus-hibiscus', 'Jus d’Hibiscus Nectar d’Eden', w=640, h=800)}</div>
        <div><p class="kicker">Les boissons bien-être</p><h2>Naturelles et revitalisantes</h2><p>Les jus Nectar d'Eden, à base de fruits, plantes, épices et super-aliments, pour hydrater, détoxifier et renforcer votre vitalité au quotidien.</p><a href="menu.html#jus" class="btn btn--ghost mt-lg">Voir les jus</a></div>
      </article>
      <article class="row">
        <div class="row-media" data-unveil>{pic('plat-18', 'Salade fraîcheur, tomates cerises et concombre', folder='gallery', w=605, h=1080)}</div>
        <div><p class="kicker">Les desserts</p><h2>Sains et gourmands</h2><p>Des douceurs préparées avec des ingrédients naturels et peu transformés, pour finir le repas avec légèreté et plaisir.</p></div>
      </article>
    </div>
  </div>
</section>

<section class="band band--photo" data-stalk="Patience">
  <div class="photo" data-parallax>{pic('bamboo-stalks-vivid', '', folder='bamboo', w=1000, h=1503)}</div>
  <div class="shell narrow">
    <p class="kicker">Patience &amp; croissance</p>
    <h2>Une cuisine qui prend le temps de bien faire</h2>
    <p class="lead">Le bambou pousse vite une fois enraciné, mais ses racines se construisent en silence, année après année. C'est ainsi que nous cuisinons : avec la patience des saveurs qui infusent, des sauces qui mijotent, et des recettes transmises puis affinées au fil du temps.</p>
  </div>
</section>

<section class="band" id="galerie" data-stalk="Galerie">
  <div class="shell">
    <div class="section-head"><div><p class="kicker">En images</p><h2>La galerie gourmande</h2></div>
      <div class="chips" role="group" aria-label="Filtrer la galerie" data-gallery-filters>
        <button type="button" class="chip" data-gfilter="all" aria-pressed="true">Tout</button><button type="button" class="chip" data-gfilter="poulet" aria-pressed="false">Poulet</button><button type="button" class="chip" data-gfilter="boeuf" aria-pressed="false">Bœuf</button><button type="button" class="chip" data-gfilter="poisson-vege" aria-pressed="false">Poisson &amp; végé</button><button type="button" class="chip" data-gfilter="autres" aria-pressed="false">Autres</button>
      </div></div>
    {GALLERY.format(attrs='')}
  </div>
</section>

<section class="band band--canopee" data-stalk="Nos principes">
  <div class="shell">
    <div class="section-head"><div><p class="kicker">Ce qui nous distingue</p><h2>Quatre principes dans chaque assiette</h2></div></div>
    <ul class="pillars">
      <li><h3>Ingrédients de qualité</h3><p>Une sélection rigoureuse des meilleurs produits naturels.</p></li>
      <li><h3>Cuisson saine</h3><p>Des méthodes douces pour préserver les nutriments et les saveurs.</p></li>
      <li><h3>Équilibre &amp; harmonie</h3><p>Des recettes pensées pour le corps, l'esprit et l'émotion.</p></li>
      <li><h3>Éthique &amp; durabilité</h3><p>Respect de la nature, des producteurs et des générations futures.</p></li>
    </ul>
  </div>
</section>

{cta("Envie de goûter ?", "Commandez en livraison ou pour un événement, réponse rapide sur WhatsApp.")}
</main>
"""

def page_services():
    return f"""<main id="main">
{page_hero("Nos services", "Un atelier culinaire à Bingerville, sans salle ni attente : votre commande où que vous soyez dans le grand Abidjan.", "Nos services")}
<section class="band" data-stalk="Services">
  <div class="shell">
    <div class="rows">
      <article class="row">
        <div class="row-media" data-unveil>{pic('plat-28', 'Wrap de poulet croustillant', folder='gallery', w=605, h=1080)}</div>
        <div><p class="kicker">Au quotidien</p><h2>Livraison express</h2><p>Composez votre panier sur la carte, choisissez votre zone et l'heure : vos plats holistiques arrivent chez vous ou au bureau, préparés avec des ingrédients frais et de saison.</p><a href="menu.html" class="btn btn--gold mt-lg">Commander</a></div>
      </article>
      <article class="row row--flip">
        <div class="row-media" data-unveil>{pic('plat-08', 'Grillades et frites maison', folder='gallery', w=605, h=1080)}</div>
        <div><p class="kicker">Pour vos événements</p><h2>Traiteur événementiel</h2><p>Menus sur mesure pour vos événements privés, professionnels ou institutionnels : sains, gourmands et équilibrés.</p><a href="traiteur.html" class="btn btn--gold mt-lg">Demander un devis</a></div>
      </article>
      <article class="row">
        <div class="row-media" data-unveil>{pic('plat-18', 'Salade fraîcheur', folder='gallery', w=605, h=1080)}</div>
        <div><p class="kicker">Sur la durée</p><h2>Cures &amp; formules holistiques</h2><p>Des formules hebdomadaires de repas conscients, pensées pour accompagner durablement votre bien-être et livrées à votre rythme.</p><a href="{wa("Bonjour Graya Holistic, je voudrais des informations sur les cures et formules.")}" class="btn btn--ghost mt-lg">{ICON['wa']}Demander les formules</a></div>
      </article>
    </div>
  </div>
</section>
<section class="band band--canopee" data-stalk="Notre promesse">
  <div class="shell">
    <div class="section-head"><div><p class="kicker">Notre promesse</p><h2>Un même engagement, à chaque service</h2></div></div>
    <ul class="pillars">
      <li><h3>Produits locaux et de saison</h3><p>Soutenir nos producteurs et garantir la fraîcheur.</p></li>
      <li><h3>Cuisine saine et équilibrée</h3><p>Des recettes savoureuses pour votre bien-être.</p></li>
      <li><h3>Engagement écoresponsable</h3><p>Des pratiques durables pour un avenir meilleur.</p></li>
      <li><h3>Service attentionné</h3><p>Une équipe à votre écoute, de la commande à la livraison.</p></li>
    </ul>
  </div>
</section>
{cta("Une envie, un événement, une cure à démarrer ?", "Livraison, traiteur ou formule holistique : parlons-en.")}
</main>
"""

def page_apropos():
    return f"""<main id="main">
{page_hero("Qui sommes-nous", "Graya Holistic® est une initiative pionnière en Côte d'Ivoire qui transforme l'alimentation en un acte de soin, de conscience et de dignité.", "La maison", photo="bamboo-grove-golden")}
<section class="band" data-stalk="Philosophie">
  <div class="shell split">
    <div class="split-media" data-unveil>{pic('bamboo-stalks-vivid', 'Tiges de bambou vert', folder='bamboo', w=1000, h=1503)}</div>
    <div>
      <p class="kicker">Notre philosophie</p>
      <h2>Un dialogue entre le corps, l'esprit et la terre</h2>
      <p>Nous croyons que manger ne se résume pas à se nourrir : c'est un dialogue entre le corps, l'esprit, la terre et l'environnement.</p>
      <p>Ici, la cuisine devient un langage de santé, de culture et de lien humain. La cuisine qui soigne, l'art qui nourrit, l'expérience qui transforme.</p>
      <p>Comme le bambou, nous grandissons vite mais restons souples et résistants : ancrés dans nos racines ivoiriennes, ouverts sur le monde.</p>
    </div>
  </div>
</section>
<section class="band band--canopee" data-stalk="Vision">
  <div class="shell">
    <div class="section-head"><div><p class="kicker">Vision, mission, ambition</p><h2>Ce qui nous fait avancer</h2></div></div>
    <div class="trio">
      <div><h3>Notre vision</h3><p>Faire de Graya Holistic® la référence en Côte d'Ivoire et en Afrique d'une gastronomie consciente, thérapeutique et durable, au service du bien-être individuel et collectif.</p></div>
      <div><h3>Notre mission</h3><p>Offrir une expérience culinaire unique qui nourrit le corps, apaise l'esprit, valorise nos ressources locales et inspire un mode de vie sain et respectueux de la nature.</p></div>
      <div><h3>Notre ambition</h3><p>Devenir un acteur majeur de la gastronomie holistique en Afrique, en valorisant nos terroirs, nos cultures et notre biodiversité.</p></div>
    </div>
  </div>
</section>
<section class="band" data-stalk="Trois héritages">
  <div class="shell manifesto">
    <blockquote>Trois héritages, une même conscience.<cite>Née de la rencontre entre</cite></blockquote>
    <ul class="roots">
      <li><div><h3>Les savoirs culinaires africains</h3><p>Transmis de génération en génération, puis réinventés.</p></div></li>
      <li><div><h3>Les plantes et épices locales</h3><p>Choisies pour leurs vertus nutritives et thérapeutiques.</p></div></li>
      <li><div><h3>Le bien-être holistique</h3><p>Des approches contemporaines qui replacent l'humain au centre du repas.</p></div></li>
    </ul>
  </div>
</section>
{label_band()}
{cta("Envie de nous goûter ?", "Découvrez la carte, ou écrivez-nous pour une commande de groupe.")}
</main>
"""

def label_band():
    return """<section class="band band--papier label-band" data-stalk="Label">
  <div class="shell label">
    <picture><source srcset="assets/img/eco-bmt-badge.webp" type="image/webp"><img src="assets/img/eco-bmt-badge.jpg" alt="Label ÉCO BMT" width="200" height="200" loading="lazy"></picture>
    <div><p class="kicker">Un label engagé</p><h2>Labellisé ÉCO BMT™</h2><p>Éducation et design, santé, durabilité : une restauration responsable pour un avenir meilleur.</p><a href="engagement.html" class="btn btn--gold mt-lg">Découvrir notre engagement</a></div>
  </div>
</section>"""

def page_engagement():
    return f"""<main id="main">
{page_hero("Une marque engagée pour l'humain et la planète", "Bien manger, bien vivre, bien-être aujourd'hui pour un avenir meilleur demain.", "Engagement")}
<section class="band" data-stalk="Nos engagements">
  <div class="shell">
    <div class="section-head"><div><p class="kicker">Graya Holistic s'engage à</p><h2>Cinq engagements, une même conscience</h2></div></div>
    <ul class="commitments">
      <li><h3>Valoriser les plantes et épices</h3><p>Locales et du monde entier.</p></li>
      <li><h3>Soutenir le terroir ivoirien</h3><p>Les produits et les producteurs locaux.</p></li>
      <li><h3>Promouvoir une alimentation consciente</h3><p>Saine et responsable.</p></li>
      <li><h3>Respecter le vivant</h3><p>La biodiversité, la plante et la terre.</p></li>
      <li><h3>Contribuer à un avenir durable</h3><p>À travers une gastronomie porteuse de sens.</p></li>
    </ul>
  </div>
</section>
<section class="band band--photo" data-stalk="Croissance">
  <div class="photo" data-parallax>{pic('bamboo-sunlit-path', '', folder='bamboo', w=1200, h=1800)}</div>
  <div class="shell narrow">
    <p class="kicker">Une croissance responsable</p>
    <h2>Comme une bambouseraie, notre impact grandit racine par racine</h2>
    <p class="lead">Le bambou régénère les sols et capte le carbone sans jamais s'épuiser : l'image même de l'engagement que nous voulons construire, saison après saison.</p>
  </div>
</section>
<section class="band band--canopee" data-stalk="Notre promesse">
  <div class="shell">
    <div class="section-head"><div><p class="kicker">Notre promesse</p><h2>Chaque création est pensée pour</h2></div><p>L'émotion naît à chaque bouchée, l'harmonie à chaque instant.</p></div>
    <ul class="pillars">
      <li><h3>Éveiller</h3><p>Les sens.</p></li><li><h3>Apaiser</h3><p>Les émotions.</p></li><li><h3>Nourrir</h3><p>Le corps et l'esprit.</p></li><li><h3>Soutenir</h3><p>Le bien-être durable.</p></li>
    </ul>
  </div>
</section>
<section class="band" data-stalk="Ambition">
  <div class="shell manifesto">
    <blockquote>Devenir un acteur majeur de la gastronomie holistique en Afrique.<cite>Notre ambition</cite></blockquote>
    <ul class="roots">
      <li><div><h3>Pour une Afrique plus verte</h3></div></li>
      <li><div><h3>Pour des communautés plus fortes</h3></div></li>
      <li><div><h3>Pour une alimentation plus consciente</h3></div></li>
      <li><div><h3>Pour un avenir plus lumineux</h3></div></li>
    </ul>
  </div>
</section>
{label_band()}
{cta("Partageons cette vision", "Producteurs, partenaires, curieux : parlons-en.", primary=("contact.html", "Nous contacter"))}
</main>
"""

def page_contact():
    phones = "".join(f'<a href="tel:{t}">{e(d)}</a>' for t, d in D.PHONES)
    return f"""<main id="main">
{page_hero("Parlons de votre prochaine table", "Commande, traiteur, formule holistique ou simple question : nous répondons rapidement, surtout sur WhatsApp.", "Contact")}
<section class="band" data-stalk="Nous joindre">
  <div class="shell contact">
    <div>
      <dl class="contact-list">
        <dt>WhatsApp</dt><dd><a href="{wa("Bonjour Graya Holistic, j'ai une question.")}">Écrire sur WhatsApp</a></dd>
        <dt>Téléphone</dt><dd>{phones}</dd>
        <dt>E-mail</dt><dd><a href="mailto:{D.EMAIL}">{e(D.EMAIL)}</a></dd>
        <dt>Cuisine</dt><dd>{e(D.AREA_LABEL)}, Côte d'Ivoire<br><small>Atelier sans salle : commandes en livraison uniquement</small></dd>
      </dl>
      {hours_dl()}
    </div>
    <form class="contact-form" data-contact novalidate>
      <h2 class="h3">Écrivez-nous</h2>
      <p>Votre message s'ouvre dans WhatsApp, prêt à envoyer.</p>
      <div class="field"><label for="c-name">Nom complet</label><input id="c-name" name="name" type="text" autocomplete="name" required></div>
      <div class="field"><label for="c-subject">Sujet</label><select id="c-subject" name="subject" required><option value="">Choisir</option><option>Commande ou livraison</option><option>Traiteur et événements</option><option>Cure ou formule holistique</option><option>Partenariat</option><option>Autre</option></select></div>
      <div class="field"><label for="c-msg">Message</label><textarea id="c-msg" name="message" rows="5" required></textarea></div>
      <p class="form-error" data-error role="alert" hidden></p>
      <button type="submit" class="btn btn--gold">{ICON['wa']}Envoyer sur WhatsApp</button>
    </form>
  </div>
</section>
<section class="band band--canopee" data-stalk="Zones">
  <div class="shell info">
    <div><p class="kicker">Zones de livraison</p><h2>Depuis Bingerville, vers tout le grand Abidjan</h2>{zones_ul()}</div>
    <div class="map"><iframe src="https://maps.google.com/maps?q=Bingerville%2C%20C%C3%B4te%20d%27Ivoire&z=12&output=embed" title="Carte : Bingerville et la zone de livraison" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
  </div>
</section>
{cta("Envie de passer commande ?", "La carte est à un clic.")}
</main>
"""

def page_faq():
    items = "".join(f'<details class="faq-item"><summary><h2 class="h3">{e(q)}</h2></summary><p>{e(a)}</p></details>' for q, a in D.FAQ)
    return f"""<main id="main">
{page_hero("Questions fréquentes", "Commande, livraison, horaires, traiteur : l'essentiel en quelques réponses.", "Questions fréquentes")}
<section class="band" data-stalk="Réponses">
  <div class="shell narrow faq">{items}</div>
</section>
{cta("Vous ne trouvez pas votre réponse ?", "Écrivez-nous, nous répondons rapidement.")}
</main>
"""

def page_404():
    return f"""<main id="main">
<section class="page-hero page-hero--404">
  <div class="page-hero-bg">{pic('bamboo-sunlit-path', '', folder='bamboo', w=1200, h=1800, lazy=False)}</div>
  <div class="shell">
    <p class="kicker">Erreur 404</p>
    <h1>Ce chemin ne mène nulle part</h1>
    <p class="lead">La page a peut-être été déplacée. Revenez à l'accueil ou allez directement à la carte.</p>
    <div class="actions mt-xl"><a href="index.html" class="btn btn--gold">Retour à l'accueil</a><a href="menu.html" class="btn btn--ghost">Voir la carte</a></div>
  </div>
</section>
</main>
"""


# ------------------------------------------------------------------ structured data
def menu_ld():
    return {"@context": "https://schema.org", "@type": "Menu", "name": "La carte Graya Holistic", "url": D.BASE_URL + "menu.html",
            "inLanguage": "fr", "hasMenuSection": [
                {"@type": "MenuSection", "name": s["title"], "hasMenuItem": [
                    {"@type": "MenuItem", "name": it["name"], "description": f'{it["sub"]}. {it["desc"]}',
                     **({"image": D.BASE_URL + f'assets/img/plats/{it["img"]}.jpg'} if it["img"] else {}),
                     "offers": ([{"@type": "Offer", "name": lbl, "price": p, "priceCurrency": "XOF"} for _, lbl, p in it["sizes"]]
                                if "sizes" in it else {"@type": "Offer", "price": it["price"], "priceCurrency": "XOF"})}
                    for it in s["items"]]} for s in D.MENU]}

def faq_ld():
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in D.FAQ]}

def service_ld():
    return {"@context": "https://schema.org", "@type": "Service", "serviceType": "Traiteur événementiel",
            "name": "Traiteur Graya Holistic", "provider": {"@id": D.BASE_URL + "#restaurant"},
            "areaServed": {"@type": "City", "name": "Abidjan"}, "url": D.BASE_URL + "traiteur.html",
            "description": "Menus sur mesure pour événements privés, professionnels et institutionnels, cuisinés à Bingerville et livrés dans le grand Abidjan."}


PAGES = [
    {"file": "index.html", "title": "Graya Holistic — Cuisine holistique consciente à Bingerville, Abidjan",
     "desc": "Cuisine holistique consciente cuisinée à Bingerville et livrée dans tout Abidjan : brochettes signature, soupes, jus thérapeutiques Nectar d'Eden, traiteur. Commande sur WhatsApp.",
     "body": page_index, "ld": [restaurant_ld()]},
    {"file": "menu.html", "title": "La carte & les prix — livraison à Abidjan | Graya Holistic",
     "desc": "La carte Graya Holistic : brochettes signature, poulet braisé au feu de bois, Kedjenou, soupe du pêcheur, attiéké, aloko, jus Nectar d'Eden. Prix en FCFA, commande en ligne.",
     "body": page_menu, "ld": [menu_ld(), crumbs_ld("La carte", "menu.html")]},
    {"file": "traiteur.html", "title": "Traiteur événementiel à Abidjan — devis en ligne | Graya Holistic",
     "desc": "Traiteur pour mariages, anniversaires, séminaires et réceptions à Abidjan : menus sur mesure, sains et généreux. Demandez votre devis en deux minutes.",
     "body": page_traiteur, "ld": [service_ld(), crumbs_ld("Traiteur", "traiteur.html")]},
    {"file": "notre-cuisine.html", "title": "Notre cuisine holistique : plats, jus & desserts | Graya Holistic",
     "desc": "Cuisine Holistique Consciente™ : des plats équilibrés, des jus bien-être Nectar d'Eden et des desserts sains, préparés avec des ingrédients locaux et de saison.",
     "body": page_cuisine, "ld": [crumbs_ld("Notre cuisine", "notre-cuisine.html")]},
    {"file": "services.html", "title": "Livraison, traiteur & cures à Abidjan | Graya Holistic",
     "desc": "Livraison express, traiteur événementiel et cures holistiques : les services de Graya Holistic, atelier culinaire à Bingerville.",
     "body": page_services, "ld": [crumbs_ld("Nos services", "services.html")]},
    {"file": "a-propos.html", "title": "Qui sommes-nous — cuisine consciente à Bingerville | Graya Holistic",
     "desc": "Graya Holistic® transforme l'alimentation en un acte de soin, de conscience et de dignité. Notre vision, notre mission et nos racines.",
     "body": page_apropos, "ld": [crumbs_ld("Qui sommes-nous", "a-propos.html")]},
    {"file": "engagement.html", "title": "Engagement éco-responsable, label ÉCO BMT™ | Graya Holistic",
     "desc": "Plantes et épices locales, producteurs ivoiriens, alimentation consciente : les engagements de Graya Holistic, labellisé ÉCO BMT™.",
     "body": page_engagement, "ld": [crumbs_ld("Engagement", "engagement.html")]},
    {"file": "contact.html", "title": "Contact & commande WhatsApp — Bingerville | Graya Holistic",
     "desc": "Contactez Graya Holistic à Bingerville : WhatsApp, téléphone, e-mail, horaires et zones de livraison dans le grand Abidjan.",
     "body": page_contact, "ld": [crumbs_ld("Contact", "contact.html")]},
    {"file": "faq.html", "title": "Questions fréquentes — commande & livraison | Graya Holistic",
     "desc": "Comment commander, zones et horaires de livraison, traiteur, jus Nectar d'Eden, label ÉCO BMT™ : les réponses aux questions fréquentes.",
     "body": page_faq, "ld": [faq_ld(), crumbs_ld("Questions fréquentes", "faq.html")]},
    {"file": "404.html", "title": "Page introuvable — Graya Holistic", "desc": "Cette page n'existe pas.",
     "body": page_404, "noindex": True},
]


def data_js():
    items = {}
    for s in D.MENU:
        for it in s["items"]:
            items[it["id"]] = {"name": it["name"], "cat": s["id"]}
    data = {"whatsapp": D.WHATSAPP, "zones": [{"name": z, "fee": f} for z, f in D.ZONES], "hours": D.HOURS, "dishes": items}
    return "/* Generated by tools/build.py from tools/site_data.py — do not edit by hand. */\nwindow.GRAYA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"


def main():
    for p in PAGES:
        active = p["file"]
        out = head(p) + header(active) + p["body"]() + footer()
        (ROOT / p["file"]).write_text(out, encoding="utf-8")
    (ROOT / "assets/js/data.js").write_text(data_js(), encoding="utf-8")
    urls = "".join(f"  <url><loc>{D.BASE_URL}{'' if p['file'] == 'index.html' else p['file']}</loc></url>\n" for p in PAGES if not p.get("noindex"))
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    print("built", len(PAGES), "pages")

if __name__ == "__main__":
    main()
