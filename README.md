# Graya Holistic

Site vitrine statique de **Graya Holistic®** — Cuisine Holistique Consciente™, restaurant, traiteur et événements à Abidjan, Côte d'Ivoire. Labellisé ÉCO BMT™.

Forké de la structure et du système de design de [BMT Green Academy](https://github.com/Xtruck149/bmtacademy) et ré-habillé pour un thème restaurant/gastronomie consciente (palette olive/or, typographie Playfair Display + Inter).

## Structure

```
index.html            Accueil
a-propos.html          Qui sommes-nous — vision, mission, ambition
notre-cuisine.html     Cuisine Holistique Consciente™ — plats, boissons, desserts
services.html          Nos espaces & services — restaurant, traiteur, événements, livraison, réceptions
engagement.html        Engagement & responsabilité — label ÉCO BMT™
contact.html           Contact & formulaire
404.html               Page d'erreur
assets/css/style.css   Feuille de style unique (design system partagé avec BMT, palette différente)
assets/js/main.js      Comportements JS (menu, scroll, animations, accordéons)
assets/img/            Logo et déclinaisons (favicons, PWA, og-image), générés depuis le logo fourni
```

Site 100 % HTML/CSS/JS statique, sans dépendances ni étape de build.

## Origine du contenu

Le texte du site a été extrait de maquettes visuelles (Canva) fournies par le client — ce ne sont pas des pages web fonctionnelles, seulement des visuels contenant le message de marque. Le logo (`assets/img/logo-source.png`) a été fourni comme fichier image et décliné en plusieurs formats (mark carré, lockup complet, favicons, icônes PWA, image de partage social) via un script Python/Pillow.

**Point à vérifier avec le client** : le téléphone et l'email de contact affichés dans les maquettes sont identiques à ceux de BMT Green Academy (marque sœur, labellisée ÉCO BMT). Ils ont été repris tels quels — à confirmer ou remplacer par des coordonnées propres à Graya Holistic si nécessaire.

## Développement local

```bash
python -m http.server 8000
```

Puis visiter `http://localhost:8000`.

## Déploiement

Prévu pour GitHub Pages à l'adresse `https://xtruck149.github.io/GrayaHolistic/`. Tous les liens internes sont relatifs pour rester compatibles avec ce sous-chemin.

## Audit du 25/09/2026 — ce qui a été corrigé

Mesures Lighthouse mobile (perf / accessibilité), avant → après :

| Page | Perf | A11y | LCP |
|---|---|---|---|
| Accueil | 67 → 79 | 95 → 100 | 9,4 s → 4,3 s |
| Menu | 70 → 87 | 94 → 100 | 6,0 s → 3,3 s |
| Contact | 76 → 92 | 95 → 100 | 5,1 s → 2,8 s |
| Qui sommes-nous | 76 → 92 | 94 → 100 | 5,2 s → 2,6 s |
| Engagement | 82 → 94 | 94 → 100 | 4,1 s → 2,6 s |

- **Performance** : Google Fonts chargées via `<link>` + `preconnect` (plus d'`@import` bloquant dans le CSS) ; logos servis en WebP redimensionné (412 Ko → 41 Ko, 162 Ko → 13 Ko) ; photo hero en `fetchpriority="high"` et conservée comme première diapositive du carrousel (elle était remplacée au chargement) ; images sous la ligne de flottaison en `loading="lazy"` avec dimensions intrinsèques.
- **Accessibilité** : hiérarchie des titres corrigée (h4/h5 → h2/h3 avec classes `.h4`/`.h5` pour garder le rendu) ; nom accessible sur le lien logo ; fil d'Ariane en `<nav aria-label>` + `aria-current` ; `nav` principale étiquetée ; boutons typés ; contraste du « 404 ».
- **Robustesse** : le contenu animé au scroll n'est plus masqué si JavaScript ne s'exécute pas (classe `.js` posée dans le `<head>`).
- **SEO** : titres de pages intérieures plus descriptifs, JSON-LD `BreadcrumbList`, `lastmod` dans le sitemap, `<base>` sur la 404 pour que ses liens marchent à n'importe quelle profondeur d'URL.
- **Ménage** : suppression d'un doublon (`WhatsApp Image ….jpeg` = `eco-bmt-badge.jpg`) et de `logo-512.png` (identique à `icon-512.png`).

Note : la 404 contient `<base href="/GrayaHolistic/">` — en local, la tester via `http://localhost:8000/GrayaHolistic/404.html` en servant le dossier parent.

### Points à trancher avec le client (non modifiés)

- Email, Facebook et Instagram affichés (et dans le JSON-LD `sameAs`) sont ceux de **BMT Green Academy**, pas de Graya Holistic.
- Frais de livraison par zone dans `main.js` marqués « placeholder ».
- Le menu affiche la plupart des plats et prix **dans les images** : lisible par les lecteurs d'écran via `alt`, mais invisible pour Google en texte. Les passer en texte HTML (comme Gabriella/Nerrée) améliorerait le référencement local.
- Eyebrow du menu « Cuisine Quantique » alors que la marque dit partout « Cuisine Holistique Consciente™ ».
- Pas d'adresse précise ni de fiche Google Business liée : c'est le levier n°1 pour le SEO local à Abidjan.
