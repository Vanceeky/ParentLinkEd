# Generated by Django 5.0.4 on 2024-10-13 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_grade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='quarter_1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grade',
            name='quarter_2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grade',
            name='quarter_3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='grade',
            name='quarter_4',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
