# inbuild python imports
from abc import ABCMeta

# inbuilt django imports
from django.test import SimpleTestCase, TestCase, LiveServerTestCase
from django.core.cache import cache
# from django_redis import get_redis_connection

# third party imports
from django.conf import settings
from mongoengine.connection import connect, get_connection, get_db

# inter-app imports

# local imports
from .utils import disconnect

try:
    from rest_framework.test import APIClient
except ImportError:
    APIClient = None

try:
    from py2neo import neo4j
except ImportError:
    neo4j = None


REDIS_DATABASES = ['redis0', 'redis1', 'redis2', 'redis3']



class MongoTestMixin(object):

    """ Mixin to enforce use of mongodb, instead of relational database, in testing  """

    @classmethod
    def setUpClass(cls):
        cls.ensure_valid_configuration()
        super(MongoTestMixin, cls).setUpClass()

    @classmethod
    def ensure_valid_configuration(self):
        try:
            self.MONGO_DB_SETTINGS = settings.TEST_MONGO_DATABASE
        except:
            raise AttributeError("settings file has no attribute 'TEST_MONGO_SETTINGS'. Specify TEST_MONGO_SETTINGS in settings file. E.g: {'DB_NAME': 'test', 'HOST': ['localhost'], 'PORT': 27017}")

    def _pre_setup(self):
        """ (MongoTestMixin) -> (NoneType)
        create a new mongo connection.

        Note:- It explicitly uses Class name to call methods, since the calling overriden
        _setup_database and _teardown_database is not required behaviour, as it would
        not work with other Test Mixins like Redis or Neo4j, which have their own _setup_database
        and _teardown_database
        """
        SimpleTestCase._pre_setup(self)

        MongoTestMixin._setup_database(self)

    def _post_teardown(self):
        SimpleTestCase._post_teardown(self)

        MongoTestMixin._teardown_database(self)

    def _setup_database(self):
        disconnect() # disconnect any existing connections built in settings
        connect(self.MONGO_DB_SETTINGS['db'], port = self.MONGO_DB_SETTINGS['port'])

    def _teardown_database(self):
        connection = get_connection()
        connection.drop_database(self.MONGO_DB_SETTINGS['db'])
        disconnect()

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

    def __enter__(self):
        """ (_AssertNumQueries) -> (int)
        drop any existing profiling data,
        set profiling_level to profile everything, and issue a request to profile.find which
        instantiates the change.
        """
        self.db = get_db()
        self.db.set_profiling_level(0)
        self.db.system.profile.drop()
        self.db.set_profiling_level(2)
        self.db.system.profile.find()

    def __exit__(self, type, value, traceback):
        actual_num_of_queries = self._count()
        self.test_case.assertEqual(actual_num_of_queries, self.num_of_queries, "{0} query executed, {1} query expected".format(actual_num_of_queries, self.num_of_queries))

        self.db.set_profiling_level(0)

    def _count(self):
        """ (_AssertNumQueries) -> (int)
        return number_of_queries executed in context.

        1 is subtracted, since any request to db.system.profile is itself a query.
        """
        return self.db.system.profile.find().count() - 1

class _AssertMaxNumQueries(_AssertNumQueries):

    """ Context Managers to count number of mongodb queries and assert max limit """

    def __exit__(self, type, value, traceback):
        actual_num_of_queries = self._count()
        self.test_case.assertLessEqual(actual_num_of_queries, self.num_of_queries, "{0} query executed, maximum {1} query expected".format(actual_num_of_queries, self.num_of_queries))

        self.db.set_profiling_level(0)


