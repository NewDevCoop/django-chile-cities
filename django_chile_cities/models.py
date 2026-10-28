from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=70)
    number = models.IntegerField()
    code = models.IntegerField(unique=True)
    iso_3166_2_cl = models.CharField(max_length=5, unique=True)

    class Meta:
        verbose_name = "Región"
        verbose_name_plural = "Regiones"
        ordering = ["number"]

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    code = models.IntegerField()

    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["region", "code"],
                name="unique_province_code_per_region",
            ),
        ]

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    conara_sii = models.IntegerField(null=True, blank=True)
    code_treasury = models.IntegerField(null=True, blank=True)
    code = models.IntegerField()
    hashtag = models.CharField(max_length=100, default="", blank=True)

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["province", "code"],
                name="unique_city_code_per_province",
            ),
        ]

    def __str__(self):
        return self.name
