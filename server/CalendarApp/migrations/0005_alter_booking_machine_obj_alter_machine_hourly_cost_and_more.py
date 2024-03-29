# Generated by Django 4.2.6 on 2024-03-08 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("CalendarApp", "0004_alter_machine_hourly_cost_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="machine_obj",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="CalendarApp.machine"
            ),
        ),
        migrations.AlterField(
            model_name="machine",
            name="hourly_cost",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="machine",
            name="hourly_cost_assisted",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="machine",
            name="hourly_cost_buyer",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="machine",
            name="hourly_cost_buyer_assisted",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="machine",
            name="hourly_cost_external",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AlterField(
            model_name="machine",
            name="hourly_cost_external_assisted",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
