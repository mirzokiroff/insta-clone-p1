# Generated by Django 5.1.1 on 2024-10-29 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_remove_post_alt_text_remove_post_audio_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_saved',
            field=models.BooleanField(default=False),
        ),
    ]
