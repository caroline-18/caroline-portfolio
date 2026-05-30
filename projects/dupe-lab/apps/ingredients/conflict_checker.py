from .models import IngredientConflict

def check_ingredients_for_conflicts(ingredient_text: str) -> list[dict]:
    """
    Takes a raw ingredient string from a product and checks
    it against all known conflict pairs.
    """
    text = ingredient_text.lower()
    all_conflicts = IngredientConflict.objects.all()
    found = []

    for conflict in all_conflicts:
        a = conflict.ingredient_a.lower()
        b = conflict.ingredient_b.lower()
        if a in text and b in text:
            found.append({
                'ingredient_a':    conflict.ingredient_a,
                'ingredient_b':    conflict.ingredient_b,
                'severity':        conflict.severity,
                'reason':          conflict.reason,
                'safe_alternative': conflict.safe_alternative,
            })
    return found

def check_multiple_products(products) -> list[dict]:
    """
    Check conflicts across a list of products by combining
    all their ingredients and scanning for conflict pairs.
    """
    combined_ingredients = {}
    for product in products:
        ing_text = (product.ingredients or '').lower()
        combined_ingredients[product.name] = ing_text

    all_conflicts = IngredientConflict.objects.all()
    found = []

    for conflict in all_conflicts:
        a = conflict.ingredient_a.lower()
        b = conflict.ingredient_b.lower()

        products_with_a = [name for name, ings in combined_ingredients.items() if a in ings]
        products_with_b = [name for name, ings in combined_ingredients.items() if b in ings]

        if products_with_a and products_with_b:
            found.append({
                'ingredient_a':     conflict.ingredient_a,
                'ingredient_b':     conflict.ingredient_b,
                'severity':         conflict.severity,
                'reason':           conflict.reason,
                'safe_alternative': conflict.safe_alternative,
                'found_in_a':       products_with_a,
                'found_in_b':       products_with_b,
            })
    return found