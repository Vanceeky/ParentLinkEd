# Generated by Django 5.0.4 on 2024-09-09 18:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_subject_subject_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yearlevelsection',
            name='instructor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='year_level_sections', to='base.instructor'),
        ),
    ]
