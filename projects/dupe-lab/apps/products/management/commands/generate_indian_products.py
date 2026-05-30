"""
Management command: generate_indian_products
=============================================
Generates a large dataset of Indian skincare products with realistic
ingredient lists, prices in INR, and Indian brand names.

Usage:
    python manage.py generate_indian_products
    python manage.py generate_indian_products --count 5000
    python manage.py generate_indian_products --count 10000 --clear
"""
import random
from django.core.management.base import BaseCommand
from apps.products.models import Product

# ── Indian Brands ──────────────────────────────────────────────────────────────
BRANDS = {
    "Mamaearth": {
        "price_range": (299, 999),
        "style": "natural",
        "skin_focus": ["sensitive", "dry", "normal"],
    },
    "Minimalist": {
        "price_range": (399, 1099),
        "style": "actives",
        "skin_focus": ["oily", "combination", "normal"],
    },
    "Dot & Key": {
        "price_range": (395, 1295),
        "style": "natural",
        "skin_focus": ["dry", "normal", "sensitive"],
    },
    "Plum": {
        "price_range": (295, 995),
        "style": "natural",
        "skin_focus": ["oily", "combination", "sensitive"],
    },
    "Biotique": {
        "price_range": (149, 699),
        "style": "ayurvedic",
        "skin_focus": ["dry", "normal", "sensitive"],
    },
    "Himalaya": {
        "price_range": (99, 599),
        "style": "herbal",
        "skin_focus": ["sensitive", "oily", "normal"],
    },
    "Lakme": {
        "price_range": (199, 1499),
        "style": "mainstream",
        "skin_focus": ["normal", "combination", "oily"],
    },
    "Wow Skin Science": {
        "price_range": (299, 1299),
        "style": "natural",
        "skin_focus": ["dry", "normal", "sensitive"],
    },
    "Forest Essentials": {
        "price_range": (795, 4995),
        "style": "luxury_ayurvedic",
        "skin_focus": ["dry", "sensitive", "normal"],
    },
    "Kama Ayurveda": {
        "price_range": (595, 3995),
        "style": "luxury_ayurvedic",
        "skin_focus": ["dry", "sensitive", "normal"],
    },
    "mCaffeine": {
        "price_range": (299, 999),
        "style": "caffeine",
        "skin_focus": ["oily", "combination", "normal"],
    },
    "The Derma Co": {
        "price_range": (399, 1499),
        "style": "actives",
        "skin_focus": ["oily", "combination", "acne"],
    },
    "Pilgrim": {
        "price_range": (349, 1199),
        "style": "k-beauty",
        "skin_focus": ["dry", "sensitive", "normal"],
    },
    "St. Botanica": {
        "price_range": (449, 1599),
        "style": "natural",
        "skin_focus": ["dry", "normal", "combination"],
    },
    "Jovees": {
        "price_range": (150, 699),
        "style": "herbal",
        "skin_focus": ["sensitive", "dry", "normal"],
    },
    "Khadi Natural": {
        "price_range": (125, 595),
        "style": "ayurvedic",
        "skin_focus": ["sensitive", "dry", "normal"],
    },
    "VLCC": {
        "price_range": (149, 899),
        "style": "herbal",
        "skin_focus": ["oily", "combination", "normal"],
    },
    "Neutrogena India": {
        "price_range": (299, 1299),
        "style": "clinical",
        "skin_focus": ["oily", "combination", "sensitive"],
    },
    "Garnier India": {
        "price_range": (99, 799),
        "style": "mainstream",
        "skin_focus": ["oily", "combination", "normal"],
    },
    "Lotus Herbals": {
        "price_range": (175, 899),
        "style": "herbal",
        "skin_focus": ["sensitive", "dry", "normal"],
    },
    "Aqualogica": {
        "price_range": (349, 999),
        "style": "hydration",
        "skin_focus": ["dry", "combination", "normal"],
    },
    "Foxtale": {
        "price_range": (449, 1299),
        "style": "actives",
        "skin_focus": ["oily", "combination", "acne"],
    },
    "Deconstruct": {
        "price_range": (499, 1499),
        "style": "actives",
        "skin_focus": ["oily", "combination", "normal"],
    },
    "Suganda": {
        "price_range": (450, 1599),
        "style": "actives",
        "skin_focus": ["sensitive", "dry", "normal"],
    },
    "Earth Rhythm": {
        "price_range": (395, 1295),
        "style": "natural",
        "skin_focus": ["dry", "sensitive", "normal"],
    },
    "Re'equil": {
        "price_range": (399, 1699),
        "style": "clinical",
        "skin_focus": ["sensitive", "oily", "combination"],
    },
    "Cetaphil India": {
        "price_range": (349, 1299),
        "style": "clinical",
        "skin_focus": ["sensitive", "dry", "normal"],
    },
    "Ponds": {
        "price_range": (99, 599),
        "style": "mainstream",
        "skin_focus": ["normal", "combination", "dry"],
    },
    "Olay India": {
        "price_range": (299, 2499),
        "style": "anti_aging",
        "skin_focus": ["dry", "normal", "combination"],
    },
    "L'Oreal Paris India": {
        "price_range": (299, 1999),
        "style": "mainstream",
        "skin_focus": ["normal", "combination", "dry"],
    },
}

