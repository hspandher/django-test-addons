"""
All common test case classes and methods reside in this module.
Please do not add any app specific test stuff in this module.
The classes and methods defined in this module should be
inherited/extended by other other apps' test related modules.

@author:    Amyth (mail@amythsingh.com)
"""


# Imports
from django.test import TestCase

from testcases import SimpleTestCase
from testcases.mixins import CommonMethodsMixin


class SimpleViewsTest(SimpleTestCase, CommonMethodsMixin):
    pass


class ViewsTest(TestCase, CommonMethodsMixin):
    pass
