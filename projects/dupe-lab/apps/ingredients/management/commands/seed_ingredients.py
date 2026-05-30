"""
Management command: seed_ingredients
======================================
Populates the Ingredient table with descriptions, benefits,
risk levels, and flags for the most common skincare ingredients.

Usage:
    python manage.py seed_ingredients
"""
from django.core.management.base import BaseCommand
from apps.ingredients.models import Ingredient

INGREDIENT_DATA = [
    {
        'name': 'Niacinamide',
        'inci_name': 'Niacinamide',
        'description': 'A form of Vitamin B3 and one of the most well-researched skincare ingredients. Water-soluble and stable across a wide pH range.',
        'benefits': 'Improves skin barrier function, reduces inflammation and redness, minimizes pore appearance, brightens skin tone, reduces hyperpigmentation, controls sebum production.',
        'side_effects': 'Generally very well tolerated. High concentrations (>10%) may cause flushing in some individuals.',
        'category': 'vitamin',
        'risk_level': 'safe',
        'good_for_dry': True, 'good_for_oily': True, 'good_for_sensitive': True,
        'is_fragrance': False, 'is_alcohol': False, 'is_paraben': False, 'is_sulfate': False,
    },
    {
        'name': 'Hyaluronic Acid',
        'inci_name': 'Sodium Hyaluronate',
        'description': 'A naturally occurring polysaccharide that can hold up to 1000x its weight in water. Key humectant in modern skincare.',
        'benefits': 'Intense hydration, plumps skin, reduces appearance of fine lines, supports wound healing, improves skin elasticity.',
        'side_effects': 'Extremely well tolerated. In low humidity environments, may draw moisture from skin if not sealed with an occlusive.',
        'category': 'humectant',
        'risk_level': 'safe',
        'good_for_dry': True, 'good_for_oily': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Glycerin',
        'inci_name': 'Glycerin',
        'description': 'A simple polyol compound and one of the most effective and affordable humectants. Found in almost every moisturizer.',
        'benefits': 'Attracts moisture to skin, strengthens skin barrier, gentle enough for all skin types, improves skin softness and smoothness.',
        'side_effects': 'Very safe. In very high concentrations without dilution can feel sticky.',
        'category': 'humectant',
        'risk_level': 'safe',
        'good_for_dry': True, 'good_for_oily': False, 'good_for_sensitive': True,
    },
    {
        'name': 'Retinol',
        'inci_name': 'Retinol',
        'description': 'A form of Vitamin A and gold-standard anti-aging ingredient. Converts to retinoic acid in the skin to accelerate cell turnover.',
        'benefits': 'Reduces fine lines and wrinkles, increases collagen production, fades hyperpigmentation, unclogs pores, improves skin texture.',
        'side_effects': 'Retinoid dermatitis (dryness, flaking, redness) especially when starting. Photosensitizing — must use SPF. Avoid during pregnancy.',
        'category': 'retinoid',
        'risk_level': 'moderate',
        'good_for_dry': False, 'good_for_oily': True, 'good_for_sensitive': False,
    },
    {
        'name': 'Vitamin C',
        'inci_name': 'Ascorbic Acid',
        'description': 'A potent antioxidant and brightening agent. L-ascorbic acid is the most active form but also the most unstable.',
        'benefits': 'Brightens skin tone, fades dark spots, neutralizes free radicals, boosts collagen synthesis, improves UV damage.',
        'side_effects': 'Can cause irritation at high concentrations, especially on sensitive skin. Oxidizes quickly once opened.',
        'category': 'antioxidant',
        'risk_level': 'low',
        'good_for_dry': True, 'good_for_oily': True, 'good_for_sensitive': False,
    },
    {
        'name': 'Ceramide NP',
        'inci_name': 'Ceramide NP',
        'description': 'A type of ceramide (lipid) that is a natural component of the skin barrier. Helps maintain the integrity of the stratum corneum.',
        'benefits': 'Restores and strengthens skin barrier, reduces transepidermal water loss (TEWL), soothes sensitive and eczema-prone skin.',
        'side_effects': 'Extremely well tolerated. No known side effects.',
        'category': 'emollient',
        'risk_level': 'safe',
        'good_for_dry': True, 'good_for_oily': False, 'good_for_sensitive': True,
    },
    {
        'name': 'Salicylic Acid',
        'inci_name': 'Salicylic Acid',
        'description': 'A beta hydroxy acid (BHA) that is oil-soluble, allowing it to penetrate into pores. Classic exfoliant for oily and acne-prone skin.',
        'benefits': 'Exfoliates inside pores, reduces blackheads and whiteheads, anti-inflammatory, reduces sebum, treats and prevents acne.',
        'side_effects': 'Can cause dryness and irritation, especially at high concentrations. Avoid during pregnancy in large amounts.',
        'category': 'exfoliant',
        'risk_level': 'low',
        'good_for_dry': False, 'good_for_oily': True, 'good_for_sensitive': False,
    },
    {
        'name': 'Glycolic Acid',
        'inci_name': 'Glycolic Acid',
        'description': 'An alpha hydroxy acid (AHA) derived from sugarcane with the smallest molecular weight, allowing deepest penetration.',
        'benefits': 'Chemical exfoliation, brightens dull skin, reduces fine lines, fades hyperpigmentation, improves skin texture.',
        'side_effects': 'Photosensitizing — always use SPF. Can cause stinging, redness, and increased sensitivity especially at high concentrations.',
        'category': 'exfoliant',
        'risk_level': 'moderate',
        'good_for_dry': False, 'good_for_oily': True, 'good_for_sensitive': False,
    },
    {
        'name': 'Dimethicone',
        'inci_name': 'Dimethicone',
        'description': 'A silicone polymer used extensively as an emollient and skin protectant. Gives products a silky, slip-free texture.',
        'benefits': 'Creates a protective barrier, smooths skin surface, fills in fine lines temporarily, non-comedogenic in moderate amounts.',
        'side_effects': 'Generally safe but can trap debris if not properly cleansed off. Some users report breakouts.',
        'category': 'emollient',
        'risk_level': 'low',
        'good_for_dry': True, 'good_for_oily': False, 'good_for_sensitive': True,
        'is_silicone': True,
    },
    {
        'name': 'Fragrance',
        'inci_name': 'Parfum / Fragrance',
        'description': 'A catch-all term for scent compounds added to cosmetics. Can include hundreds of undisclosed chemicals under one label.',
        'benefits': 'Improves sensory experience of products. No skin benefit.',
        'side_effects': 'Common allergen and skin sensitizer. Can cause contact dermatitis, inflammation, and allergic reactions. Particularly problematic for sensitive skin.',
        'category': 'fragrance',
        'risk_level': 'moderate',
        'good_for_dry': False, 'good_for_oily': False, 'good_for_sensitive': False,
        'is_fragrance': True,
    },
    {
        'name': 'Alcohol Denat',
        'inci_name': 'Alcohol Denat.',
        'description': 'Denatured ethanol (drinking alcohol with denaturants added). Used as an antimicrobial, solvent, and to give lightweight textures.',
        'benefits': 'Creates lightweight feel, acts as preservative, helps other ingredients penetrate.',
        'side_effects': 'Disrupts skin barrier at high concentrations, causes dryness, irritation, and can worsen rosacea. Controversial in skincare.',
        'category': 'other',
        'risk_level': 'moderate',
        'good_for_dry': False, 'good_for_oily': False, 'good_for_sensitive': False,
        'is_alcohol': True,
    },
    {
        'name': 'Methylparaben',
        'inci_name': 'Methylparaben',
        'description': 'The most widely used paraben preservative in cosmetics. Prevents mold and bacterial growth.',
        'benefits': 'Effective broad-spectrum preservative that extends product shelf life.',
        'side_effects': 'Potential endocrine disruptor at high systemic doses — though absorption from topical use is minimal. Associated with skin sensitivity.',
        'category': 'preservative',
        'risk_level': 'low',
        'is_paraben': True,
    },
    {
        'name': 'Sodium Lauryl Sulfate',
        'inci_name': 'Sodium Lauryl Sulfate',
        'description': 'A strong anionic surfactant used as a foaming and cleansing agent. Common in shampoos and cleansers.',
        'benefits': 'Effective at removing dirt and oil, creates rich lather.',
        'side_effects': 'Strips skin of natural oils, damages skin barrier, causes dryness and irritation especially with prolonged use.',
        'category': 'surfactant',
        'risk_level': 'moderate',
        'is_sulfate': True,
    },
    {
        'name': 'Tocopherol',
        'inci_name': 'Tocopherol',
        'description': 'Natural Vitamin E, one of the most important fat-soluble antioxidants in skin. Both a skin nutrient and a stabilizer for other ingredients.',
        'benefits': 'Antioxidant protection, moisturizing, supports skin healing, stabilizes formulas with Vitamin C.',
        'side_effects': 'Occasionally causes contact dermatitis in sensitive individuals. Generally very well tolerated.',
        'category': 'antioxidant',
        'risk_level': 'safe',
        'good_for_dry': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Panthenol',
        'inci_name': 'Panthenol',
        'description': 'Pro-Vitamin B5 that converts to pantothenic acid in the skin. A soothing humectant and skin conditioner.',
        'benefits': 'Hydrates and soothes skin, promotes healing, improves barrier function, reduces inflammation, adds moisture.',
        'side_effects': 'Extremely gentle. Rarely causes any adverse reactions.',
        'category': 'humectant',
        'risk_level': 'safe',
        'good_for_dry': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Zinc PCA',
        'inci_name': 'Zinc PCA',
        'description': 'A combination of zinc and PCA (pyrrolidone carboxylic acid). Targets sebum regulation and has antimicrobial properties.',
        'benefits': 'Controls excess oil production, reduces acne-causing bacteria, minimizes pores, anti-inflammatory.',
        'side_effects': 'Generally well tolerated. May cause dryness if overused.',
        'category': 'other',
        'risk_level': 'safe',
        'good_for_oily': True,
    },
    {
        'name': 'Ferulic Acid',
        'inci_name': 'Ferulic Acid',
        'description': 'A plant-based antioxidant that dramatically boosts the stability and efficacy of Vitamins C and E when used together.',
        'benefits': 'Amplifies antioxidant protection, improves photostability of Vitamin C, anti-aging, anti-inflammatory.',
        'side_effects': 'Very well tolerated. May cause stinging in high concentrations.',
        'category': 'antioxidant',
        'risk_level': 'safe',
    },
    {
        'name': 'Squalane',
        'inci_name': 'Squalane',
        'description': 'A stable, hydrogenated form of squalene that mimics the skin\'s own lipids. Lightweight and non-greasy.',
        'benefits': 'Deep moisturizing without greasiness, supports barrier repair, antioxidant, suitable for all skin types.',
        'side_effects': 'Excellent safety profile. Non-comedogenic and very rarely causes reactions.',
        'category': 'emollient',
        'risk_level': 'safe',
        'good_for_dry': True, 'good_for_oily': True, 'good_for_sensitive': True,
    },
    {
        'name': 'Allantoin',
        'inci_name': 'Allantoin',
        'description': 'A naturally occurring compound (found in comfrey plant) with exceptional soothing and skin-softening properties.',
        'benefits': 'Soothes irritated skin, promotes cell regeneration, softens skin, reduces inflammation, keratolytic (softens rough skin).',
        'side_effects': 'One of the safest ingredients in skincare. No known significant side effects.',
        'category': 'other',
        'risk_level': 'safe',
        'good_for_sensitive': True,
    },
    {
        'name': 'Centella Asiatica Extract',
        'inci_name': 'Centella Asiatica Extract',
        'description': 'Herb extract with long history in Ayurvedic and traditional Chinese medicine. Rich in triterpenoids including madecassoside and asiaticoside.',
        'benefits': 'Calms sensitive and irritated skin, promotes wound healing and collagen synthesis, antioxidant, strengthens skin barrier.',
        'side_effects': 'Very well tolerated. Rare allergic reactions in sensitive individuals.',
        'category': 'botanical',
        'risk_level': 'safe',
        'good_for_sensitive': True,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with common skincare ingredient information'

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for data in INGREDIENT_DATA:
            obj, was_created = Ingredient.objects.update_or_create(
                name=data['name'],
                defaults=data,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done! Created: {created}  |  Updated: {updated}"
        ))
