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
