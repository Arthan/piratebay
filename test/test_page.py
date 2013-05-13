import unittest
from lxml import html
from piratebay.page import SearchPage, PageItem
from test import get_fixture

class TestPage(unittest.TestCase):
    def setUp(self):
        self.doc = html.parse(open(get_fixture("real_site.html"))).getroot()
        self.doc2 = html.parse(open(get_fixture("site_p6.html"))).getroot()
        self.p1 = SearchPage(self.doc)
        self.p2 = SearchPage(self.doc2)
    def test_document_all(self):
        self.assertEqual(self.p1.document, self.doc)
        self.assertEqual(self.p2.document, self.doc2)
        self.assertIsInstance(self.p1, SearchPage)
        self.assertIsInstance(self.p2, SearchPage)
        self.assertEqual(self.p1.get_current_page(), 1)
        self.assertEqual(self.p1.get_number_of_pages(), 26)
        self.assertEqual(self.p2.get_current_page(), 6)
        self.assertEqual(self.p2.get_number_of_pages(), 26)
    def test_all(self):
        self.assertEqual(30, len(self.p1.all()))
        self.assertEqual(30, len(self.p2.all()))
    def test_search(self):
        def comp_test(first, second):
            user = first.encode("utf-8").split('/')
            if len(user) >= 2:
                user = user[-2]
            if user == second:
                return True
            return False
        t1 = list(self.p1.search("user", "Sabelma", comparator=comp_test, order_by="seeders", reversed=True))
        t2 = list(self.p1.search("user", "Mois20", comparator=comp_test, order_by="seeders", reversed=False))
        self.assertIsInstance(t1[0], PageItem)
        self.assertEqual(len(t1), 6) 
        self.assertEqual(len(t2), 7)
        self.assertEqual(len([x for x in self.p1.search("user", "/user/Sabelma/")]), 6)
        last = t1[0].seeders
        for c in t1:
            self.assertLessEqual(c.seeders, last)
            last = c.seeders
        last = t2[0].seeders
        for c in t2:
            self.assertGreaterEqual(c.seeders, last)
            last = c.seeders
    def test_limits(self):
        self.assertEqual(len(self.p1.all(limit=5)), 5)
