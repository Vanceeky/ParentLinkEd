# Generated by Django 5.0.4 on 2024-10-03 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_student_age_student_avatar_student_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='guardian',
            name='avatar',
            field=models.ImageField(blank=True, default='/default_avatar.png', null=True, upload_to='avatars/'),
        ),
        migrations.AddField(
            model_name='guardian',
            name='relationship',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
