# Generated by Django 4.1.4 on 2023-01-22 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EmotionBoard', '0007_modelvaliddataset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='write_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]