class Neo4jTestMixin(object):

    """ Mixin to enforce use of mongodb, instead of relational database, in testing  """

    def ensure_valid_configuration(self):
        if not neo4j:
            raise ImportError('Neo4j package must be installed to use Neo4j test cases.')

        try:
            NEO4J_LINK = settings.NEO4J_TEST_LINK
        except AttributeError:
            raise AttributeError("settings file has no attribute 'NEO4J_TEST_LINK'. Specify NEO4J_TEST_LINK in settings file. E.g: NEO4J_TEST_LINK = 'http://localhost:7474/db/data'")

    def _pre_setup(self):
        SimpleTestCase._pre_setup(self)

        Neo4jTestMixin._setup_database(self)

    def _post_teardown(self):
        Neo4jTestMixin._teardown_database(self)

    def _setup_database(self):
        self.graph_db = neo4j.Graph(self.NEO4J_LINK)

    def _teardown_database(self):
        SimpleTestCase._post_teardown(self)

        query = '''
        START n = node(*)
        OPTIONAL MATCH n-[r]-()
        DELETE n, r;
        '''

        self.graph_db.cypher.execute(query)


class MongoNeo4jTestMixin(Neo4jTestMixin, MongoTestMixin):

    """ Mixin to enforce use of mongodb, instead of relational database, in testing  """


    def _pre_setup(self):
        Neo4jTestMixin._pre_setup(self)
        MongoTestMixin._pre_setup(self)

    def _post_teardown(self):
        Neo4jTestMixin._post_teardown(self)
        MongoTestMixin._post_teardown(self)


class RedisTestMixin(object):

    def ensure_valid_configuration(self):
        try:
            from redis_cache import get_redis_connection
            self.redis_connections = map(lambda connection_name: get_redis_connection(connection_name), settings.TEST_CACHES.keys())
        except:
            raise AttributeError("settings file doesn't have redis configuration defined.")

    def _pre_setup(self):
        SimpleTestCase._pre_setup(self)

        RedisTestMixin._setup_database(self)

    def _post_teardown(self):
        RedisTestMixin._teardown_database(self)

    def _setup_database(self):
        pass

    def _teardown_database(self):
        map(lambda connection: connection.flushdb(), self.redis_connections)


class MongoRedisTestMixin(RedisTestMixin, MongoTestMixin):

    def _pre_setup(self):
        MongoTestMixin._pre_setup(self)
        RedisTestMixin._pre_setup(self)

    def _post_teardown(self):
        MongoTestMixin._post_teardown(self)
        RedisTestMixin._post_teardown(self)


class RedisMongoNeo4jTestMixin(RedisTestMixin, Neo4jTestMixin, MongoTestMixin):

    """ Mixin to enforce use of mongodb, instead of relational database, in testing  """

    def _pre_setup(self):
        Neo4jTestMixin._pre_setup(self)
        MongoTestMixin._pre_setup(self)
        RedisTestMixin._pre_setup(self)

    def _post_teardown(self):
        Neo4jTestMixin._post_teardown(self)
        MongoTestMixin._post_teardown(self)
        RedisTestMixin._post_teardown(self)


class MongoTestCase(MongoTestMixin, SimpleTestCase):

    """ TestCase that creates a mongo collection and clears it after each test """
    pass


class MongoLiveServerTestCase(MongoTestMixin, LiveServerTestCase):

    """ TestCase that runs liveserver using mongodb instead of relational database  """
    pass

class Neo4jTestCase(Neo4jTestMixin, TestCase):

    pass


class MongoNeo4jTestCase(MongoNeo4jTestMixin, TestCase):

    pass


class RedisTestCase(RedisTestMixin, TestCase):

    pass


class MongoRedisTestCase(MongoRedisTestMixin, TestCase):

    pass


class RedisMongoNeo4jTestCase(RedisMongoNeo4jTestMixin, TestCase):

    pass

class ApiTestMixin(object):

    def ensure_valid_configuration(self):
        if not self.client_class:
            raise ImportError('django rest framework is required to use API test cases.')


class APIRedisTestCase(RedisTestCase):

    client_class = APIClient


class APIMongoTestCase(MongoTestCase):

    client_class = APIClient


class APINeo4jTestCase(Neo4jTestCase):

    client_class = APIClient


class APIMongoRedisTestCase(MongoRedisTestCase):

    client_class = APIClient


class APIRedisMongoNeo4jTestCase(RedisMongoNeo4jTestCase):

    client_class = APIClient




