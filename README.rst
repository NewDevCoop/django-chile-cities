=====
Chile Cities
=====

Chile Cities is a Django app to load cities and regions of Chile.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "chile-cities" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "chile-cities",
    ]


2. Run ``python manage.py migrate`` to create the chile-cities models.

3. Run ``python manage.py load-chile-cities`` to load seed data.