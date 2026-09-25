"""Graya Holistic — single source of truth for the site's content that changes:
menu, prices, delivery zones, hours, contact details.

After editing this file run:  python3 tools/build.py
(it rewrites the HTML pages and assets/js/data.js)."""

BASE_URL = "https://xtruck149.github.io/GrayaHolistic/"
CITY = "Bingerville"          # where the kitchen is
REGION = "Abidjan"
AREA_LABEL = "Bingerville, Abidjan"
WHATSAPP = "2250101736812"
PHONES = [("+2250101736812", "01\u00a001\u00a073\u00a068\u00a012"), ("+2250777776200", "07\u00a077\u00a077\u00a062\u00a000")]
# TODO client: this email and the social links below belong to BMT Green Academy.
EMAIL = "bmtgreenacademy@gmail.com"
SOCIAL = {"Facebook": "https://facebook.com/bmtgreenacademy", "Instagram": "https://instagram.com/bmtgreenacademy"}

# Opening hours — weekday numbers follow JavaScript (0 = Sunday).
HOURS = [
    {"label": "Lundi – Samedi", "days": [1, 2, 3, 4, 5, 6], "opens": "11:00", "closes": "21:30"},
    {"label": "Dimanche", "days": [0], "opens": "12:00", "closes": "20:00"},
]

# Delivery fee by zone, from the kitchen in Bingerville.
# TODO client: placeholder figures, confirm before launch.
ZONES = [
    ("Bingerville", 500), ("Riviera", 1000), ("Cocody", 1500), ("Plateau", 2000),
    ("Marcory", 2000), ("Treichville", 2000), ("Zone 4", 2000), ("Grand-Bassam", 2500),
    ("Yopougon", 3000),
]

# The menu. `img` is a file stem in assets/img/plats/ (webp + jpg), or None.
# `sizes` replaces `price` for drinks sold by the glass or the bottle.
JUICE_SIZES = [("verre", "Verre", 2000), ("bouteille", "Bouteille", 5000)]
MENU = [
    {"id": "brochettes", "title": "Brochettes signature", "intro": "Chacune porte un nom et une histoire.", "items": [
        {"id": "francois", "name": "François", "sub": "L'Exotique Élégance", "desc": "2 brochettes de poulet tendre, légumes parfumés, persil, ail et poivre gris.", "price": 3000, "img": "brochette-francois"},
        {"id": "kaikai", "name": "Kaikai", "sub": "Bangkok Raffiné", "desc": "2 saucisses de poulet marinées, légumes croquants, touche asiatique subtile.", "price": 3000, "img": "brochette-kaikai"},
        {"id": "intrigue", "name": "Intrigue", "sub": "Crémeuse Intensité", "desc": "2 brochettes de gésiers fondants, herbes locales et notes réconfortantes.", "price": 4000, "img": "brochette-intrigue"},
        {"id": "rivage", "name": "Rivage Méditerranéen", "sub": "Le bœuf du Sud", "desc": "Filet de bœuf, poivrons, courgettes, épices douces inspirées du Sud.", "price": 5000, "img": "brochette-rivage-mediterraneen"},
        {"id": "gabriella", "name": "Gabriella", "sub": "Parfum d'Ailleurs", "desc": "Porc savoureux, graines torréfiées, épices chaudes et herbes aromatiques.", "price": 3000, "img": None},
        {"id": "nerree", "name": "Nerrée", "sub": "Perle des Lagunes", "desc": "Brochettes de crevettes grillées, herbes fines et sauce légère.", "price": 5000, "img": None},
    ]},
    {"id": "feu-de-bois", "title": "Au feu de bois", "intro": "Cuisson lente, marinades aux épices traditionnelles.", "items": [
        {"id": "braise", "name": "Le Braisé des Origines", "sub": "Demi-poulet", "desc": "Poulet braisé au feu de bois, mariné aux épices traditionnelles, cuisson lente et consciente.", "price": 5000, "img": None},
        {"id": "poisson-graya", "name": "Le Poisson Graya", "sub": "Saveurs de la lagune", "desc": "Poisson frais légèrement frit puis braisé, aux oignons, tomates et épices douces.", "price": 4000, "img": "poisson-graya"},
    ]},
    {"id": "soupes", "title": "Soupes & émotions", "intro": "Des bouillons qui réconfortent.", "items": [
        {"id": "soupe-pecheur", "name": "La Soupe du Pêcheur", "sub": "Réconfort ancestral", "desc": "Carpe fraîche, écrevisses, aubergines, gombo et épices lagunaires.", "price": 5000, "img": "soupe-du-pecheur"},
        {"id": "kedjenou", "name": "Kedjenou", "sub": "La Légendaire", "desc": "Poulet mijoté à l'ivoirienne, légumes et parfums authentiques.", "price": 3000, "img": "soupe-kedjenou"},
    ]},
    {"id": "accompagnements", "title": "Accompagnements", "intro": "Pour compléter votre assiette.", "items": [
        {"id": "ebrie", "name": "L'Ebrié", "sub": "Attiéké", "desc": "La semoule de manioc, fraîche et légère.", "price": 1000, "img": "accomp-attieke-ebrie"},
        {"id": "baoule", "name": "La Baoulé", "sub": "Aloko", "desc": "Bananes plantain mûres, caramélisées.", "price": 1000, "img": "accomp-aloko-baoule"},
        {"id": "bondoukouenne", "name": "La Bondoukouenne", "sub": "Igname", "desc": "Frite ou bouillie, selon votre envie.", "price": 1000, "img": "accomp-igname-bondoukouenne"},
        {"id": "belge", "name": "La Belge", "sub": "Frites", "desc": "Frites de pommes de terre.", "price": 1000, "img": "accomp-frites-belge"},
        {"id": "francaise", "name": "La Française", "sub": "Gratin dauphinois", "desc": "Une portion généreuse.", "price": 2000, "img": "accomp-gratin-francaise"},
    ]},
    {"id": "jus", "title": "Jus Nectar d'Eden", "intro": "Des jus naturels pensés comme des remèdes. Au verre ou en bouteille.", "items": [
        {"id": "fmn", "name": "FMN", "sub": "Force, Miel & Nature", "desc": "Cocktail de fruits, gingembre, goyave, miel et cannelle. Énergétique et revitalisant.", "sizes": JUICE_SIZES, "img": "jus-fmn"},
        {"id": "hibiscus", "name": "Jus d'Hibiscus", "sub": "Passion, vanille, menthe", "desc": "Une explosion de fraîcheur, 100 % naturelle.", "sizes": JUICE_SIZES, "img": "jus-hibiscus"},
        {"id": "deboukei", "name": "Deboukeï", "sub": "Suave & énergétique", "desc": "Pamplemousse, orange, abricot.", "sizes": JUICE_SIZES, "img": None},
        {"id": "evasion", "name": "Évasion", "sub": "Fraîcheur & légèreté", "desc": "Cocktail de fruits frais.", "sizes": JUICE_SIZES, "img": None},
    ]},
    {"id": "the", "title": "Thé digestif", "intro": "Une infusion pour finir en douceur.", "items": [
        {"id": "consolateur", "name": "Le Consolateur", "sub": "Thé thérapeutique", "desc": "Infusion douce et digestive, qui apaise l'estomac et rééquilibre le corps.", "price": 500, "img": None},
    ]},
]
# Shown on the home page.
SIGNATURE = ["kedjenou", "soupe-pecheur", "rivage", "baoule"]

