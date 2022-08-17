# Generated by Django 4.1 on 2022-08-17 21:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_messagefordelete'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='Date',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.date'),
        ),
        migrations.AlterField(
            model_name='team',
            name='Picture',
            field=models.ImageField(upload_to='static/photos/'),
        ),
    ]
