# Generated by Django 4.2.6 on 2023-12-29 11:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("UserApp", "0005_alter_mbcgroup_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="password_reset_token",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
