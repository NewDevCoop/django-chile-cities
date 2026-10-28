from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from django_chile_cities.models import City, Province, Region


def _iso_3166_2_cl(sequence):
    first_letter = chr(ord("A") + sequence % 26)
    second_letter = chr(ord("A") + (sequence // 26) % 26)
    return f"CL-{first_letter}{second_letter}"


class RegionFactory(DjangoModelFactory):
    class Meta:
        model = Region

    name = Sequence(lambda number: f"Región de Prueba {number}")
    number = Sequence(lambda number: number + 1)
    code = Sequence(lambda number: number + 1)
    iso_3166_2_cl = Sequence(_iso_3166_2_cl)


class ProvinceFactory(DjangoModelFactory):
    class Meta:
        model = Province

    name = Sequence(lambda number: f"Provincia de Prueba {number}")
    code = Sequence(lambda number: number + 1)
    region = SubFactory(RegionFactory)


class CityFactory(DjangoModelFactory):
    class Meta:
        model = City

    name = Sequence(lambda number: f"Comuna de Prueba {number}")
    code = Sequence(lambda number: number + 1)
    conara_sii = Sequence(lambda number: number + 1)
    code_treasury = Sequence(lambda number: number + 1)
    province = SubFactory(ProvinceFactory)
