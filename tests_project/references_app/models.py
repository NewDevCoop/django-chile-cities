from django.db import models


class CityReference(models.Model):
    city = models.ForeignKey(
        "django_chile_cities.City",
        on_delete=models.PROTECT,
        related_name="test_references",
    )

    class Meta:
        verbose_name = "City reference"
        verbose_name_plural = "City references"
