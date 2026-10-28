from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

APP_LABEL = "django_chile_cities"
FROM_MIGRATION = [(APP_LABEL, "0001_initial")]
TO_MIGRATION = [(APP_LABEL, "0002_region_iso_3166_2_cl_and_more")]


class Migration0002Tests(TransactionTestCase):
    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_populates_iso_codes_from_0001(self):
        executor = MigrationExecutor(connection)
        executor.migrate(FROM_MIGRATION)

        old_apps = executor.loader.project_state(FROM_MIGRATION).apps
        OldRegion = old_apps.get_model(APP_LABEL, "Region")
        OldRegion.objects.all().delete()
        for number in range(1, 17):
            OldRegion.objects.create(
                name=f"Region {number}",
                number=number,
                code=number,
            )

        executor = MigrationExecutor(connection)
        executor.migrate(TO_MIGRATION)

        new_apps = executor.loader.project_state(TO_MIGRATION).apps
        NewRegion = new_apps.get_model(APP_LABEL, "Region")
        self.assertEqual(NewRegion.objects.count(), 16)
        self.assertEqual(NewRegion.objects.get(code=1).iso_3166_2_cl, "CL-TA")
        self.assertEqual(NewRegion.objects.get(code=13).iso_3166_2_cl, "CL-RM")
        self.assertEqual(NewRegion.objects.get(code=16).iso_3166_2_cl, "CL-NB")
