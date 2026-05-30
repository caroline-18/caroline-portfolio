"""
Management command: seed_ayurvedic_ingredients
===============================================
Seeds the Ingredient table with Ayurvedic and Indian-specific
ingredients with descriptions, benefits, and safety info.

Usage:
    python manage.py seed_ayurvedic_ingredients
"""
from django.core.management.base import BaseCommand
from apps.ingredients.models import Ingredient

AYURVEDIC_INGREDIENTS = [
    {
        'name': 'Kumkumadi Oil',
        'inci_name': 'Crocus Sativus (Saffron) & Sesame Oil Blend',
        'description': 'A legendary Ayurvedic facial oil from the Ashtanga Hridayam, made by infusing saffron and 16 other herbs in sesame oil base. Used in Indian skincare for centuries.',
        'benefits': 'Brightens skin tone, reduces hyperpigmentation and dark spots, improves complexion, anti-aging, reduces blemishes. The saffron content makes it one of the most potent natural brighteners.',
        'side_effects': 'Rich oil — may not suit very oily or acne-prone skin. Patch test recommended. Can stain clothing.',
        'category': 'oil', 'risk_level': 'safe',
        'good_for_dry': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Turmeric Extract',
        'inci_name': 'Curcuma Longa Root Extract',
        'description': 'Derived from the turmeric rhizome, a staple of Indian cooking and Ayurveda. Active compound curcumin has powerful anti-inflammatory and antioxidant properties.',
        'benefits': 'Anti-inflammatory, brightens skin, reduces hyperpigmentation, antioxidant protection, traditional wound healing, reduces acne scarring.',
        'side_effects': 'Can cause yellow staining. Very high concentrations may irritate sensitive skin. Photosensitising in isolated curcumin form.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_dry': True, 'good_for_oily': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Neem Extract',
        'inci_name': 'Azadirachta Indica Leaf Extract',
        'description': 'From the neem tree, known as the "village pharmacy" in India. One of the most versatile plants in Ayurveda with powerful antibacterial and antifungal properties.',
        'benefits': 'Strong antibacterial and antifungal, treats acne and breakouts, reduces inflammation, soothes irritation, controls dandruff, purifies skin.',
        'side_effects': 'Strong smell. May cause allergic reactions in some individuals. Avoid during pregnancy in high doses.',
        'category': 'botanical', 'risk_level': 'low',
        'good_for_oily': True,
    },
    {
        'name': 'Sandalwood Oil',
        'inci_name': 'Santalum Album Oil',
        'description': 'Steam-distilled oil from the heartwood of the Indian sandalwood tree. One of the most precious and expensive botanical oils in the world, used in Ayurveda for over 4,000 years.',
        'benefits': 'Anti-inflammatory, soothes irritated skin, antimicrobial, reduces scars and blemishes, cooling effect on skin, pleasant fragrance, anti-aging.',
        'side_effects': 'Expensive ingredient — often adulterated. Rarely causes allergic reactions. Avoid if allergic to tree nuts.',
        'category': 'oil', 'risk_level': 'safe',
        'good_for_dry': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Saffron Extract',
        'inci_name': 'Crocus Sativus Stigma Extract',
        'description': 'Extracted from the stigmas of the saffron flower. One of the world\'s most expensive spices, used in Indian skincare as a premium brightening agent.',
        'benefits': 'Powerful skin brightener, reduces melanin production, antioxidant, anti-inflammatory, improves uneven skin tone, traditional glow-enhancing ingredient.',
        'side_effects': 'Very well tolerated topically. Extremely expensive — products claiming high saffron content are often adulterated.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_dry': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Ashwagandha Extract',
        'inci_name': 'Withania Somnifera Root Extract',
        'description': 'From one of Ayurveda\'s most revered adaptogenic herbs. Withanolides are the key active compounds with anti-stress and anti-aging properties.',
        'benefits': 'Anti-aging, reduces stress-induced skin damage, antioxidant, improves skin elasticity, reduces cortisol-related skin breakdown, brightening.',
        'side_effects': 'Generally well tolerated topically. Some individuals may experience mild irritation.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_dry': True,
    },
    {
        'name': 'Manjistha Extract',
        'inci_name': 'Rubia Cordifolia Root Extract',
        'description': 'A bright red Ayurvedic herb known as Indian Madder. One of the best blood-purifying herbs in Ayurveda, used extensively for skin brightening.',
        'benefits': 'Reduces pigmentation and dark spots, brightens skin, anti-inflammatory, detoxifying, traditional treatment for hyperpigmentation and melasma.',
        'side_effects': 'Generally safe topically. Can cause staining due to its red color.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_sensitive': True,
    },
    {
        'name': 'Vetiver Root Extract',
        'inci_name': 'Vetiveria Zizanoides Root Extract',
        'description': 'From the roots of the khus grass, widely grown in India. Used in Ayurveda for its cooling, purifying, and complexion-evening properties.',
        'benefits': 'Cooling and soothing, reduces skin irritation, tightens pores, antiseptic, anti-aging properties, traditionally used for sun-damaged skin.',
        'side_effects': 'Very well tolerated. Rarely causes reactions.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_oily': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Multani Mitti',
        'inci_name': 'Fuller\'s Earth / Calcium Bentonite',
        'description': 'A naturally occurring clay mineral found abundantly in Pakistan and India. One of the most widely used traditional beauty ingredients on the subcontinent.',
        'benefits': 'Deep cleanses pores, absorbs excess oil, removes impurities and dead skin cells, brightens skin, traditional de-tan treatment, reduces oiliness.',
        'side_effects': 'Can be very drying — over-use strips natural oils. Not suitable for dry or sensitive skin without moisturizer. Limit to 1-2x per week.',
        'category': 'other', 'risk_level': 'low',
        'good_for_oily': True,
    },
    {
        'name': 'Ubtan',
        'inci_name': 'Herbal Powder Blend (Chickpea, Turmeric, Sandalwood)',
        'description': 'A traditional Indian bridal skincare preparation made from a blend of chickpea flour, turmeric, sandalwood, and other herbs. Used for centuries before weddings.',
        'benefits': 'Natural exfoliation, brightens and evens skin tone, removes tan, cleanses skin gently, traditional de-tanning remedy, improves complexion.',
        'side_effects': 'Very gentle. Chickpea flour may cause reactions in those with legume allergies.',
        'category': 'other', 'risk_level': 'safe',
        'good_for_sensitive': True,
    },
    {
        'name': 'Triphala Extract',
        'inci_name': 'Emblica Officinalis, Terminalia Chebula, Terminalia Bellirica Extract',
        'description': 'A classical Ayurvedic formulation of three fruits: Amalaki (Indian gooseberry), Haritaki, and Bibhitaki. One of the most important Rasayana (rejuvenating) herbs.',
        'benefits': 'Powerful antioxidant (highest ORAC value of any botanical), brightening, anti-aging, reduces free radical damage, supports skin renewal, anti-inflammatory.',
        'side_effects': 'Extremely well tolerated topically. Very safe for all skin types.',
        'category': 'antioxidant', 'risk_level': 'safe',
        'good_for_dry': True, 'good_for_oily': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Tulsi Extract',
        'inci_name': 'Ocimum Sanctum Leaf Extract',
        'description': 'From holy basil, one of the most sacred plants in Hindu tradition. Widely used in Ayurveda as an adaptogen and skin purifier.',
        'benefits': 'Antibacterial and antifungal, purifies and cleanses skin, reduces acne, anti-inflammatory, antioxidant, reduces stress-induced skin problems.',
        'side_effects': 'Generally very safe. May cause mild contact dermatitis in sensitive individuals. Avoid high concentrations during pregnancy.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_oily': True,
    },
    {
        'name': 'Amla Extract',
        'inci_name': 'Emblica Officinalis Fruit Extract',
        'description': 'Indian gooseberry, one of the richest natural sources of Vitamin C. A cornerstone of Ayurvedic medicine for hair and skin.',
        'benefits': 'Extremely high Vitamin C content, powerful antioxidant, brightening, collagen boosting, reduces pigmentation, anti-aging, strengthens hair.',
        'side_effects': 'Generally safe. May cause mild staining. High acidity can irritate sensitive skin in high concentrations.',
        'category': 'antioxidant', 'risk_level': 'safe',
        'good_for_dry': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Rose Water',
        'inci_name': 'Rosa Damascena Flower Water',
        'description': 'Distilled water from rose petals, a staple in Indian and Middle Eastern beauty rituals for centuries. Used as a toner and soother across generations.',
        'benefits': 'Soothes irritated skin, natural toner, mild astringent, hydrating, anti-inflammatory, pleasant fragrance, balances skin pH.',
        'side_effects': 'Very well tolerated. Rarely causes reactions. Fragrant — may irritate highly fragrance-sensitive individuals.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_sensitive': True, 'good_for_dry': True,
        'is_fragrance': False,
    },
    {
        'name': 'Bakuchiol',
        'inci_name': 'Bakuchiol',
        'description': 'A meroterpene compound from the seeds of Psoralea corylifolia (babchi plant), long used in Ayurveda. The trending natural alternative to retinol.',
        'benefits': 'Retinol-like anti-aging effects without irritation, reduces fine lines, firms skin, brightening, stimulates collagen, safe for sensitive and pregnant skin.',
        'side_effects': 'Extremely well tolerated. One of the safest anti-aging actives available. No photosensitivity.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_dry': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Kesar',
        'inci_name': 'Crocus Sativus Extract (Saffron)',
        'description': 'The Indian name for saffron (Crocus sativus). Used in traditional Indian beauty rituals for its golden glow-giving properties.',
        'benefits': 'Brightens complexion, reduces dark circles and spots, antioxidant, anti-inflammatory, improves skin radiance, traditional treatment for dull skin.',
        'side_effects': 'Safe topically. Very expensive — products with meaningful kesar concentrations are premium priced.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_sensitive': True,
    },
    {
        'name': 'Chandan',
        'inci_name': 'Santalum Album Powder',
        'description': 'Sandalwood powder (Chandan), used in Indian beauty rituals and religious ceremonies for thousands of years. One of the oldest known cosmetic ingredients.',
        'benefits': 'Soothes skin inflammation, antimicrobial, reduces blemishes and scars, cooling, mild astringent, brightening, traditionally applied as face pack.',
        'side_effects': 'Generally safe. Rarely causes allergic contact dermatitis.',
        'category': 'botanical', 'risk_level': 'safe',
        'good_for_sensitive': True,
    },
    {
        'name': 'Papaya Extract',
        'inci_name': 'Carica Papaya Fruit Extract',
        'description': 'Derived from papaya fruit, widely grown across India. Contains papain enzyme which acts as a natural chemical exfoliant.',
        'benefits': 'Natural enzymatic exfoliation via papain, brightens dull skin, reduces dead skin buildup, de-tanning effect, improves skin texture, vitamin C content.',
        'side_effects': 'Papain can cause irritation in sensitive skin. Avoid if latex-allergic (cross-reactivity). Can cause stinging around eyes.',
        'category': 'exfoliant', 'risk_level': 'low',
        'good_for_oily': True,
    },
    {
        'name': 'Coconut Oil',
        'inci_name': 'Cocos Nucifera Oil',
        'description': 'Cold-pressed oil from coconut flesh. Extremely popular across South India, Kerala in particular, as a traditional beauty and hair care staple.',
        'benefits': 'Deep moisturising, antimicrobial (lauric acid), reduces inflammation, improves skin barrier, traditional hair growth treatment.',
        'side_effects': 'Highly comedogenic — can cause breakouts on face for oily/acne-prone skin types. Best used on body or hair rather than face.',
        'category': 'oil', 'risk_level': 'low',
        'good_for_dry': True,
    },
    {
        'name': 'Almond Oil',
        'inci_name': 'Prunus Dulcis Oil',
        'description': 'Cold-pressed oil from sweet almonds. Extremely popular in Indian households for baby massage and under-eye treatment.',
        'benefits': 'Rich in Vitamin E, softens and nourishes skin, reduces dark circles, lightweight, absorbs well, traditional baby massage oil.',
        'side_effects': 'Avoid if tree-nut allergic. Moderately comedogenic — use with caution on acne-prone skin.',
        'category': 'oil', 'risk_level': 'low',
        'good_for_dry': True,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with Ayurvedic and Indian ingredient information'

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for data in AYURVEDIC_INGREDIENTS:
            # Set defaults for missing boolean fields
            defaults = {
                'inci_name': data.get('inci_name', ''),
                'description': data.get('description', ''),
                'benefits': data.get('benefits', ''),
                'side_effects': data.get('side_effects', ''),
                'category': data.get('category', 'other'),
                'risk_level': data.get('risk_level', 'safe'),
                'good_for_dry': data.get('good_for_dry', False),
                'good_for_oily': data.get('good_for_oily', False),
                'good_for_sensitive': data.get('good_for_sensitive', False),
                'is_fragrance': data.get('is_fragrance', False),
                'is_alcohol': data.get('is_alcohol', False),
                'is_paraben': data.get('is_paraben', False),
                'is_sulfate': data.get('is_sulfate', False),
                'is_silicone': data.get('is_silicone', False),
            }
            obj, was_created = Ingredient.objects.update_or_create(
                name=data['name'],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done! Created: {created} Ayurvedic ingredients  |  Updated: {updated}"
        ))