# ── Product Templates by Category ─────────────────────────────────────────────
PRODUCT_TEMPLATES = {
    "moisturizer": {
        "names": [
            "Daily Moisturizing Cream", "Hydrating Face Cream", "Skin Repair Moisturizer",
            "Nourishing Day Cream", "Intense Hydration Cream", "Oil-Free Moisturizer",
            "SPF Moisturizer", "Night Repair Cream", "Barrier Repair Moisturizer",
            "Ultra Light Moisturizer", "Deep Nourishment Cream", "Glow Boosting Moisturizer",
            "Ceramide Moisturizer", "Peptide Face Cream", "Brightening Day Cream",
            "Anti-Ageing Moisturizer", "Skin Brightening Cream", "Matte Moisturizer",
            "Gel Moisturizer", "Whipped Face Cream", "Shea Butter Cream",
            "Turmeric Glow Cream", "Saffron Brightening Cream", "Kumkumadi Moisturizer",
            "Aloe Vera Moisturizer", "Rose Hip Moisturizer", "Sandalwood Cream",
        ],
        "base_ingredients": [
            "Aqua", "Glycerin", "Cetearyl Alcohol", "Dimethicone", "Carbomer",
            "Sodium Hydroxide", "Disodium EDTA", "Phenoxyethanol",
        ],
        "style_ingredients": {
            "natural": ["Aloe Barbadensis Leaf Juice", "Rosa Canina Fruit Oil", "Chamomilla Recutita Extract", "Green Tea Extract", "Turmeric Extract", "Neem Extract"],
            "ayurvedic": ["Santalum Album Oil", "Curcuma Longa Extract", "Azadirachta Indica Leaf Extract", "Centella Asiatica Extract", "Vetiver Root Extract", "Ashwagandha Extract"],
            "luxury_ayurvedic": ["Saffron Extract", "Kumkumadi Oil", "24K Gold Leaf Extract", "Pearl Powder", "Rose Absolute", "Jasmine Extract", "Sandalwood Oil"],
            "actives": ["Niacinamide", "Hyaluronic Acid", "Retinol", "Ceramide NP", "Peptide Complex", "Alpha Arbutin"],
            "clinical": ["Ceramide NP", "Ceramide AP", "Hyaluronic Acid", "Niacinamide", "Panthenol", "Allantoin"],
            "mainstream": ["Niacinamide", "Vitamin E", "SPF Filters", "Glycerin", "Shea Butter"],
            "herbal": ["Neem Extract", "Tulsi Extract", "Aloe Vera", "Turmeric", "Triphala Extract"],
            "hydration": ["Hyaluronic Acid", "Sodium PCA", "Betaine", "Glycerin", "Aquaxyl"],
            "anti_aging": ["Retinol", "Peptide Complex", "Niacinamide", "Collagen", "Vitamin C"],
            "k-beauty": ["Centella Asiatica", "Snail Secretion Filtrate", "Galactomyces", "Bifida Ferment Lysate"],
            "caffeine": ["Caffeine", "Green Coffee Extract", "Hyaluronic Acid", "Niacinamide"],
        },
    },
    "serum": {
        "names": [
            "Vitamin C Brightening Serum", "Niacinamide 10% Serum", "Hyaluronic Acid Serum",
            "Retinol Anti-Ageing Serum", "Kojic Acid Dark Spot Serum", "AHA BHA Exfoliating Serum",
            "Salicylic Acid Serum", "Alpha Arbutin Serum", "Tranexamic Acid Serum",
            "Peptide Firming Serum", "Glow Serum", "Dark Spot Corrector Serum",
            "Glass Skin Serum", "Brightening Serum", "Anti-Pigmentation Serum",
            "Saffron Glow Serum", "Kumkumadi Elixir", "Rose Hip Face Serum",
            "Bakuchiol Serum", "Ceramide Serum", "Snail Repair Serum",
            "BHA Blackhead Serum", "Glycolic Acid Serum", "Lactic Acid Serum",
        ],
        "base_ingredients": [
            "Aqua", "Glycerin", "Propanediol", "Pentylene Glycol", "Carbomer",
            "Sodium Hydroxide", "Phenoxyethanol", "Ethylhexylglycerin",
        ],
        "style_ingredients": {
            "natural": ["Rosehip Oil", "Sea Buckthorn Extract", "Vitamin C", "Niacinamide", "Green Tea Extract"],
            "ayurvedic": ["Kumkumadi Oil", "Saffron Extract", "Turmeric Extract", "Manjistha Extract"],
            "luxury_ayurvedic": ["Kumkumadi Taila", "Saffron", "Rose Water", "Gold Bhasma", "Pearl Bhasma"],
            "actives": ["Niacinamide", "Zinc PCA", "Salicylic Acid", "Alpha Arbutin", "Tranexamic Acid", "Kojic Acid"],
            "clinical": ["Hyaluronic Acid", "Sodium Hyaluronate", "Niacinamide", "Panthenol", "Ceramide"],
            "mainstream": ["Vitamin C", "Niacinamide", "Glycerin", "Aloe Vera"],
            "herbal": ["Aloe Vera", "Cucumber Extract", "Licorice Extract", "Turmeric"],
            "hydration": ["Hyaluronic Acid", "Sodium PCA", "Trehalose", "Beta-Glucan"],
            "anti_aging": ["Retinol", "Bakuchiol", "Peptide Complex", "Vitamin C", "Ferulic Acid"],
            "k-beauty": ["Galactomyces Ferment Filtrate", "Centella Asiatica", "Snail Secretion Filtrate"],
            "caffeine": ["Caffeine", "Hyaluronic Acid", "Niacinamide", "Vitamin C"],
        },
    },
    "cleanser": {
        "names": [
            "Gentle Foaming Face Wash", "Oil Control Face Wash", "Hydrating Cleanser",
            "Brightening Face Wash", "Neem Face Wash", "Turmeric Face Wash",
            "Charcoal Face Wash", "AHA Face Wash", "Salicylic Acid Face Wash",
            "Rose Face Wash", "Aloe Vera Face Wash", "Anti-Acne Face Wash",
            "De-Tan Face Wash", "Ubtan Face Wash", "Papaya Face Wash",
            "Coffee Face Wash", "Vitamin C Face Wash", "Micellar Cleansing Water",
            "Cream Cleanser", "Gel to Foam Cleanser", "Milk Cleanser",
        ],
        "base_ingredients": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Glycerin", "Carbomer", "Sodium Chloride", "Citric Acid",
            "Sodium Benzoate", "Potassium Sorbate",
        ],
        "style_ingredients": {
            "natural": ["Aloe Barbadensis Leaf Juice", "Calendula Extract", "Chamomile Extract"],
            "ayurvedic": ["Neem Extract", "Tulsi Extract", "Haldi Extract", "Triphala"],
            "luxury_ayurvedic": ["Rose Water", "Sandalwood Extract", "Kesar Extract"],
            "actives": ["Salicylic Acid", "Niacinamide", "Tea Tree Oil", "Zinc PCA"],
            "clinical": ["Ceramide NP", "Niacinamide", "Panthenol", "Allantoin"],
            "mainstream": ["Glycerin", "Vitamin E", "Aloe Vera", "Green Tea"],
            "herbal": ["Neem", "Tulsi", "Haldi", "Chandan", "Multani Mitti"],
            "hydration": ["Glycerin", "Hyaluronic Acid", "Aloe Vera"],
            "anti_aging": ["Retinol", "Vitamin C", "Peptides"],
            "k-beauty": ["Centella Asiatica", "Green Tea", "Rice Water"],
            "caffeine": ["Caffeine", "Green Coffee", "Coconut Extract"],
        },
    },
    "sunscreen": {
        "names": [
            "SPF 50 Sunscreen", "Matte Sunscreen SPF 50+", "Tinted Sunscreen SPF 40",
            "Ultra Light SPF 60", "Invisible Sunscreen SPF 50", "Daily Sunscreen SPF 30",
            "Mineral Sunscreen SPF 50", "Aqua Fresh SPF 50+", "Gel Sunscreen SPF 50",
            "SPF 50 Sunscreen with Niacinamide", "De-Tan Sunscreen", "Anti-Pollution SPF 50",
            "Sunscreen Serum SPF 55", "Kids Sunscreen SPF 50", "Sports Sunscreen SPF 60",
            "Body Sunscreen SPF 50", "Face & Neck Sunscreen SPF 40",
        ],
        "base_ingredients": [
            "Aqua", "Ethylhexyl Methoxycinnamate", "Titanium Dioxide", "Zinc Oxide",
            "Octinoxate", "Homosalate", "Glycerin", "Dimethicone", "Carbomer",
            "Sodium Hydroxide",
        ],
        "style_ingredients": {
            "natural": ["Aloe Vera", "Green Tea Extract", "Vitamin E"],
            "ayurvedic": ["Turmeric Extract", "Neem Extract", "Sandalwood"],
            "luxury_ayurvedic": ["Saffron Extract", "Rose Extract", "Pearl Powder"],
            "actives": ["Niacinamide", "Hyaluronic Acid", "Vitamin C"],
            "clinical": ["Niacinamide", "Panthenol", "Allantoin"],
            "mainstream": ["Niacinamide", "Aloe Vera", "Vitamin E"],
            "herbal": ["Aloe Vera", "Green Tea", "Cucumber Extract"],
            "hydration": ["Hyaluronic Acid", "Glycerin", "Aloe Vera"],
            "anti_aging": ["Retinyl Palmitate", "Vitamin C", "Peptides"],
            "k-beauty": ["Centella Asiatica", "Galactomyces"],
            "caffeine": ["Caffeine", "Hyaluronic Acid"],
        },
    },
    "toner": {
        "names": [
            "AHA BHA Toner", "Niacinamide Toner", "Rose Water Toner",
            "Witch Hazel Toner", "Hyaluronic Acid Toner", "Glycolic Acid Toner",
            "Brightening Toner", "Pore Minimizing Toner", "Exfoliating Toner",
            "Hydrating Essence Toner", "Green Tea Toner", "Kojic Acid Toner",
            "Aloe Toner", "Rice Water Toner", "Centella Toner",
        ],
        "base_ingredients": [
            "Aqua", "Glycerin", "Butylene Glycol", "Niacinamide",
            "Sodium PCA", "Allantoin", "Phenoxyethanol",
        ],
        "style_ingredients": {
            "natural": ["Rose Water", "Aloe Vera Juice", "Cucumber Extract", "Green Tea"],
            "ayurvedic": ["Rose Water", "Vetiver Water", "Kewra Water", "Sandalwood Water"],
            "luxury_ayurvedic": ["Rose Absolute", "Jasmine Water", "Kesar Water"],
            "actives": ["Niacinamide", "AHA", "BHA", "PHA", "Salicylic Acid"],
            "clinical": ["Niacinamide", "Hyaluronic Acid", "Panthenol"],
            "mainstream": ["Niacinamide", "Glycerin", "Aloe Vera"],
            "herbal": ["Tulsi Water", "Neem Water", "Triphala Extract"],
            "hydration": ["Hyaluronic Acid", "Glycerin", "Beta-Glucan"],
            "anti_aging": ["Glycolic Acid", "Lactic Acid", "Peptides"],
            "k-beauty": ["Galactomyces", "Rice Ferment Filtrate", "Centella"],
            "caffeine": ["Caffeine", "Green Tea", "Hyaluronic Acid"],
        },
    },
    "mask": {
        "names": [
            "Kaolin Clay Mask", "Multani Mitti Face Pack", "Charcoal Peel-Off Mask",
            "Turmeric Face Pack", "De-Tan Face Pack", "Brightening Face Mask",
            "Hydrating Sheet Mask", "Anti-Acne Clay Mask", "Papaya Face Pack",
            "Ubtan Face Pack", "Rose Clay Mask", "Sleeping Mask",
            "AHA Overnight Mask", "Glow Mask", "Pigmentation Mask",
        ],
        "base_ingredients": [
            "Aqua", "Kaolin", "Bentonite", "Glycerin", "Xanthan Gum",
            "Titanium Dioxide", "Phenoxyethanol",
        ],
        "style_ingredients": {
            "natural": ["Papaya Extract", "Pineapple Extract", "Rose Hip", "Aloe Vera"],
            "ayurvedic": ["Multani Mitti", "Chandan Powder", "Haldi", "Neem Powder", "Ubtan"],
            "luxury_ayurvedic": ["Saffron", "Rose Absolute", "Kumkumadi", "Pearl Powder"],
            "actives": ["Salicylic Acid", "Niacinamide", "AHA", "Kaolin"],
            "clinical": ["Kaolin", "Niacinamide", "Allantoin"],
            "mainstream": ["Glycerin", "Aloe Vera", "Vitamin E"],
            "herbal": ["Multani Mitti", "Neem", "Tulsi", "Haldi"],
            "hydration": ["Hyaluronic Acid", "Aloe Vera", "Glycerin"],
            "anti_aging": ["Retinol", "Peptides", "Vitamin C"],
            "k-beauty": ["Centella Asiatica", "Green Tea", "Rice Extract"],
            "caffeine": ["Caffeine", "Coconut Oil", "Green Coffee"],
        },
    },
    "eye_cream": {
        "names": [
            "Under Eye Cream", "Dark Circle Corrector", "Eye Depuffing Gel",
            "Anti-Ageing Eye Cream", "Brightening Eye Serum", "Eye Repair Cream",
            "Vitamin K Eye Cream", "Peptide Eye Cream", "Caffeine Eye Gel",
        ],
        "base_ingredients": [
            "Aqua", "Glycerin", "Dimethicone", "Niacinamide", "Carbomer",
            "Sodium Hydroxide", "Phenoxyethanol",
        ],
        "style_ingredients": {
            "natural": ["Rose Hip Oil", "Almond Oil", "Vitamin E"],
            "ayurvedic": ["Almond Oil", "Saffron Extract", "Rose Extract"],
            "luxury_ayurvedic": ["Kumkumadi Oil", "Saffron", "24K Gold"],
            "actives": ["Caffeine", "Vitamin K", "Niacinamide", "Peptides"],
            "clinical": ["Ceramide", "Niacinamide", "Hyaluronic Acid"],
            "mainstream": ["Vitamin E", "Glycerin", "Retinol"],
            "herbal": ["Almond Oil", "Cucumber Extract", "Aloe Vera"],
            "hydration": ["Hyaluronic Acid", "Glycerin", "Sodium PCA"],
            "anti_aging": ["Retinol", "Peptides", "Vitamin C"],
            "k-beauty": ["Galactomyces", "Snail Extract", "Centella"],
            "caffeine": ["Caffeine", "Green Tea", "Hyaluronic Acid"],
        },
    },
    "treatment": {
        "names": [
            "Anti-Acne Spot Treatment", "Salicylic Acid Treatment", "Kojic Acid Treatment",
            "Niacinamide Treatment", "Retinol Treatment", "AHA Exfoliant",
            "BHA Blackhead Treatment", "Hyperpigmentation Treatment",
            "Dark Spot Corrector", "Acne Scar Treatment", "Vitamin C Treatment",
            "Alpha Arbutin Treatment", "Tranexamic Acid Treatment",
        ],
        "base_ingredients": [
            "Aqua", "Glycerin", "Propanediol", "Niacinamide",
            "Sodium Hydroxide", "Phenoxyethanol",
        ],
        "style_ingredients": {
            "natural": ["Tea Tree Oil", "Witch Hazel", "Aloe Vera"],
            "ayurvedic": ["Neem Oil", "Turmeric Extract", "Manjistha"],
            "luxury_ayurvedic": ["Saffron", "Kumkumadi", "Rose"],
            "actives": ["Salicylic Acid", "Niacinamide", "Alpha Arbutin", "Kojic Acid", "Tranexamic Acid"],
            "clinical": ["Salicylic Acid", "Niacinamide", "Ceramide"],
            "mainstream": ["Salicylic Acid", "Benzoyl Peroxide", "Niacinamide"],
            "herbal": ["Tea Tree", "Neem", "Tulsi Extract"],
            "hydration": ["Hyaluronic Acid", "Aloe Vera"],
            "anti_aging": ["Retinol", "Glycolic Acid", "Vitamin C"],
            "k-beauty": ["Centella Asiatica", "Tea Tree", "BHA"],
            "caffeine": ["Caffeine", "Niacinamide"],
        },
    },
}

