# Generated by Django 5.0.6 on 2024-05-19 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
