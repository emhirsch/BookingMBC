# Generated by Django 4.2.6 on 2023-12-19 13:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CalendarApp", "0001_initial"),
        ("UserApp", "0002_alter_userprofile_machines4thisuser_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="machines4ThisUser",
            field=models.ManyToManyField(
                blank=True, related_name="machines4ThisUser", to="CalendarApp.machine"
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="machines_bought",
            field=models.ManyToManyField(
                blank=True, related_name="machines_bought", to="CalendarApp.machine"
            ),
        ),
    ]