SKIN_TYPE_COMBOS = [
    {"skin_dry": True,  "skin_oily": False, "skin_normal": False, "skin_combination": False, "skin_sensitive": False},
    {"skin_dry": False, "skin_oily": True,  "skin_normal": False, "skin_combination": False, "skin_sensitive": False},
    {"skin_dry": False, "skin_oily": False, "skin_normal": True,  "skin_combination": False, "skin_sensitive": False},
    {"skin_dry": False, "skin_oily": False, "skin_normal": False, "skin_combination": True,  "skin_sensitive": False},
    {"skin_dry": True,  "skin_oily": False, "skin_normal": False, "skin_combination": False, "skin_sensitive": True},
    {"skin_dry": False, "skin_oily": True,  "skin_normal": False, "skin_combination": True,  "skin_sensitive": False},
    {"skin_dry": False, "skin_oily": False, "skin_normal": True,  "skin_combination": False, "skin_sensitive": True},
    {"skin_dry": True,  "skin_oily": False, "skin_normal": True,  "skin_combination": False, "skin_sensitive": False},
    {"skin_dry": False, "skin_oily": True,  "skin_normal": False, "skin_combination": False, "skin_sensitive": True},
    {"skin_dry": True,  "skin_oily": False, "skin_normal": True,  "skin_combination": False, "skin_sensitive": True},
]


