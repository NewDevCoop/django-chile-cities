from django.db import models

# Create your models here.


class Region(models.Model):
    name = models.CharField(max_length=70)
    number = models.IntegerField()
    code = models.IntegerField()


class Province(models.Model):
    name = models.CharField(max_length=30)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    code = models.IntegerField()


class City(models.Model):
    name = models.CharField(max_length=20)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    conara_sii = models.IntegerField(null=True)
    code_treasury = models.IntegerField(null=True)
    code = models.IntegerField()
    hashtag = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.name
