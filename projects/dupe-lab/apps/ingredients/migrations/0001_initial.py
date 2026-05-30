from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, unique=True)),
                ('inci_name', models.CharField(blank=True, help_text='INCI scientific name', max_length=300)),
                ('description', models.TextField(blank=True)),
                ('benefits', models.TextField(blank=True)),
                ('side_effects', models.TextField(blank=True)),
                ('category', models.CharField(choices=[('humectant','Humectant'),('emollient','Emollient'),('occlusant','Occlusant'),('antioxidant','Antioxidant'),('exfoliant','Exfoliant'),('surfactant','Surfactant'),('preservative','Preservative'),('fragrance','Fragrance'),('sunscreen','UV Filter'),('brightener','Brightener'),('peptide','Peptide'),('retinoid','Retinoid'),('vitamin','Vitamin'),('botanical','Botanical Extract'),('oil','Oil'),('other','Other')], default='other', max_length=50)),
                ('risk_level', models.CharField(choices=[('safe','Safe'),('low','Low Risk'),('moderate','Moderate Risk'),('high','High Risk'),('avoid','Avoid')], default='safe', max_length=10)),
                ('good_for_dry', models.BooleanField(default=False)),
                ('good_for_oily', models.BooleanField(default=False)),
                ('good_for_sensitive', models.BooleanField(default=False)),
                ('is_fragrance', models.BooleanField(default=False)),
                ('is_alcohol', models.BooleanField(default=False)),
                ('is_paraben', models.BooleanField(default=False)),
                ('is_sulfate', models.BooleanField(default=False)),
                ('is_silicone', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.AddIndex(
            model_name='ingredient',
            index=models.Index(fields=['name'], name='ingredients_name_idx'),
        ),
    ]
