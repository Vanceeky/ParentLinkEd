# Generated by Django 5.0.4 on 2024-10-03 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_guardian_avatar_guardian_relationship'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='student_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
