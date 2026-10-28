from django.db import migrations, models

ISO_3166_2_CL = {
    1: "CL-TA",
    2: "CL-AN",
    3: "CL-AT",
    4: "CL-CO",
    5: "CL-VS",
    6: "CL-LI",
    7: "CL-ML",
    8: "CL-BI",
    9: "CL-AR",
    10: "CL-LL",
    11: "CL-AI",
    12: "CL-MA",
    13: "CL-RM",
    14: "CL-LR",
    15: "CL-AP",
    16: "CL-NB",
}


def _duplicates(values):
    seen = set()
    duplicates = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def populate_iso_3166_2_cl(apps, schema_editor):
    Region = apps.get_model("django_chile_cities", "Region")
    duplicate_codes = _duplicates(Region.objects.values_list("code", flat=True))
    if duplicate_codes:
        raise RuntimeError(
            "Cannot add a unique constraint on Region.code: duplicate codes "
            f"{duplicate_codes}. Clean the data before migrating."
        )

    for code, iso_code in ISO_3166_2_CL.items():
        Region.objects.filter(code=code).update(iso_3166_2_cl=iso_code)

    missing = list(
        Region.objects.filter(iso_3166_2_cl__isnull=True).values_list(
            "code", "number", "name"
        )
    )
    if missing:
        formatted = ", ".join(
            f"code={code} number={number} ({name})" for code, number, name in missing
        )
        raise RuntimeError(
            "Cannot populate ISO 3166-2:CL codes for regions: "
            f"{formatted}. The migration expects regions with codes 1-16."
        )


def validate_unique_constraints(apps, schema_editor):
    Province = apps.get_model("django_chile_cities", "Province")
    City = apps.get_model("django_chile_cities", "City")

    province_keys = list(Province.objects.values_list("region_id", "code"))
    duplicate_provinces = _duplicates(province_keys)
    if duplicate_provinces:
        raise RuntimeError(
            "Cannot add the unique constraint on Province (region, code): "
            f"duplicate values {duplicate_provinces}. Clean the data before "
            "migrating."
        )

    city_keys = list(City.objects.values_list("province_id", "code"))
    duplicate_cities = _duplicates(city_keys)
    if duplicate_cities:
        raise RuntimeError(
            "Cannot add the unique constraint on City (province, code): "
            f"duplicate values {duplicate_cities}. Clean the data before "
            "migrating."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("django_chile_cities", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="region",
            options={
                "ordering": ["number"],
                "verbose_name": "Región",
                "verbose_name_plural": "Regiones",
            },
        ),
        migrations.AlterModelOptions(
            name="province",
            options={
                "ordering": ["name"],
                "verbose_name": "Provincia",
                "verbose_name_plural": "Provincias",
            },
        ),
        migrations.AlterModelOptions(
            name="city",
            options={
                "ordering": ["name"],
                "verbose_name": "Ciudad",
                "verbose_name_plural": "Ciudades",
            },
        ),
        migrations.AddField(
            model_name="region",
            name="iso_3166_2_cl",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.RunPython(populate_iso_3166_2_cl, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="region",
            name="iso_3166_2_cl",
            field=models.CharField(max_length=5, unique=True),
        ),
        migrations.AlterField(
            model_name="region",
            name="code",
            field=models.IntegerField(unique=True),
        ),
        migrations.RunPython(validate_unique_constraints, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="city",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="city",
            name="conara_sii",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="city",
            name="code_treasury",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="province",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name="province",
            constraint=models.UniqueConstraint(
                fields=("region", "code"),
                name="unique_province_code_per_region",
            ),
        ),
        migrations.AddConstraint(
            model_name="city",
            constraint=models.UniqueConstraint(
                fields=("province", "code"),
                name="unique_city_code_per_province",
            ),
        ),
    ]
