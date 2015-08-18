=============
Installation
=============

.. code-block:: console

    pip install django-test-addons

=============
Requirements
=============

Django test addons requires the following:

    1. Python(2.7+)
    2. Django(1.6, 1.7, 1.8)

The following packages are optional:

    * `Mongoengine (0.8.7)+ <http://mongoengine-odm.readthedocs.org/>`_ - Testing support for Mongo DB.
    * `Django Redis (3.8.2)+ <https://pypi.python.org/pypi/django-redis>`_ - Testing support Redis.
    * `Py2neo (2.0.6)+ <https://pypi.python.org/pypi/py2neo>`_  - Testing support for Neo4j graph database.
    * `Python Memcached (1.53)+ <https://pypi.python.org/pypi/python-memcached>`_  - Testing support for Memcache.
    * `Django Rest Framework (3.0.5)+ <http://django-rest-framework.readthedocs.org/en/stable/>`_ - Testing support for Django Rest Framework Apis

.. note:: Package may work perfectly for older versions than specified. It's just that it is not tested with them. So feel free to give it a try.

=========
Tutorial
=========

This tutorial provides a step-by-step description on how to use django test addons for
testing different database systems.

Getting Started
================
It is recommended to have local installation of respective databases just for testing.
Staging or shared database or any database with critical data should never be used in
testing, as database is cleaned after each test is ran. It is recommended to use a separate
settings file for testing.

.. warning:: **Be Careful** to use correct settings for test databases. Using staging or any other database may result in cleaning of the entire database.

If you haven't installed django test addons already, use

.. code-block:: console

    pip install django-test-addons

Testing Mongodb
================

Defining test settings
----------------------

Make sure you have running installation of mongodb and have mongoengine installed.
Just specify the settings for connection to mongodb instance in the settings file.
Define *TEST_MONGO_DATABASE* dict in your test file containing connection information.

**Example**:

Add this code to test settings file -

.. code-block:: python

    TEST_MONGO_DATABASE = {
        'db': 'test',
        'host': ['localhost'],
        'port': 27017,
    }

Make sure to use same test database for all mongo database aliases. To clarify,
say you have following mongo connection settings in your development/production
settings containing two mongodb aliases.

.. code-block:: python

    MONGO_DATABASES = {
        'default': {
            'db': 'main',
            'host': ['193.34.32.11'], # random development server
            'port': 27017,
        },
        'miscellaneous': {
            'DB_NAME': 'misc',
            'HOST': ['193.34.32.11'],
            'PORT': 27017,
        }
    }

In your test settings, make sure to disconnect all existing connections and connect
all mongodb aliases to test db.

.. code-block:: python

    # import MONGO_DATABASES variable from development settings file or just use the
    # variable if you are using single file for testing with some environment settings.

    import mongoengine

    TEST_MONGO_DATABASE = {
        'db': 'test',
        'host': ['localhost'],
        'port': 27017,
    }

    map(lambda connection: mongoengine.connection.disconnect(connection), MONGO_DATABASES.keys())

    MONGO_DATABASES = {connection: TEST_MONGO_DATABASE for connection in MONGO_DATABASES.keys()}

    for connection_name, attrs in MONGO_DATABASES.items():
        mongoengine.connect(**dict(zip(['alias'] + attrs.keys(), [connection_name] + attrs.values())))

Writing Tests
--------------

Just import *MongoTestCase* from test_addons, and inherit test class from it.

**Example**

.. code-block:: python

    import test_addons

    class TestSomething(test_addons.MongoTestCase):

        def test_instantiation(self):
            pass


Testing Memcache
=================

Just specify *CLEAR_CACHE=TRUE* in your test class, if you want to clear cache too(it could be Memcache or Redis or any other caching framework that works with django). You must have CACHES configured in your test settings for this to work.

**Example**

