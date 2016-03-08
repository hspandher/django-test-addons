
==============================================
Django Test Addons's documentation!
==============================================

**Django test addons** provides support for testing different databases along with
Django Web Framework. By default, django provides support for relational databases
only. Since no-sql database systems are being widely used in django community, testing
support for them is vital. As of now, django test addons provides testing support
for Mongodb, Redis, Neo4j, Memcache, Django Rest Framework APIs only. Support for more
databases might be provided in future.

Installation
=============

.. code-block:: console

    pip install django-test-addons

Requirements
=============

Django test addons requires the following:

    1. Python(2.7+)
    2. Django(1.6, 1.7, 1.8, 1.9)

The following packages are optional:

    * `Mongoengine (0.8.7)+ <http://mongoengine-odm.readthedocs.org/>`_ - Testing support for Mongo DB.
    * `Django Redis (3.8.2)+ <https://pypi.python.org/pypi/django-redis>`_ - Testing support Redis.
    * `Py2neo (2.0.6)+ <https://pypi.python.org/pypi/py2neo>`_  - Testing support for Neo4j graph database.
    * `Python Memcached (1.53)+ <https://pypi.python.org/pypi/python-memcached>`_  - Testing support for Memcache.
    * `Django Rest Framework (3.0.5)+ <http://django-rest-framework.readthedocs.org/en/stable/>`_ - Testing support for Django Rest Framework Apis

.. note:: Package may work perfectly for older versions than specified. It's just that it is not tested with them. So feel free to give it a try.


User Guide
===========

.. toctree::
   :maxdepth: 3
   :numbered:

   main


=========
Changelog
=========

Changes in version 1.0
=======================
- Support for Django 1.9 along with Python 3

Changes in version 0.3.6
=======================
- Updated pypi download url to the latest version (Minor update)

Changes in version 0.3.5
=======================
- Fix APIClient bug. It was not working due to incorrect name error (use of self instead of cls)


Community
==========

To get help with using MongoEngine, use the `Django test addons mailing list <https://groups.google.com/forum/#!forum/django-test-addons>`_ , raise an issue on `github <https://github.com/hspandher/django-test-addons>`_  or just mail me directly at *hspandher@outlook.com*.


Contributing
=============

**Yes please!**  I am always looking for contributions, additions and improvements.
Support for testing more databases is specifically required.

The source is available on `GitHub <https://github.com/hspandher/django-test-addons>`_
and contributions are always encouraged. Contributions can be as simple as
minor tweaks to this documentation, the website or the core.

To contribute, fork the project on
`GitHub <https://github.com/hspandher/django-test-addons>`_ and send a
pull request.


License
========
The MIT License (MIT)

Copyright (c) 2015, Hakampreet Singh Pandher

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Indices and tables
===================

* :ref:`genindex`
* :ref:`search`

