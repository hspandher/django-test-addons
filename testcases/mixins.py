"""
This module contains all the mixins to be used by testcases
module.

@author:    Amyth (mail@amythsingh.com)
"""


# Imports
from django.core.urlresolvers import reverse


class CommonMethodsMixin(object):
    """
    Common Methods Mixin to be used by base test case classes
    """

    def assertContextContains(self, items):
        """
        Tests if the response context contains all of
        the given items.
        """

        for item in items:
            self.assertTrue(item in self.response.context)

    def assertJsonResponse(self, response):
        """
        Tests if the given response is a json response.
        """

        self.assertTrue("application/json" in response['Content-type'])

    def assertTemplatesContains(self, template):
        """
        Tests if context.templates contains the
        given template.
        """

        templates = [tpl.name for tpl in self.response.templates]
        self.assertTrue(template in templates)

    def assertMessagesContains(self, message):
        """
        Tests if context messages contains the
        given message.
        """

        messages = [mssg.message for mssg in self.context['messages']]
        self.assertTrue(message in messages)

    def check_request(self, view, request_type, status, data=None,
            follow=False, *args, **kwargs):
        """
        Tests a GET request for a given view
        with the given data and status code.
        """

        REQUEST_TYPE_MAPPING = {
            "get": self.client.get,
            "post": self.client.post,
            "put": self.client.put,
            "delete": self.client.delete,
        }

        data = data or {}
        view_url = reverse(view, *args, **kwargs)
        request = REQUEST_TYPE_MAPPING.get(request_type)
        response = request(view_url, data=data, follow=follow)
        self.response = response