.. code-block:: python

    import test_addons

    class TestSomething(test_addons.MongoTestCase):

        CLEAR_CACHE = True

        def test_instantiation(self):
            pass


Testing Redis
==============

Defining test settings
-----------------------

Make sure you have redis db installed and a running redis server. Just specify
*TEST_CACHES* dictionary in your test settings containing redis connection info.

**Example**:

.. code-block:: python

    TEST_CACHES = {
        'default': {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "127.0.0.1:6379:0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        },
        'redis1': {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "127.0.0.1:6379:1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        },
    }

.. note:: 'django_redis.cache.ShardClient' does not allow flushing all db as of now, so make sure not to use it. Sharding is not required in testing environment anyway.

Writing Tests
--------------
Just import *RedisTestCase* from test_addons, and inherit test class from it.

**Example**

.. code-block:: python

    import test_addons

    class TestSomething(test_addons.RedisTestCase):

        def test_instantiation(self):
            pass


Testing Neo4j Graph database
=============================

Defining test settings
-----------------------

Make sure you have neo4j graph installed and a running neo4j server. Just specify
*NEO4J_TEST_LINK* pointing to ip address of running neo4j server in your test settings file.

**Example**

.. code-block:: python

    NEO4J_TEST_LINK = 'http://localhost:7474/db/data'

.. note:: Since neo4j 2.0, it requires authentication to connection to your neo4j server. Considering it is unnecessary for testing environment, make sure to set 'dbms.security.auth_enabled=false' in your neo4j-server.properties file

Writing Tests
--------------
Just import *Neo4jTestCase* from test_addons, and inherit test class from it.

**Example**

.. code-block:: python

    import test_addons

    class TestSomething(test_addons.Neo4jTestCase):

        def test_instantiation(self):
            pass


Testing Django Rest Framework APIs
===================================
It provides support for testing Django rest framework api's along with one or
more databases.

.. note:: Test cases described above would have worked for apis as well, but they use default Test Client provided by Django, whereas it uses Test Client provided by DRF having some additional facilities like forcing authentication.

Writing Tests
--------------

Just import APITestCase for the specific database you are using (specify settings accordingly).

*Available options are*:

    * APIRedisTestCase
    * APIMongoTestCase
    * APINeo4jTestCase
    * APIMongoRedisTestCase
    * APIRedisMongoNeo4jTestCase

**Example**
Say we want to use test DRF apis along with mongodb.

.. code-block:: python

    import test_addons

    class TestSomething(test_addons.APIMongoTestCase):

        def test_instantiation(self):
            pass


Composite Testing
==================

Often multiple databases are used simulataneously, thereby creating the need of
testing them simulataneously. Just to cater this need, django test addons provide
different combinations of TestCases for respective database combinations.

Composite Test Cases:
-------------------------------

    * MongoNeo4jTestCase
    * MongoRedisTestCase
    * RedisMongoNeo4jTestCase
    * APIRedisTestCase
    * APIMongoTestCase
    * APINeo4jTestCase
    * APIMongoRedisTestCase
    * APIRedisMongoNeo4jTestCase

Facing Issues
=============
Make sure you have defined settings exactly as mentioned. If you still can't resolve the issue, you can use `Django test addons mailing list <https://groups.google.com/forum/#!forum/django-test-addons>`_ or raise an issue on `github <https://github.com/hspandher/django-test-addons>`_  or just mail me directly at *hspandher@outlook.com*


=========
Changelog
=========

Changes in 0.3.5
=======================
- Fix APIClient bug. It was not working due to incorrect name error

==========
Community
==========

To get help with using MongoEngine, use the `Django test addons mailing list <https://groups.google.com/forum/#!forum/django-test-addons>`_ , raise an issue on `github <https://github.com/hspandher/django-test-addons>`_  or just mail me directly at *hspandher@outlook.com*.

=============
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

========
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

===================
Indices and tables
===================

* :ref:`genindex`
* :ref:`search`

