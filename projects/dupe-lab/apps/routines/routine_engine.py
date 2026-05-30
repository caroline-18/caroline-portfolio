STEP_ORDER = {
    'am': ['cleanser','toner','serum','treatment','moisturizer','sunscreen','eye_cream'],
    'pm': ['cleanser','toner','serum','treatment','moisturizer','oil'],
    'weekly': ['exfoliator','mask','treatment','moisturizer'],
}

CONFLICT_PAIRS = [
    ('retinol',      'aha',       'Retinol + AHA can cause severe irritation'),
    ('retinol',      'bha',       'Retinol + BHA can cause severe irritation'),
    ('retinol',      'vitamin c', 'Use Vitamin C in AM and Retinol in PM'),
    ('niacinamide',  'vitamin c', 'May cause temporary flushing at high concentrations'),
    ('aha',          'bha',       'Using both at once can over-exfoliate skin'),
]

def sort_products_into_routine(products, routine_type='am'):
    order = STEP_ORDER.get(routine_type, STEP_ORDER['am'])
    buckets = {cat: [] for cat in order}
    unmatched = []

    for product in products:
        cat = product.category.lower().replace(' ', '_')
        if cat in buckets:
            buckets[cat].append(product)
        else:
            unmatched.append(product)

    steps = []
    step_num = 1
    for cat in order:
        for product in buckets[cat]:
            steps.append({'step_num': step_num, 'category': cat, 'product': product})
            step_num += 1

    for product in unmatched:
        steps.append({'step_num': step_num, 'category': 'other', 'product': product})
        step_num += 1

    return steps

def detect_conflicts(products):
    all_ingredients = {}
    for p in products:
        ingredient_text = (p.ingredients or '').lower()
        all_ingredients[p.id] = ingredient_text

    warnings = []
    for i, p1 in enumerate(products):
        for p2 in products[i+1:]:
            ing1 = all_ingredients[p1.id]
            ing2 = all_ingredients[p2.id]
            for a, b, reason in CONFLICT_PAIRS:
                if a in ing1 and b in ing2:
                    warnings.append({
                        'product_a': p1.name,
                        'product_b': p2.name,
                        'reason':    reason,
                    })
    return warnings