# Generated by Django 5.1.7 on 2025-04-09 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0003_alter_workout_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout',
            name='name_workout_en',
            field=models.CharField(default='<django.db.models.fields.related.ForeignKey>', max_length=50),
        ),
        migrations.AddField(
            model_name='workout',
            name='name_workout_fr',
            field=models.CharField(default='<django.db.models.fields.related.ForeignKey>', max_length=50),
        ),
    ]
