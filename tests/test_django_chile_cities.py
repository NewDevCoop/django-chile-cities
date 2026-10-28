from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.test import TestCase
from references_app.models import CityReference

from django_chile_cities.factories import CityFactory, ProvinceFactory, RegionFactory
from django_chile_cities.models import City, Province, Region


class LoadChileCitiesCommandTests(TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command("load_chile_cities", *args, stdout=out, **kwargs)
        return out.getvalue()

    def test_loads_all_data(self):
        output = self.call_command()
        self.assertEqual(Region.objects.count(), 16)
        self.assertEqual(Province.objects.count(), 56)
        self.assertEqual(City.objects.count(), 346)
        self.assertIn("16 regions", output)
        self.assertIn("56 provinces", output)
        self.assertIn("346 cities", output)

    def test_command_is_idempotent(self):
        self.call_command()
        region_pks = dict(Region.objects.values_list("code", "pk"))
        city_pks = dict(City.objects.values_list("code", "pk"))
        self.call_command()
        self.assertEqual(Region.objects.count(), 16)
        self.assertEqual(Province.objects.count(), 56)
        self.assertEqual(City.objects.count(), 346)
        self.assertEqual(dict(Region.objects.values_list("code", "pk")), region_pks)
        self.assertEqual(dict(City.objects.values_list("code", "pk")), city_pks)

    def test_force_updates_modified_data(self):
        self.call_command()
        region = Region.objects.get(code=13)
        region.name = "Modified name"
        region.save()
        self.call_command(force=True)
        self.assertEqual(
            Region.objects.get(code=13).name,
            "Región Metropolitana de Santiago",
        )

    def test_force_preserves_primary_keys(self):
        self.call_command()
        city = City.objects.get(code=1101)
        region = Region.objects.get(code=13)
        self.call_command(force=True)
        self.assertEqual(City.objects.get(code=1101).pk, city.pk)
        self.assertEqual(Region.objects.get(code=13).pk, region.pk)

    def test_force_removes_stale_records(self):
        self.call_command()
        province = Province.objects.get(code=11)
        City.objects.create(name="Comuna obsoleta", province=province, code=9999)
        output = self.call_command(force=True)
        self.assertFalse(City.objects.filter(code=9999).exists())
        self.assertIn("Removed 1 stale records.", output)

    def test_force_keeps_records_referenced_with_protect(self):
        self.call_command()
        city = City.objects.get(code=1101)
        reference = CityReference.objects.create(city=city)
        self.call_command(force=True)
        self.assertTrue(CityReference.objects.filter(pk=reference.pk).exists())
        self.assertEqual(City.objects.get(pk=city.pk).code, 1101)

    def test_force_reports_protected_stale_records(self):
        self.call_command()
        province = Province.objects.get(code=11)
        stale = City.objects.create(
            name="Comuna obsoleta",
            province=province,
            code=9999,
        )
        CityReference.objects.create(city=stale)
        with self.assertRaisesMessage(CommandError, "referenced by other models"):
            self.call_command(force=True)
        self.assertTrue(City.objects.filter(pk=stale.pk).exists())

    def test_region_filter(self):
        self.call_command(region=1)
        self.assertEqual(Region.objects.count(), 1)
        self.assertEqual(Province.objects.count(), 2)
        self.assertEqual(City.objects.count(), 7)

    def test_region_filter_invalid_number(self):
        with self.assertRaisesMessage(CommandError, "No region found with number 99."):
            self.call_command(region=99)

    def test_force_region_filter_does_not_delete_other_regions(self):
        self.call_command()
        output = self.call_command(region=1, force=True)
        self.assertEqual(Region.objects.count(), 16)
        self.assertEqual(City.objects.count(), 346)
        self.assertIn("Removed 0 stale records.", output)

    def test_force_region_filter_removes_stale_records_in_region(self):
        self.call_command()
        province = Province.objects.get(code=11)
        City.objects.create(name="Comuna obsoleta", province=province, code=9999)
        self.call_command(region=1, force=True)
        self.assertFalse(City.objects.filter(code=9999).exists())
        self.assertEqual(City.objects.count(), 346)


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_chile_cities", stdout=StringIO())

    def test_str_methods(self):
        self.assertEqual(
            str(Region.objects.get(code=13)),
            "Región Metropolitana de Santiago",
        )
        self.assertEqual(str(Province.objects.get(code=11)), "Iquique")
        self.assertEqual(str(City.objects.get(code=1101)), "Iquique")

    def test_region_ordering(self):
        numbers = list(Region.objects.values_list("number", flat=True))
        self.assertEqual(numbers, sorted(numbers))

    def test_region_iso_3166_2_cl_codes(self):
        self.assertEqual(Region.objects.get(number=13).iso_3166_2_cl, "CL-RM")
        codes = list(Region.objects.values_list("iso_3166_2_cl", flat=True))
        self.assertEqual(len(codes), len(set(codes)))

    def test_city_hierarchy(self):
        city = City.objects.get(code=1101)
        self.assertEqual(city.province.name, "Iquique")
        self.assertEqual(city.province.region.name, "Región de Tarapacá")

    def test_meta_verbose_names(self):
        self.assertEqual(Region._meta.verbose_name, "Región")
        self.assertEqual(Province._meta.verbose_name, "Provincia")
        self.assertEqual(City._meta.verbose_name, "Ciudad")

    def test_region_code_unique_constraint(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Region.objects.create(
                name="Duplicada",
                number=99,
                code=1,
                iso_3166_2_cl="CL-XX",
            )

    def test_region_iso_unique_constraint(self):
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Region.objects.create(
                name="Duplicada",
                number=99,
                code=99,
                iso_3166_2_cl="CL-TA",
            )

    def test_province_unique_constraint(self):
        region = Region.objects.get(code=1)
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Province.objects.create(name="Duplicada", region=region, code=11)

    def test_city_unique_constraint(self):
        province = Province.objects.get(code=11)
        with transaction.atomic(), self.assertRaises(IntegrityError):
            City.objects.create(name="Duplicada", province=province, code=1101)


class DataIntegrityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_chile_cities", stdout=StringIO())

    def test_counts(self):
        self.assertEqual(Region.objects.count(), 16)
        self.assertEqual(Province.objects.count(), 56)
        self.assertEqual(City.objects.count(), 346)

    def test_all_cities_reach_region_through_province(self):
        self.assertEqual(
            City.objects.exclude(province__region__isnull=True).count(),
            City.objects.count(),
        )

    def test_official_region_names(self):
        names = {region.number: region.name for region in Region.objects.all()}
        self.assertEqual(names[6], "Región de O'Higgins")
        self.assertEqual(names[8], "Región del Biobío")
        self.assertEqual(names[9], "Región de La Araucanía")
        self.assertEqual(
            names[11], "Región de Aysén del General Carlos Ibáñez del Campo"
        )
        self.assertEqual(names[12], "Región de Magallanes y de la Antártica Chilena")
        self.assertEqual(names[13], "Región Metropolitana de Santiago")
        self.assertEqual(names[16], "Región de Ñuble")

    def test_corrected_names(self):
        expected_cities = [
            "Paihuano",
            "La Calera",
            "Llay-Llay",
            "Marchigüe",
            "San Pedro de la Paz",
            "Padre las Casas",
            "San Juan de la Costa",
            "O'Higgins",
            "Aysén",
        ]
        for name in expected_cities:
            with self.subTest(name=name):
                self.assertTrue(City.objects.filter(name=name).exists())

        expected_provinces = ["Biobío", "Coyhaique", "Aysén"]
        for name in expected_provinces:
            with self.subTest(province=name):
                self.assertTrue(Province.objects.filter(name=name).exists())

        self.assertFalse(City.objects.filter(name="Paigüano").exists())
        self.assertFalse(City.objects.filter(name="Calera").exists())
        self.assertFalse(City.objects.filter(name="Llaillay").exists())
        self.assertFalse(City.objects.filter(name="Marchihue").exists())
        self.assertFalse(City.objects.filter(name="Ohiggins").exists())
        self.assertFalse(City.objects.filter(name="Aisén").exists())
        self.assertFalse(Province.objects.filter(name="Coihaique").exists())
        self.assertFalse(Province.objects.filter(name="Bío Bío").exists())

    def test_iso_codes(self):
        regions = list(Region.objects.order_by("number"))
        self.assertEqual(len(regions), 16)
        self.assertEqual(len({region.iso_3166_2_cl for region in regions}), 16)
        self.assertEqual(regions[0].iso_3166_2_cl, "CL-TA")
        self.assertEqual(regions[12].iso_3166_2_cl, "CL-RM")
        self.assertEqual(regions[15].iso_3166_2_cl, "CL-NB")
        for region in regions:
            self.assertRegex(region.iso_3166_2_cl, r"^CL-[A-Z]{2}$")

    def test_codes_are_unique(self):
        duplicate_provinces = (
            Province.objects.values("region_id", "code")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
        )
        duplicate_cities = (
            City.objects.values("province_id", "code")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
        )
        self.assertFalse(duplicate_provinces.exists())
        self.assertFalse(duplicate_cities.exists())

    def test_names_fit_model_max_lengths(self):
        self.assertTrue(all(len(region.name) <= 70 for region in Region.objects.all()))
        self.assertTrue(
            all(len(province.name) <= 100 for province in Province.objects.all())
        )
        self.assertTrue(all(len(city.name) <= 100 for city in City.objects.all()))

    def test_antarctica_has_no_codes(self):
        city = City.objects.get(name="Antártica")
        self.assertIsNone(city.conara_sii)
        self.assertIsNone(city.code_treasury)

    def test_comuna_names_are_not_truncated(self):
        self.assertTrue(City.objects.filter(name="San Vicente de Tagua Tagua").exists())
        self.assertFalse(City.objects.filter(name="San Vicente").exists())
        self.assertTrue(City.objects.filter(name="Macul").exists())
        self.assertFalse(City.objects.filter(name="Macúl").exists())


class FactoryTests(TestCase):
    def test_region_factory(self):
        region = RegionFactory()
        self.assertRegex(region.iso_3166_2_cl, r"^CL-[A-Z]{2}$")
        self.assertEqual(str(region), region.name)

    def test_city_factory_creates_hierarchy(self):
        city = CityFactory()
        self.assertIsNotNone(city.province.region)
        self.assertEqual(str(city), city.name)
        self.assertGreater(city.code, 0)

    def test_factories_create_unique_values(self):
        regions = RegionFactory.create_batch(2)
        self.assertEqual(len({region.code for region in regions}), 2)
        self.assertEqual(len({region.iso_3166_2_cl for region in regions}), 2)

        provinces = ProvinceFactory.create_batch(2)
        self.assertEqual(
            len({(province.region_id, province.code) for province in provinces}),
            2,
        )

        cities = CityFactory.create_batch(2)
        self.assertEqual(
            len({(city.province_id, city.code) for city in cities}),
            2,
        )
