# Generated by Django 5.0.4 on 2024-11-01 14:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='year_level_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.yearlevelsection'),
        ),
    ]
