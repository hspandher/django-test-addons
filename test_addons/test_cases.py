# inbuild python imports

# inbuilt django imports
from django.test import LiveServerTestCase, SimpleTestCase

# third party imports

# inter-app imports

# local imports
from . import mixins


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


class MongoTestCase(mixins.MongoTestMixin, SimpleTestCase):

    """ TestCase that creates a mongo collection and clears it after each test """
    pass


class MongoLiveServerTestCase(mixins.MongoTestMixin, LiveServerTestCase):

    """ TestCase that runs liveserver using mongodb instead of relational database  """
    pass

class Neo4jTestCase(mixins.Neo4jTestMixin, SimpleTestCase):

    pass


class MongoNeo4jTestCase(mixins.Neo4jTestMixin, mixins.MongoTestMixin, SimpleTestCase):

    pass


class RedisTestCase(mixins.RedisTestMixin, SimpleTestCase):

    pass


class MongoRedisTestCase(mixins.RedisTestMixin, mixins.MongoTestMixin, SimpleTestCase):

    pass


class RedisMongoNeo4jTestCase(mixins.Neo4jTestMixin, mixins.RedisTestMixin, mixins.MongoTestMixin, SimpleTestCase):

    pass


class APIRedisTestCase(mixins.ApiTestMixin, RedisTestCase):

    pass


class APIMongoTestCase(mixins.ApiTestMixin, MongoTestCase):

    pass


class APINeo4jTestCase(mixins.ApiTestMixin, Neo4jTestCase):

    pass


class APIMongoRedisTestCase(mixins.ApiTestMixin, MongoRedisTestCase):

    pass


class APIRedisMongoNeo4jTestCase(mixins.ApiTestMixin, RedisMongoNeo4jTestCase):

    pass




