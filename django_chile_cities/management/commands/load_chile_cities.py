import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import ProtectedError, RestrictedError

from django_chile_cities.models import City, Province, Region

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


class Command(BaseCommand):
    help = "Load Chile regions, provinces and cities into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Update existing records and delete records that are no longer "
                "in the fixtures (existing IDs are preserved)"
            ),
        )
        parser.add_argument(
            "--region",
            type=int,
            metavar="NUMBER",
            help="Load only the region with the given number (1-16)",
        )

    def handle(self, *args, **options):
        force = options["force"]
        region_number = options["region"]

        regions = self.read_fixture("region")
        provinces = self.read_fixture("province")
        cities = self.read_fixture("city")

        if region_number is not None:
            regions, provinces, cities = self.filter_by_region(
                region_number, regions, provinces, cities
            )

        with transaction.atomic():
            region_map = self.load_regions(regions)
            province_map = self.load_provinces(provinces, region_map)
            self.load_cities(cities, province_map)
            removed = (
                self.delete_stale_records(regions, provinces, cities, region_number)
                if force
                else 0
            )

        message = (
            f"Loaded {len(regions)} regions, {len(provinces)} provinces "
            f"and {len(cities)} cities successfully."
        )
        if force:
            message += f" Removed {removed} stale records."
        self.stdout.write(self.style.SUCCESS(message))

    def read_fixture(self, name):
        path = FIXTURES_DIR / f"{name}.json"
        try:
            with open(path, encoding="utf-8") as fixture_file:
                return json.load(fixture_file)
        except FileNotFoundError as exc:
            raise CommandError(f"Fixture not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON in fixture: {path}") from exc

    def filter_by_region(self, region_number, regions, provinces, cities):
        selected_regions = [
            record for record in regions if record["fields"]["number"] == region_number
        ]
        if not selected_regions:
            raise CommandError(f"No region found with number {region_number}.")
        region_pks = {record["pk"] for record in selected_regions}
        selected_provinces = [
            record for record in provinces if record["fields"]["region"] in region_pks
        ]
        province_pks = {record["pk"] for record in selected_provinces}
        selected_cities = [
            record for record in cities if record["fields"]["province"] in province_pks
        ]
        return selected_regions, selected_provinces, selected_cities

    def load_regions(self, records):
        region_map = {}
        for record in records:
            fields = record["fields"]
            region, _ = Region.objects.update_or_create(
                code=fields["code"],
                defaults={
                    "name": fields["name"],
                    "number": fields["number"],
                    "iso_3166_2_cl": fields["iso_3166_2_cl"],
                },
            )
            region_map[record["pk"]] = region
        return region_map

    def load_provinces(self, records, region_map):
        province_map = {}
        for record in records:
            fields = record["fields"]
            try:
                region = region_map[fields["region"]]
            except KeyError as exc:
                raise CommandError(
                    f"Province {fields['name']!r} references unknown region "
                    f"fixture pk {fields['region']}."
                ) from exc
            province, _ = Province.objects.update_or_create(
                region=region,
                code=fields["code"],
                defaults={"name": fields["name"]},
            )
            province_map[record["pk"]] = province
        return province_map

    def load_cities(self, records, province_map):
        for record in records:
            fields = record["fields"]
            try:
                province = province_map[fields["province"]]
            except KeyError as exc:
                raise CommandError(
                    f"City {fields['name']!r} references unknown province "
                    f"fixture pk {fields['province']}."
                ) from exc
            City.objects.update_or_create(
                province=province,
                code=fields["code"],
                defaults={
                    "name": fields["name"],
                    "conara_sii": fields.get("conara_sii"),
                    "code_treasury": fields.get("code_treasury"),
                    "hashtag": fields.get("hashtag", ""),
                },
            )

    def delete_stale_records(self, regions, provinces, cities, region_number):
        region_codes = {record["fields"]["code"] for record in regions}
        region_code_by_fixture_pk = {
            record["pk"]: record["fields"]["code"] for record in regions
        }
        province_keys = {
            (
                region_code_by_fixture_pk[record["fields"]["region"]],
                record["fields"]["code"],
            )
            for record in provinces
        }
        province_code_by_fixture_pk = {
            record["pk"]: record["fields"]["code"] for record in provinces
        }
        province_region_by_fixture_pk = {
            record["pk"]: record["fields"]["region"] for record in provinces
        }
        city_keys = {
            (
                region_code_by_fixture_pk[
                    province_region_by_fixture_pk[city["fields"]["province"]]
                ],
                province_code_by_fixture_pk[city["fields"]["province"]],
                city["fields"]["code"],
            )
            for city in cities
        }

        if region_number is None:
            city_queryset = City.objects.all()
            province_queryset = Province.objects.all()
            region_queryset = Region.objects.all()
        else:
            city_queryset = City.objects.filter(province__region__code__in=region_codes)
            province_queryset = Province.objects.filter(region__code__in=region_codes)
            region_queryset = Region.objects.none()

        stale_cities = [
            city
            for city in city_queryset.select_related("province__region")
            if (city.province.region.code, city.province.code, city.code)
            not in city_keys
        ]
        stale_provinces = [
            province
            for province in province_queryset.select_related("region")
            if (province.region.code, province.code) not in province_keys
        ]
        stale_regions = [
            region for region in region_queryset if region.code not in region_codes
        ]

        city_ids = [city.pk for city in stale_cities]
        province_ids = [province.pk for province in stale_provinces]
        region_ids = [region.pk for region in stale_regions]

        try:
            if city_ids:
                City.objects.filter(pk__in=city_ids).delete()
            if province_ids:
                Province.objects.filter(pk__in=province_ids).delete()
            if region_ids:
                Region.objects.filter(pk__in=region_ids).delete()
        except (ProtectedError, RestrictedError) as exc:
            raise CommandError(
                "Cannot remove stale records because they are referenced by "
                "other models. Remove those references, delete the stale "
                "records manually, or run the command without --force."
            ) from exc

        return len(city_ids) + len(province_ids) + len(region_ids)
