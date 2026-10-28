# Changelog

## [2.0.0] - 2026-10-28

### Added
- `Region.iso_3166_2_cl` field with ISO 3166-2:CL codes (e.g. `CL-RM`)
- Unique constraints on `Region.code`, `Province.(region, code)` and
  `City.(province, code)`
- `load_chile_cities` command options: `--force` (synchronize existing data and
  remove stale records) and `--region NUMBER` (partial load)
- `--force` preserves primary keys and refuses to delete records referenced by
  other models with `on_delete=PROTECT`
- Django admin integration for Region, Province and City
- `__str__` and `Meta` (verbose names, ordering) on all models
- Expanded test suite covering the command, models, data integrity, factories,
  migration `0002` and `--force` reference safety
- GitHub Actions CI matrix (Django 4.2/5.2/6.0/6.1, Python 3.10–3.14) with
  lint, migration check, build and wheel smoke test
- `factory_boy` factories for all models, available through the `factories`
  extra
- `MANIFEST.in` entries for the changelog and test projects

### Changed
- Official region names (e.g. "Región Metropolitana de Santiago", "Región de
  O'Higgins", "Región del Biobío", "Región de La Araucanía"). Region 6 uses the
  short name; its full official name is "Región del Libertador General
  Bernardo O'Higgins"
- `City.name` and `Province.name` max_length increased to 100
- Command output now reports loaded counts and, with `--force`, removed stale
  records
- Packaging migrated to PEP 621 (`pyproject.toml`) with `setuptools>=77` and
  PEP 639 license metadata
- Requires Django >= 4.2 and Python >= 3.10
- Tests moved out of the installed package into `tests/`
- The test project now includes an app with a `PROTECT` foreign key to `City`
  for release-safety tests

### Fixed
- `factories.py`: wrong app label (`chile_cities` → `django_chile_cities`) and
  nonexistent field; factories now use sequences so they can create multiple
  objects
- Truncated comuna name "San Vicente" → "San Vicente de Tagua Tagua"
- Misspelled comuna "Macúl" → "Macul"
- Corrected comuna and province names: "Paigüano" → "Paihuano",
  "Calera" → "La Calera", "Llaillay" → "Llay-Llay",
  "Marchihue" → "Marchigüe", "Ohiggins" → "O'Higgins",
  "Aisén" → "Aysén", "Bío Bío" → "Biobío", "Coihaique" → "Coyhaique",
  "San Pedro de La Paz" → "San Pedro de la Paz",
  "Padre Las Casas" → "Padre las Casas" and
  "San Juan de La Costa" → "San Juan de la Costa"
- Typo in command success message
- Test suite configuration: wrong `DJANGO_SETTINGS_MODULE` and missing test
  collection pattern (tests never ran)
- Migration `0002` now validates duplicate codes and missing ISO mappings
  before adding unique constraints, with an actionable error message

### Removed
- Dead `views.py`
- Legacy `setup.py`, `setup.cfg` and duplicate `README.rst`

### Upgrade notes
- Run `python manage.py migrate` and then `python manage.py load_chile_cities`.
  A normal load updates names by code and preserves primary keys.
- Migration `0002` expects the 16 standard regions (codes 1-16). Custom regions
  outside that range, or duplicate region/province/city codes, must be cleaned
  before migrating.
- If your installation used the old `chile_cities` module name, update
  `INSTALLED_APPS` and review the migration history before migrating.

## [1.0.1] - 2025-06-03

- Initial PyPI release with regions, provinces and cities fixtures.
