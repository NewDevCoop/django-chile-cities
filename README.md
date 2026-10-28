# Chile Cities

**Chile Cities** is a Django app to load regions, provinces and cities (comunas)
of Chile.

## Features

- 16 regions, 56 provinces and 346 comunas of Chile
- ISO 3166-2:CL codes for regions (e.g. `CL-RM`)
- SII CONARA and Treasury codes for comunas
- Idempotent `load_chile_cities` management command
- Safe `--force` sync that preserves existing primary keys
- Django admin integration
- `factory_boy` factories for testing
- No GeoDjango required

## Requirements

- Python 3.10+
- Django 4.2+

CI tests Django 4.2, 5.2, 6.0 and 6.1 on Python 3.10-3.14, using the versions
supported by each Django release.

## Installation

```bash
pip install django-chile-cities
```

If you want to use the bundled factories, install the optional extra:

```bash
pip install "django-chile-cities[factories]"
```

## Quick Start

1. Add `django_chile_cities` to your `INSTALLED_APPS` setting:

    ```python
    INSTALLED_APPS = [
        ...,
        "django_chile_cities",
    ]
    ```

2. Run migrations to create the models:

    ```bash
    python manage.py migrate
    ```

3. Load the seed data:

    ```bash
    python manage.py load_chile_cities
    ```

## Usage

Import the models in your project:

```python
from django_chile_cities.models import Region, Province, City


class MyTable(models.Model):
    ...
    city = models.ForeignKey(City, on_delete=models.PROTECT)
```

Access the province and region through a city instance:

```python
my_table_instance.city.province.region
```

### Models

| Model | Fields | Notes |
| --- | --- | --- |
| `Region` | `name`, `number`, `code`, `iso_3166_2_cl` | `code` and `iso_3166_2_cl` are unique |
| `Province` | `name`, `region`, `code` | `code` is unique per region |
| `City` | `name`, `province`, `code`, `conara_sii`, `code_treasury`, `hashtag` | `code` is unique per province |

`City` represents a comuna. `City.code` is the comuna code used by this
dataset; `conara_sii` and `code_treasury` are the SII CONARA and Treasury
codes. `Antártica` has no CONARA or Treasury code, so both fields are `NULL`
for that comuna.

### Management command

```bash
# Load all data (idempotent: safe to run multiple times)
python manage.py load_chile_cities

# Update existing data and remove records that are no longer in the fixtures
python manage.py load_chile_cities --force

# Load only one region by number (1-16)
python manage.py load_chile_cities --region 13

# Sync only one region
python manage.py load_chile_cities --region 13 --force
```

`--force` updates existing rows and deletes only stale rows. It preserves the
primary keys of records that still exist, so foreign keys from your own models
keep working. If a stale row is referenced by another model with
`on_delete=PROTECT`, the command fails with an actionable error instead of
deleting user data.

## Data source

Data is based on the official political-administrative division of Chile
(SUBDERE/INE) and the SII CONARA codes. The dataset was reviewed in October
2026. Region 6 uses the short name "Región de O'Higgins"; its full official
name is "Región del Libertador General Bernardo O'Higgins". If you need a
specific revision, verify the names and codes against the official sources
before relying on them.

## Upgrading from 1.x

1. Upgrade the package:

    ```bash
    pip install --upgrade django-chile-cities
    ```

2. Apply the new migrations:

    ```bash
    python manage.py migrate
    ```

3. Refresh the data:

    ```bash
    python manage.py load_chile_cities
    ```

The 2.0.0 migration adds ISO 3166-2:CL codes and unique constraints. It expects
the standard regions with codes 1-16. If your database contains custom regions
outside that range or duplicate region/province/city codes, the migration stops
with an explicit error; clean the data before migrating.

`--force` is not required for a normal upgrade: `load_chile_cities` updates
names by code without changing primary keys.

If your installation used the old `chile_cities` module name, update
`INSTALLED_APPS` and review your migration history before applying the
migrations.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
python -m build
twine check dist/*
```

## License

BSD-3-Clause