FAQ = [
    ("Comment passer commande ?",
     "Depuis la carte : ajoutez vos plats au panier, choisissez votre zone de livraison et l'heure, puis envoyez la commande sur WhatsApp. "
     "Vous pouvez aussi nous écrire directement sur WhatsApp au 01\u00a001\u00a073\u00a068\u00a012."),
    ("Dans quelles zones livrez-vous ?",
     "Notre cuisine est à Bingerville. Nous livrons à Bingerville, Riviera, Cocody, Plateau, Marcory, Treichville, Zone 4, Grand-Bassam et Yopougon. "
     "Les frais dépendent de la distance et s'affichent dans le panier. Pour une autre zone, précisez-la : nous confirmons sur WhatsApp."),
    ("Quels sont vos horaires ?",
     "Du lundi au samedi de 11 h à 21 h 30, et le dimanche de 12 h à 20 h. Vous pouvez aussi programmer une commande pour plus tard depuis le panier."),
    ("Peut-on manger sur place ?",
     "Graya Holistic est un atelier culinaire virtuel : il n'y a pas de salle. Nos plats sont préparés à la commande et livrés chez vous, au bureau ou sur votre lieu d'événement."),
    ("Qu'est-ce que la cuisine holistique consciente ?",
     "Une cuisine qui nourrit le corps, apaise l'esprit et élève l'âme : des savoirs culinaires africains, des plantes et épices locales choisies pour leurs vertus, "
     "et une attention au bien-être à chaque étape, de la cuisson à l'assiette."),
    ("Comment réserver le traiteur pour un événement ?",
     "Remplissez la demande de devis sur la page Traiteur : date, nombre d'invités, type de service et vos préférences. "
     "Elle part sur WhatsApp et nous revenons vers vous avec une proposition de menu."),
    ("Que sont les jus Nectar d'Eden ?",
     "Nos jus naturels thérapeutiques, préparés à partir de fruits, plantes et épices : FMN, Hibiscus, Deboukeï et Évasion. "
     "Ils sont proposés au verre (2 000 FCFA) ou en bouteille (5 000 FCFA)."),
    ("Que signifie le label ÉCO BMT™ ?",
     "C'est un label de restauration responsable autour de trois axes : éducation et design, santé, durabilité. "
     "Il reconnaît notre engagement pour les produits locaux et une alimentation saine."),
]
