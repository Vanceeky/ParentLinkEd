# Generated by Django 5.0.4 on 2024-09-09 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='subject_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
