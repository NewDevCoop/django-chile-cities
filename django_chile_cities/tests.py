from io import StringIO
from django.test import TestCase
from django.core.management import call_command


class Test(TestCase):

    def test_command(self):

        out = StringIO()
        call_command("load_chile_cities", stdout=out)
        self.assertIn("Script executed Succesfully.", out.getvalue())
