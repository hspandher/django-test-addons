# inbuild python imports

# inbuilt django imports

# third party imports
from django.conf import settings

# inter-app imports

# local imports
from . import utils

try:
    import mongoengine
except ImportError:
    mongoengine = None

try:
    from django.core.cache import cache
except ImportError:
    cache = None

try:
    from rest_framework.test import APIClient
except ImportError:
    APIClient = None

try:
    from py2neo import neo4j
except ImportError:
    neo4j = None


class MongoTestMixin(object):

    """ Mixin to enforce use of mongodb, instead of relational database, in testing  """

    CLEAR_CACHE = False

    @classmethod
    def setUpClass(cls):
        if not mongoengine:
            raise ImportError("Mongoengine must be installed to use MongoTestCase.")

        try:
            cls.MONGO_DB_SETTINGS = settings.TEST_MONGO_DATABASE
        except:
            raise AttributeError("settings file has no attribute 'TEST_MONGO_DATABASE'. Specify TEST_MONGO_DATABASE in settings file. E.g: {'DB_NAME': 'test', 'HOST': ['localhost'], 'PORT': 27017}")

        if cls.CLEAR_CACHE:
            if not cache:
                raise AttributeError("CACHE settings are not configured in settings, yet.")

        super(MongoTestMixin, cls).setUpClass()

    def _pre_setup(self):
        """ (MongoTestMixin) -> (NoneType)
        create a new mongo connection.
        """
        super(MongoTestMixin, self)._pre_setup()

        utils.disconnect()
        mongoengine.connection.connect(self.MONGO_DB_SETTINGS['db'], host = self.MONGO_DB_SETTINGS['host'], port = self.MONGO_DB_SETTINGS['port'])

    def _post_teardown(self):
        super(MongoTestMixin, self)._post_teardown()

        connection = mongoengine.connection.get_connection()
        connection.drop_database(self.MONGO_DB_SETTINGS['db'])
        utils.disconnect()

        if self.CLEAR_CACHE:
            cache.clear()

    def assertNumQueries(self, num, func = None, *args, **kwargs):
        context_manager = _AssertNumQueries
        return self._assert_num_queries(context_manager, num, func, *args, **kwargs)

    def assertMaxNumQueries(self, num, func = None, *args, **kwargs):
        context_manager = _AssertMaxNumQueries
        return self._assert_num_queries(context_manager, num, func, *args, **kwargs)

    def _assert_num_queries(self, context_manager, num, func, *args, **kwargs):
        context = context_manager(self, num)

        if func is None:
            return context

        with context:
            func(*args, **kwargs)


class _AssertNumQueries(object):
    """ Context Manager to count number of mongodb queries and assert equality to expected value """

    def __init__(self, test_case, num_of_queries):
        self.test_case = test_case
        self.num_of_queries = num_of_queries
        self.db = mongoengine.connection.get_db()

    def __enter__(self):
        """ (_AssertNumQueries) -> (int)
        drop any existing profiling data,
        set profiling_level to profile everything, and issue a request to profile.find which
        instantiates the change.
        """
        self.db.set_profiling_level(0)
        self.db.system.profile.drop()
        self.db.set_profiling_level(2)
        return self

    def __exit__(self, type, value, traceback):
        actual_num_of_queries = self._count()
        self.test_case.assertEqual(actual_num_of_queries, self.num_of_queries, "{0} query executed, {1} query expected".format(actual_num_of_queries, self.num_of_queries))

        self.db.set_profiling_level(0)

    def _count(self):
        """ (_AssertNumQueries) -> (int)
        return number_of_queries executed in context.

        1 is subtracted, since any request to db.system.profile is itself a query.
        """
        ignore_query  = {
            "command.count": {"$ne": "system.profile"},
            "ns": {"$ne": "{0}.system.indexes".format(self.db.name)}
        }

        count = self.db.system.profile.find(ignore_query).count()

        return count


class _AssertMaxNumQueries(_AssertNumQueries):

    """ Context Managers to count number of mongodb queries and assert max limit """

    def __exit__(self, type, value, traceback):
        actual_num_of_queries = self._count()
        self.test_case.assertLessEqual(actual_num_of_queries, self.num_of_queries, "{0} query executed, maximum {1} query expected".format(actual_num_of_queries, self.num_of_queries))

        self.db.set_profiling_level(0)


class Neo4jTestMixin(object):

    """ Mixin to enforce use of mongodb, instead of relational database, in testing  """

    @classmethod
    def setUpClass(cls):
        if not neo4j:
            raise ImportError('Neo4j package must be installed to use Neo4j test cases.')
        try:
            cls.NEO4J_LINK = settings.NEO4J_TEST_LINK
        except AttributeError:
            raise AttributeError("settings file has no attribute 'NEO4J_TEST_LINK'. Specify NEO4J_TEST_LINK in settings file. E.g: NEO4J_TEST_LINK = 'http://localhost:7474/db/data'")

        super(Neo4jTestMixin, cls).setUpClass()

    def _pre_setup(self):
        super(Neo4jTestMixin, self)._pre_setup()

        self.graph_db = neo4j.Graph(self.NEO4J_LINK)

    def _post_teardown(self):
        super(Neo4jTestMixin, self)._post_teardown()

        query = '''
        START n = node(*)
        OPTIONAL MATCH n-[r]-()
        DELETE n, r;
        '''

        self.graph_db.cypher.execute(query)


class RedisTestMixin(object):

    @classmethod
    def setUpClass(cls):
        try:
            from django_redis import get_redis_connection
            cls.redis_connections = map(lambda connection_name: get_redis_connection(connection_name), settings.CACHES.keys())
        except ImportError as exc:
            raise ImportError("django_redis must be installed to use RedisTestCase. Exception details:- {0}".format(repr(exc)))
        except AttributeError as exc:
            raise AttributeError("settings file doesn't have redis configuration defined. Define CACHES in test settings file. Exception details:- {0}".format(repr(exc)))

        super(RedisTestMixin, cls).setUpClass()

    def _post_teardown(self):
        super(RedisTestMixin, self)._post_teardown()
        map(lambda connection: connection.flushdb(), self.redis_connections)


class ApiTestMixin(object):

    client_class = APIClient

    @classmethod
    def setUpClass(cls):
        if not cls.client_class:
            raise ImportError('django rest framework is required to use API test cases.')

        super(ApiTestMixin, cls).setUpClass()
