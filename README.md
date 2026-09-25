# Graya Holistic

Site de **Graya Holistic®** — Cuisine Holistique Consciente™, atelier culinaire et traiteur basé à **Bingerville** (Abidjan), livraison dans tout le grand Abidjan. Labellisé ÉCO BMT™.

Direction visuelle « Nuit de bambouseraie » : vert forêt profond, filets dorés, Bodoni Moda + Jost (polices hébergées dans `assets/fonts/`), reprise des cartes menu de la marque.

## Pages

| Fichier | Contenu |
|---|---|
| `index.html` | Accueil : logo en grand, racines, 4 plats phares, approche, traiteur, galerie, zones & horaires |
| `menu.html` | La carte en texte, filtres par catégorie, « Laisser le chef choisir », ajout au panier |
| `traiteur.html` | Traiteur événementiel + demande de devis guidée en 3 étapes (envoi WhatsApp) |
| `notre-cuisine.html` | Plats, boissons, desserts, galerie filtrable |
| `services.html` | Livraison, traiteur, cures & formules |
| `a-propos.html` | Qui sommes-nous |
| `engagement.html` | Engagements & label ÉCO BMT™ |
| `contact.html` | Coordonnées, horaires, formulaire (envoi WhatsApp), carte |
| `faq.html` | Questions fréquentes |
| `404.html` | Page d'erreur (liens ancrés avec `<base href="/GrayaHolistic/">`) |

## Fonctionnalités

- **Panier sur tout le site** : ajout depuis la carte ou l'accueil, quantités, zone de livraison avec frais, « dès que possible » ou créneau programmé dans les horaires d'ouverture, adresse, nom, note. Le récapitulatif part sur WhatsApp. Le panier est gardé dans le navigateur (`localStorage`).
- **Devis traiteur** en 3 étapes avec validation, récapitulatif et envoi WhatsApp.
- **Animations** : entrée du logo et du titre sur l'accueil, bambous qui ondulent, parallaxe des photos, photos qui se dévoilent vers le haut, transitions fondues entre pages, tige de bambou qui grandit au défilement (ordinateur) avec un nœud par section. Tout est coupé si « réduire les animations » est activé.
- **SEO local** : données structurées `Restaurant` (Bingerville), `Menu` (tous les plats et prix), `FAQPage`, `Service` (traiteur), fil d'Ariane ; titres et descriptions par page ; sitemap généré.

## Modifier le contenu

Le contenu qui change (carte, prix, zones et frais, horaires, téléphones, FAQ) est dans **`tools/site_data.py`**. Les pages sont générées par **`tools/build.py`** :

```bash
python3 tools/build.py
```

Cela réécrit les pages HTML, `assets/js/data.js` et `sitemap.xml`. On peut toujours modifier un HTML à la main, mais le prochain build l'écrasera : mieux vaut modifier `build.py` / `site_data.py`.

Autres scripts :
- `tools/logo_extract.py` : régénère les logos transparents (sans fond ni liseré blanc, texte éclairci pour fond sombre) depuis `assets/img/logo-source.png`. Nécessite Pillow, numpy, scipy.
- `tools/bamboo_svg.py` : régénère les illustrations de bambou `assets/img/deco/*.svg`.

Les photos des plats (`assets/img/plats/`) sont recadrées depuis les visuels de la carte d'origine (`assets/img/menu/`, conservés comme sources).

## Développement local

```bash
python3 -m http.server 8000
```

Puis `http://localhost:8000`. Pour tester la 404, servir le dossier parent et ouvrir `http://localhost:8000/GrayaHolistic/404.html`.

## Déploiement

GitHub Pages : `https://xtruck149.github.io/GrayaHolistic/`. Liens internes relatifs. Pour un nom de domaine propre, changer `BASE_URL` dans `tools/site_data.py`, relancer le build, et mettre à jour `robots.txt` et le `<base>` de la 404 dans `build.py`.

## À confirmer avec la cliente

- **Email et réseaux sociaux** : ceux affichés sont ceux de BMT Green Academy (`EMAIL`, `SOCIAL` dans `site_data.py`).
- **Frais de livraison par zone** : valeurs provisoires (`ZONES`).
- **Avis clients** : aucun avis réel n'est publié. Les ajouter (avec accord des clients) ou relier une fiche Google Business, levier n°1 du SEO local.
- Adresse précise à Bingerville si elle peut être publiée (améliore la fiche Google et les données structurées).
