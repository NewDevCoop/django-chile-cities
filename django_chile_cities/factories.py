from factory.django import DjangoModelFactory
from factory import SubFactory


class RegionFactory(DjangoModelFactory):
    class Meta:
        model = 'chile_cities.region'

    name = 'region 1'
    iso_3166_2_cl = 'CL'


class ProvinceFactory(DjangoModelFactory):
    class Meta:
        model = 'chile_cities.province'

    name = 'provincia 1'
    region = SubFactory(RegionFactory)


class CityFactory(DjangoModelFactory):
    class Meta:
        model = 'chile_cities.city'

    name = 'ciudad 1'
    province = SubFactory(ProvinceFactory)