def build_ingredients(category: str, style: str) -> str:
    template = PRODUCT_TEMPLATES[category]
    base = list(template["base_ingredients"])
    style_ings = template["style_ingredients"].get(style, template["style_ingredients"]["natural"])

    # Pick a random subset of style ingredients
    n_style = random.randint(1, max(1, min(7, len(style_ings))))
    chosen_style = random.sample(style_ings, n_style)

    # Optional extras
    extras = [
        "Sodium Hyaluronate", "Tocopherol", "Panthenol", "Allantoin",
        "Xanthan Gum", "Citric Acid", "Sodium Citrate", "Ethylhexylglycerin",
        "Caprylyl Glycol", "Disodium EDTA", "Potassium Sorbate",
    ]
    n_extra = random.randint(2, 5)
    chosen_extra = random.sample(extras, n_extra)

    all_ings = base + chosen_style + chosen_extra
    # Shuffle except first 3 (base stay at top like real INCI lists)
    first_three = all_ings[:3]
    rest = all_ings[3:]
    random.shuffle(rest)
    return ", ".join(first_three + rest)


class Command(BaseCommand):
    help = "Generate Indian skincare product dataset"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):
        count = options["count"]

        if options["clear"]:
            deleted = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing products."))

        self.stdout.write(f"Generating {count} Indian skincare products...")

        categories = list(PRODUCT_TEMPLATES.keys())
        brand_names = list(BRANDS.keys())

        batch = []
        created = 0
        batch_size = 500

        # Track used name combos to avoid exact duplicates
        used = set()

        attempts = 0
        while created < count and attempts < count * 3:
            attempts += 1

            brand_name = random.choice(brand_names)
            brand_info = BRANDS[brand_name]
            category = random.choice(categories)
            template = PRODUCT_TEMPLATES[category]

            product_name = random.choice(template["names"])

            # Add variant suffix to create variety
            variants = [
                "", " - 30ml", " - 50ml", " - 100ml", " - 150ml",
                " (Oily Skin)", " (Dry Skin)", " (Sensitive Skin)",
                " with SPF", " Advanced", " Pro", " Original",
                " Lite", " Night", " Day", " Intensive",
            ]
            product_name += random.choice(variants)

            key = (brand_name, product_name)
            if key in used:
                continue
            used.add(key)

            price = round(random.uniform(*brand_info["price_range"]), 2)
            rank = round(random.uniform(3.2, 4.9), 1)
            ingredients = build_ingredients(category, brand_info["style"])
            skin_types = random.choice(SKIN_TYPE_COMBOS)

            # Indian-specific flags
            style = brand_info["style"]
            is_ayurvedic = style in ("ayurvedic", "luxury_ayurvedic", "herbal")
            indian_brands = {
                "Mamaearth", "Minimalist", "Dot & Key", "Plum", "Biotique",
                "Himalaya", "Wow Skin Science", "Forest Essentials", "Kama Ayurveda",
                "mCaffeine", "The Derma Co", "Pilgrim", "Jovees", "Khadi Natural",
                "VLCC", "Lotus Herbals", "Aqualogica", "Foxtale", "Deconstruct",
                "Suganda", "Earth Rhythm", "Re'equil", "St. Botanica",
            }
            made_in_india = brand_name in indian_brands

            batch.append(Product(
                brand=brand_name,
                name=product_name,
                category=category,
                price=price,
                rank=rank,
                ingredients=ingredients,
                made_in_india=made_in_india,
                is_ayurvedic=is_ayurvedic,
                currency='INR',
                **skin_types,
            ))
            created += 1

            if len(batch) >= batch_size:
                # Generate slugs before bulk create
                for p in batch:
                    from django.utils.text import slugify
                    import uuid
                    p.slug = slugify(f"{p.brand}-{p.name}-{uuid.uuid4().hex[:6]}")
                Product.objects.bulk_create(batch, ignore_conflicts=True)
                self.stdout.write(f"  Created {created}/{count}...")
                batch = []

        if batch:
            for p in batch:
                from django.utils.text import slugify
                import uuid
                p.slug = slugify(f"{p.brand}-{p.name}-{uuid.uuid4().hex[:6]}")
            Product.objects.bulk_create(batch, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Generated {created} Indian skincare products."
        ))
        self.stdout.write(
            "Next: run 'python manage.py build_similarity_cache' to compute similarities."
        )