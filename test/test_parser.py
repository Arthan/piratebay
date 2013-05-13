import unittest
import datetime
from lxml import html
from piratebay import exceptions
from piratebay.parser import SearchPageParser, UserPageParser, TorrentInfoParser
from test import get_fixture

class DateMixIn(object):
    def assertDate(self, d1, d2):
        self.assertEqual( (d1.year, d1.month, d1.day),\
                            (d2.year, d2.month, d2.day) )
        self.assertEqual( (d1.hour, d1.minute, d1.second),\
                            (d2.hour, d2.minute, d2.second) )
# Keep a dictionary with all lxml documents, so as not to re-read and re-parse
# them all each unittest.
html_docs = dict(
    real_site = html.parse(get_fixture("real_site.html")).getroot(),
    site_p6 = html.parse(get_fixture("site_p6.html")).getroot(),
    torrent_info_url = html.parse(get_fixture("torrent_info_url.html")).getroot()
)

class TestFailingCases(unittest.TestCase):
    def _create_parsers(self, document):
        return SearchPageParser(document), UserPageParser(document)
    def generate_document(self, code):
        return html.document_fromstring(code)
    def test_find_table(self):
        fragment = self.generate_document("""
        <html><body>
        <div id='content'><div id='main-content'>
        </div></div></body></html>""")
        p1, p2 = self._create_parsers(fragment)
        for parser in [p1, p2]:
            self.assertRaises(exceptions.ElementNotFound, parser.find_table)
    def test_process_row(self):
        fragment = html.fragment_fromstring("""
        <tr>
            <td>One</td>
            <td>Two</td>
            <td>Three</td>
        </tr>
        """)
        user_is_anonymous = html.fragment_fromstring("""
        <tr>
            <td class='vertTh'><center>some text</center></td>
            <td>
                <div class='detName'><a href='/torrent/some_torrent' class='detLink'>some torrent</a></div>
                <a href="..." title='Download this torrent'>...</a>
                <a href="..." title='Download this torrent using magnet'>...</a>
                <a href="/user/<some_user>" title="Browse <some_user>">some_user</a>
                <img src="..." />
                <font class='detDesc'>
                    Uploaded 08-10&nbsp;15:57, Size 1.03&nbsp;GiB, ULed by
                </font>
            </td>
            <td align='right'>123</td>
            <td align='right'>321</td>
        </tr>
        """)
        p1, p2 = self._create_parsers(fragment)
        self.assert_(p2.process_row(fragment) == None)
        self.assertRaises(exceptions.InvalidRow, p1.process_row, fragment)
        self.assertEqual(p1.process_row(user_is_anonymous)["user"], "Anonymous")
        self.assertEqual(p2.process_row(user_is_anonymous)["user"], "Anonymous")
    def test_process_page_numbers(self):
        div_not_found = self.generate_document("<div></div>")
        incorrect_div = self.generate_document("<div align='center'>incorrect div!</div>")
        p1, p2 = self._create_parsers(div_not_found)
        self.assertRaises(exceptions.ElementNotFound, p1.process_page_numbers)
        self.assertRaises(exceptions.ElementNotFound, p2.process_page_numbers)
        p1, p2 = self._create_parsers(div_not_found)
        self.assertRaises(exceptions.ElementNotFound, p1.process_page_numbers)
        self.assertRaises(exceptions.ElementNotFound, p2.process_page_numbers)

