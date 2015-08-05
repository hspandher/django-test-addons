# inbuild python imports

# inbuilt django imports
from django.test import SimpleTestCase

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


class SimpleTestCase(SimpleTestCase):

    _overridden_settings = None
    _modified_settings = None

    @classmethod
    def setUpClass(cls):
        super(SimpleTestCase, cls).setUpClass()

        if cls._overridden_settings:
            cls._cls_overridden_context = override_settings(**cls._overridden_settings)
            cls._cls_overridden_context.enable()
        if cls._modified_settings:
            cls._cls_modified_context = modify_settings(cls._modified_settings)
            cls._cls_modified_context.enable()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, '_cls_modified_context'):
            cls._cls_modified_context.disable()
            delattr(cls, '_cls_modified_context')
        if hasattr(cls, '_cls_overridden_context'):
            cls._cls_overridden_context.disable()
            delattr(cls, '_cls_overridden_context')

        super(SimpleTestCase, cls).tearDownClass()


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
            raise AttributeError("settings file has no attribute 'TEST_MONGO_SETTINGS'. Specify TEST_MONGO_SETTINGS in settings file. E.g: {'DB_NAME': 'test', 'HOST': ['localhost'], 'PORT': 27017}")

        if cls.CLEAR_CACHE:
            if not cache:
                raise AttributeError("CACHE settings are not configured in settings, yet.")

        super(MongoTestMixin, cls).setUpClass()

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
        utils.disconnect() # disconnect any existing connections built in settings
        mongoengine.connection.connect(self.MONGO_DB_SETTINGS['db'], port = self.MONGO_DB_SETTINGS['port'])

    def _teardown_database(self):
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


class RedisTestMixin(object):

    @classmethod
    def setUpClass(cls):
        try:
            from django_redis import get_redis_connection
            cls.redis_connections = map(lambda connection_name: get_redis_connection(connection_name), settings.TEST_CACHES.keys())
        except ImportError as exc:
            raise ImportError("django_redis must be installed to use RedisTestCase. Exception details:- {0}".format(repr(exc)))
        except AttributeError as exc:
            raise AttributeError("settings file doesn't have redis configuration defined. Define TEST_CACHES in test settings file. Exception details:- {0}".format(repr(exc)))

        super(RedisTestMixin, cls).setUpClass()

    def _pre_setup(self):
        SimpleTestCase._pre_setup(self)

        RedisTestMixin._setup_database(self)

    def _post_teardown(self):
        RedisTestMixin._teardown_database(self)

    def _setup_database(self):
        pass

    def _teardown_database(self):
        map(lambda connection: connection.flushdb(), self.redis_connections)


class MongoNeo4jTestMixin(Neo4jTestMixin, MongoTestMixin):

    """ Mixin to enforce use of mongodb, instead of relational database, in testing  """


    def _pre_setup(self):
        Neo4jTestMixin._pre_setup(self)
        MongoTestMixin._pre_setup(self)

    def _post_teardown(self):
        Neo4jTestMixin._post_teardown(self)
        MongoTestMixin._post_teardown(self)


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


class ApiTestMixin(object):

    client_class = APIClient

    @classmethod
    def setUpClass(cls):
        if not self.client_class:
            raise ImportError('django rest framework is required to use API test cases.')

        super(ApiTestMixin, cls).setUpClass()
