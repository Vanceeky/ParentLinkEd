# Generated by Django 5.0.4 on 2024-10-16 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_grade_quarter_1_alter_grade_quarter_2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('date', models.DateField()),
            ],
        ),
    ]