class TestSuccessCases(unittest.TestCase, DateMixIn):
    def setUp(self):
        self.doc = html_docs["real_site"]
    def test_find_table(self):
        p = SearchPageParser(self.doc)
        table = p.find_table()
        self.assertIsInstance(table, html.HtmlElement)
    def test_process_rows(self):
        p = SearchPageParser(self.doc)
        current_page, num_pages, data = p.run()
        self.assertEqual(current_page, 1)
        self.assertEqual(num_pages, 26)
        first_item = data[0]
        self.assertEqual(first_item["name"], "NCIS Los Angeles 1x12 Al 1x14 HDTV DVB Spanish")
        self.assert_(first_item["torrent_info_url"].endswith("/torrent/5752632/NCIS_Los_Angeles_1x12_Al_1x14_HDTV_DVB_Spanish"))
        self.assertEqual(first_item["torrent_url"], "http://torrents.thepiratebay.org/5752632/NCIS_Los_Angeles_1x12_Al_1x14_HDTV_DVB_Spanish.5752632.TPB.torrent")
        self.assertEqual(first_item["magnet_url"], "magnet:?xt=urn:btih:e2da10780dd53d95512c7881efef992f4a9e068c&dn=NCIS+Los+Angeles+1x12+Al+1x14+HDTV+DVB+Spanish&tr=http%3A%2F%2Ftracker.prq.to%2Fannounce")
        self.assert_(first_item["user"].endswith("Mois20/"))
        self.assertEqual(first_item["seeders"], 31)
        self.assertEqual(first_item["leechers"], 31)
        date = datetime.datetime.now().replace(month=8, day=10, hour=15, minute=57)
        self.assertDate(date, first_item["uploaded_at"])
        self.assertAlmostEqual(first_item["size_of"][0], 1.03)
        self.assertEqual(first_item["size_of"][1], "GiB")
    def test_process_rows_on_other_document(self):
        p = SearchPageParser(html_docs["site_p6"])
        current_page, num_pages, data = p.run()
        self.assertEqual(current_page, 6)
        self.assertEqual(num_pages, 26)

class TestTorrentInfoParser(unittest.TestCase, DateMixIn):
    def setUp(self):
        self.document = html_docs["torrent_info_url"]
        self.p = TorrentInfoParser(self.document)
    def test_parse_title(self):
        title = self.p.parse_title()
        self.assert_("name" in title)
        self.assertEqual(title["name"], "BBEdit 9.3 - latest with keygen")
    def test_locate_element_with_xpath(self):
        phony_xpath = ".//div[@id='content']/div[@id='main-content']/div[@class='phony']"
        self.assertRaises(exceptions.ElementNotFound, self.p.locate_element_with_xpath, [phony_xpath], "will raise!")
        element = self.p.locate_element_with_xpath([
            self.p._xpath_details_frame,
            self.p._xpath_details_title
        ], "...")
        self.assertIsInstance(element, html.HtmlElement)
        self.assertEqual(element.text.strip(), "BBEdit 9.3 - latest with keygen")
    def test_parse_description(self):
        description = self.p.parse_description()
        self.assert_("description" in description)
        self.assert_(description.get("description").startswith("Official Web Site:"))
    def test_parse_definition_list(self):
        dl = self.p.parse_definition_list()
        possible_keys = [
            "category", "files",
            "size_of", "tags",
            "rating", "uploaded_at",
            "user", "trusted",
            "seeders", "leechers"
        ]
        for key in possible_keys:
            self.assert_(key in dl)
        self.assertEqual(dl["category"], 302)
        self.assertEqual(dl["files"], 3)
        self.assertEqual(dl["size_of"], (16.14, u"MiB"))
        self.assertEqual(dl["tags"], ["BBEdit"])
        self.assertEqual(dl["rating"], (2, 0, 2))
        self.assertEqual(dl["trusted"], True)
        self.assertEqual(dl["seeders"], 9)
        self.assertEqual(dl["leechers"], 1)
        self.assertDate(dl["uploaded_at"],
            datetime.datetime.now().replace(
                year=2009, month=11, day=6,
                hour=11, minute=35, second=3
            ))
    def test_run(self):
        possible_keys = [
            "category", "files",
            "size_of", "tags",
            "rating", "uploaded_at",
            "user", "trusted",
            "seeders", "leechers",
            "name", "description"
        ]
        result = self.p.run()
        self.assertIsInstance(result, dict)
        for key in possible_keys:
            self.assert_(key in result)