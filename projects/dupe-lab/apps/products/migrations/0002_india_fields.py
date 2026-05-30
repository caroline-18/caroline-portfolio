from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='made_in_india',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='is_ayurvedic',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='currency',
            field=models.CharField(default='INR', max_length=5),
        ),
    ]