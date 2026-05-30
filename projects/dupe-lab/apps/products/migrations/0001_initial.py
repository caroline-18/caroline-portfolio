from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=500)),
                ('slug', models.SlugField(blank=True, max_length=600, unique=True)),
                ('category', models.CharField(choices=[('moisturizer','Moisturizer'),('serum','Serum'),('cleanser','Cleanser'),('toner','Toner'),('sunscreen','Sunscreen'),('mask','Mask'),('eye_cream','Eye Cream'),('exfoliator','Exfoliator'),('oil','Face Oil'),('treatment','Treatment'),('other','Other')], default='other', max_length=50)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('rank', models.FloatField(blank=True, help_text='Product rating (0-5)', null=True)),
                ('ingredients', models.TextField(help_text='Comma-separated ingredient list')),
                ('image_url', models.URLField(blank=True)),
                ('skin_dry', models.BooleanField(default=False)),
                ('skin_oily', models.BooleanField(default=False)),
                ('skin_normal', models.BooleanField(default=False)),
                ('skin_combination', models.BooleanField(default=False)),
                ('skin_sensitive', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['brand', 'name']},
        ),
        migrations.CreateModel(
            name='SimilarityCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity_score', models.FloatField()),
                ('computed_at', models.DateTimeField(auto_now=True)),
                ('product_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='similarity_as_a', to='products.product')),
                ('product_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='similarity_as_b', to='products.product')),
            ],
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['brand'], name='products_pr_brand_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category'], name='products_pr_category_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['price'], name='products_pr_price_idx'),
        ),
        migrations.AddIndex(
            model_name='similaritycache',
            index=models.Index(fields=['product_a', 'similarity_score'], name='products_si_product_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='similaritycache',
            unique_together={('product_a', 'product_b')},
        ),
    ]
