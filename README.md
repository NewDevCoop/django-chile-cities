# Chile Cities

**Chile Cities** is a Django app to load cities and regions of Chile.

Detailed documentation is in the `docs` directory.

## Quick Start

1. Add `chile-cities` to your `INSTALLED_APPS` setting like this:

    ```python
    INSTALLED_APPS = [
        ...,
        "django_chile_cities",
    ]
    ```

2. Run the following command to create the `chile-cities` models:

    ```bash
    python manage.py migrate
    ```

3. Load the seed data by running:

    ```bash
    python manage.py load_chile_cities
    ```

## Usage

1. Import `django_chile_cities` models in your project:

    ```python
    from django_chile_cities.models import Region, Province, City

    class MyTable(models.Model):
        ...
        city = models.ForeignKey(City, on_delete=models.PROTECT)
    ```

2. Access to province and region trough city instance:

    ```python

    my_table_instance.city.province.region

    ```

And that's it, simple, but needed in multiple projects.
