# Generated by Django 4.1 on 2022-09-02 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_alter_date_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='Name',
            field=models.CharField(max_length=300, unique=True),
        ),
    ]
