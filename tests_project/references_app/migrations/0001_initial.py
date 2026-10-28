import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("django_chile_cities", "0002_region_iso_3166_2_cl_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CityReference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="test_references",
                        to="django_chile_cities.city",
                    ),
                ),
            ],
            options={
                "verbose_name": "City reference",
                "verbose_name_plural": "City references",
            },
        ),
    ]
