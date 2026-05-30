"""
Ingredient Safety Checker

Scans a list of ingredients and flags potential irritants,
allergens, and controversial ingredients.
"""

IRRITANT_PATTERNS = {
    'fragrance': {
        'keywords': ['fragrance', 'parfum', 'perfume', 'fragrance (parfum)', 'linalool',
                     'limonene', 'eugenol', 'geraniol', 'citronellol'],
        'risk_level': 'moderate',
        'description': 'Common skin sensitizer, may cause allergic reactions.',
        'color': 'orange',
    },
    'alcohol': {
        'keywords': ['alcohol denat', 'denatured alcohol', 'ethanol', 'sd alcohol',
                     'alcohol (denat)', 'isopropyl alcohol'],
        'risk_level': 'moderate',
        'description': 'Drying, may disrupt skin barrier in high concentrations.',
        'color': 'yellow',
    },
    'parabens': {
        'keywords': ['methylparaben', 'propylparaben', 'butylparaben', 'ethylparaben',
                     'isobutylparaben', 'isopropylparaben'],
        'risk_level': 'low',
        'description': 'Preservatives with potential endocrine-disrupting concerns.',
        'color': 'yellow',
    },
    'sulfates': {
        'keywords': ['sodium lauryl sulfate', 'sls', 'sodium laureth sulfate', 'sles',
                     'ammonium lauryl sulfate', 'ammonium laureth sulfate'],
        'risk_level': 'moderate',
        'description': 'Harsh surfactants that can strip skin of natural oils.',
        'color': 'orange',
    },
    'formaldehyde_releasers': {
        'keywords': ['dmdm hydantoin', 'imidazolidinyl urea', 'diazolidinyl urea',
                     'quaternium-15', 'bronopol', '2-bromo-2-nitropropane-1,3-diol'],
        'risk_level': 'high',
        'description': 'Release formaldehyde over time; potential carcinogen and irritant.',
        'color': 'red',
    },
    'silicones': {
        'keywords': ['dimethicone', 'cyclomethicone', 'cyclopentasiloxane',
                     'dimethiconol', 'amodimethicone', 'trimethicone'],
        'risk_level': 'low',
        'description': 'Generally safe but may clog pores for some skin types.',
        'color': 'blue',
    },
    'peg_compounds': {
        'keywords': ['peg-', 'polyethylene glycol'],
        'risk_level': 'low',
        'description': 'May enhance penetration of other ingredients; concern if skin is broken.',
        'color': 'yellow',
    },
}

RISK_ORDER = {'avoid': 4, 'high': 3, 'moderate': 2, 'low': 1, 'safe': 0}


def check_ingredient_safety(ingredient_list: list) -> dict:
    """
    Analyze a list of ingredients and return safety flags.

    Args:
        ingredient_list: List of ingredient strings

    Returns:
        Dict with overall risk level and per-category flags
    """
    ingredient_text = ' '.join(i.lower() for i in ingredient_list)
    found_flags = []
    highest_risk = 'safe'

    for category, config in IRRITANT_PATTERNS.items():
        matched_ingredients = []
        for keyword in config['keywords']:
            if keyword.lower() in ingredient_text:
                # Find which actual ingredient matched
                for ing in ingredient_list:
                    if keyword.lower() in ing.lower():
                        matched_ingredients.append(ing)

        if matched_ingredients:
            found_flags.append({
                'category': category.replace('_', ' ').title(),
                'risk_level': config['risk_level'],
                'description': config['description'],
                'color': config['color'],
                'matched': list(set(matched_ingredients)),
            })

            # Track highest risk encountered
            if RISK_ORDER.get(config['risk_level'], 0) > RISK_ORDER.get(highest_risk, 0):
                highest_risk = config['risk_level']

    return {
        'flags': found_flags,
        'overall_risk': highest_risk,
        'flag_count': len(found_flags),
        'is_clean': len(found_flags) == 0,
    }


def analyze_custom_ingredient_list(raw_text: str) -> dict:
    """
    Parse a user-pasted ingredient list and run safety check.

    Args:
        raw_text: Raw ingredient text (comma or newline separated)

    Returns:
        Safety analysis dict
    """
    # Split on common delimiters
    import re
    ingredients = re.split(r'[,\n\r]+', raw_text)
    ingredients = [i.strip() for i in ingredients if i.strip()]
    return {
        'ingredient_count': len(ingredients),
        'ingredients': ingredients,
        'safety': check_ingredient_safety(ingredients),
    }
