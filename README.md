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
| `confidentialite.html` | Confidentialité : ce qui est gardé sur l'appareil, ce qui part sur WhatsApp, bouton pour tout effacer |
| `404.html` | Page d'erreur (liens ancrés avec `<base href="/GrayaHolistic/">`) |

## Fonctionnalités

- **Panier sur tout le site** : ajout depuis la carte ou l'accueil, quantités, zone de livraison avec frais, « dès que possible » ou créneau programmé dans les horaires d'ouverture, adresse, nom, note. Le récapitulatif part sur WhatsApp. Le panier est gardé dans le navigateur (`localStorage`).
- **Devis traiteur** en 3 étapes avec validation, récapitulatif et envoi WhatsApp.
- **Animations** : entrée du logo et du titre sur l'accueil, bambous qui ondulent, parallaxe des photos, photos qui se dévoilent vers le haut, transitions fondues entre pages, tige de bambou qui grandit au défilement (ordinateur) avec un nœud par section. Tout est coupé si « réduire les animations » est activé.
- **Ouvert / fermé** : pastille sur l'accueil et avertissement dans le panier hors horaires, calculés d'après `HOURS` en heure d'Abidjan.
- **Galerie dans le HTML** : générée au build depuis `assets/img/gallery/manifest.json` (tailles réelles des images, pas de saut de mise en page, indexable) ; le JavaScript ajoute seulement la visionneuse et les filtres.
- **Carte Google à la demande** : la page Contact ne contacte Google que si le visiteur clique sur « Afficher la carte ».
- **Panier fiable** : les prix d'un panier enregistré sont remis à jour depuis la carte actuelle ; la note pour la cuisine n'est plus perdue quand on change une quantité.
- **SEO local** : données structurées `Restaurant` (Bingerville), `Menu` (tous les plats et prix), `FAQPage`, `Service` (traiteur), fil d'Ariane ; titres et descriptions par page ; sitemap généré.

## Modifier le contenu

Le contenu qui change (carte, prix, zones et frais, horaires, téléphones, FAQ) est dans **`tools/site_data.py`**. Les pages sont générées par **`tools/build.py`** :

```bash
python3 tools/build.py
```

Cela réécrit les pages HTML, `assets/js/data.js` et `sitemap.xml`, et recalcule le numéro de version (`?v=`) du CSS et du JS d'après leur contenu : plus besoin de le changer à la main. Relancer le build après toute modification de `style.css` ou `main.js`. On peut toujours modifier un HTML à la main, mais le prochain build l'écrasera : mieux vaut modifier `build.py` / `site_data.py`.

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
- **Confidentialité** : la page ne cite pas d'identifiants légaux (RCCM, compte contribuable). À compléter, et à faire relire, si la marque en a.
- **`SOCIAL_CONFIRMED`** dans `site_data.py` : à passer à `True` quand l'email et les réseaux sont ceux de Graya Holistic ; les liens sont alors déclarés dans les données structurées.
- **Frais de livraison par zone** : valeurs provisoires (`ZONES`).
- **Avis clients** : aucun avis réel n'est publié. Les ajouter (avec accord des clients) ou relier une fiche Google Business, levier n°1 du SEO local.
- Adresse précise à Bingerville si elle peut être publiée (améliore la fiche Google et les données structurées).
