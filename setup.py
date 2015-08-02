from distutils.core import setup

setup(
	name = 'django-test-addons',
	packages = ['test_addons'],
	version = '0.3.3',
	description = 'Library to provide support for testing multiple database system like Mongo, Redis, Neo4j along with django.',
	author = 'Hakampreet Singh Pandher',
	author_email = 'hspandher@outlook.com',
	url = 'https://github.com/hspandher/django-test-utils',
	download_url = 'https://github.com/hspandher/django-test-utils/tarball/0.1',
	keywords = ['testing', 'django', 'mongo', 'redis', 'neo4j', 'TDD', 'python', 'memcache', 'django rest framework'],
	license = 'MIT',
    install_requires = [
        'django>1.6'
    ],
    extras_require = {
        'mongo_testing': ['mongoengine>=0.8.7'],
        'redis_testing': ['django-redis>=3.8.2'],
        'neo4j_testing': ['py2neo>=2.0.6'],
        'rest_framework_testing': ['djangorestframework>=3.0.5'],
    },
	classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Database',
    ],
)
