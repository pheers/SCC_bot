# Generated by Django 4.1 on 2022-09-23 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_remove_date_team_dateteam'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='FileId',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
