# Generated by Django 5.2.4 on 2025-07-18 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_video_uploaded_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videoquality',
            name='quality',
            field=models.CharField(choices=[('480p', '480p'), ('720p', '720p'), ('1080p', '1080p')], max_length=10),
        ),
    ]
