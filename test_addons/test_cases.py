# inbuild python imports

# inbuilt django imports
from django.test import LiveServerTestCase

# third party imports

# inter-app imports

# local imports
import mixins
from mixins import SimpleTestCase


class MongoTestCase(mixins.MongoTestMixin, SimpleTestCase):

    """ TestCase that creates a mongo collection and clears it after each test """
    pass


class MongoLiveServerTestCase(mixins.MongoTestMixin, LiveServerTestCase):

    """ TestCase that runs liveserver using mongodb instead of relational database  """
    pass

class Neo4jTestCase(mixins.Neo4jTestMixin, SimpleTestCase):

    pass


class MongoNeo4jTestCase(mixins.MongoNeo4jTestMixin, mixins.SimpleTestCase):

    pass


class RedisTestCase(mixins.RedisTestMixin, mixins.SimpleTestCase):

    pass


class MongoRedisTestCase(mixins.MongoRedisTestMixin, mixins.SimpleTestCase):

    pass


class RedisMongoNeo4jTestCase(mixins.RedisMongoNeo4jTestMixin, mixins.SimpleTestCase):

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




