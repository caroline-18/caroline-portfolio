from rest_framework import serializers
from .models import Product, SimilarityCache


class ProductSerializer(serializers.ModelSerializer):
    skin_types = serializers.SerializerMethodField()
    ingredient_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'brand', 'name', 'slug', 'category',
            'price', 'rank', 'skin_types', 'ingredient_count',
        ]

    def get_skin_types(self, obj):
        return obj.get_skin_types()


class ProductDetailSerializer(ProductSerializer):
    ingredient_list = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['ingredients', 'ingredient_list']

    def get_ingredient_list(self, obj):
        return obj.get_ingredient_list()


class SimilarityCacheSerializer(serializers.ModelSerializer):
    product_b = ProductSerializer(read_only=True)
    is_budget_dupe = serializers.BooleanField(read_only=True)
    dupe_score = serializers.FloatField(read_only=True)

    class Meta:
        model = SimilarityCache
        fields = ['product_b', 'similarity_score', 'is_budget_dupe', 'dupe_score']
