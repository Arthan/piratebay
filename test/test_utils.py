import unittest
from urllib2 import Request
from urllib import urlencode
from piratebay.utils import RequestObject, create_request_object

class TestRequestObject(unittest.TestCase):
    def setUp(self):
        self.req = RequestObject()
    def test_get_random_user_agent(self):
        first = self.req.get_random_user_agent()
        second = self.req.get_random_user_agent()
        self.assertNotEqual(first, second,
                            "User agent should be unique from one call to the other")

class TestCreateRequestObject(unittest.TestCase):
    def test_should_return_request_object(self):
        req = create_request_object("http://thepiratebay.org")
        self.assertIsInstance(req, Request, "invalid urllib2.Request object")
    def test_useragent(self):
        req = create_request_object("http://thepiratebay.org")
        self.assertIn(req.get_header('User-agent'), RequestObject.user_agents, "Should have a valid user agent!")
    def test_request_without_formdata(self):
        req = create_request_object("http://thepiratebay.org")
        self.assertEqual(req.get_full_url(), "http://thepiratebay.org")
        self.assertEqual(req.get_data(), None)
    def test_request_with_formdata(self):
        form_data = { 'q': 'ncis', 'category': 0, 'page': 0, 'orderby': 99 }
        get_req = create_request_object("http://thepiratebay.org", form_data=form_data)
        post_req = create_request_object("http://thepiratebay.org", form_data=form_data, get_request=False)
        self.assertEqual(post_req.get_data(), urlencode(form_data))
        self.assertEqual(get_req.get_data(), None, "invalid get request!")