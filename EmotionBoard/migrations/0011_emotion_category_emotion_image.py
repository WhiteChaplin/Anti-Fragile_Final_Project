# Generated by Django 4.1.4 on 2023-01-23 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EmotionBoard', '0010_diary_user_select_emotion'),
    ]

    operations = [
        migrations.AddField(
            model_name='emotion_category',
            name='emotion_image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
