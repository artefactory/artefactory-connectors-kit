from unittest import TestCase
from parameterized import parameterized
from bs4 import BeautifulSoup

PARAGRAPH_OF_200_CHARACTERS = (
    "Lorem ipsum sit amet cursus sit amet dictum sit amet justo donec"
    "enim diam vulputate ut pharetra sit amet aliquam id diam maecenas"
    "ultricies mi eget mauris pharetra et ultrices neque ornare aenean felis"
)

HTML_BODY = (
    "<ac:layout-section>"
    "<h1>Case ID card</h1>"
    "<table>"
    "<tr><th>Confidentiality</th><td>GreenPublic</td></tr>"
    "<tr><th>Article status</th><td>YellowIn progress</td></tr>"
    "<tr><th>Industry</th><td>Automotive</td></tr>"
    "<tr><th>Client company</th><td>Michelin</td></tr>"
    "<tr><th>Scope</th><td>France</td></tr>"
    "<tr><th>Mission start date</th><td>2020/01/01</td></tr>"
    "<tr><th>Mission end date</th><td>8 weeks</td></tr>"
    "<tr><th>Amount sold</th><td>45 KEUR</td></tr>"
    "<tr><th>Mission topic</th><td>Precision Marketing</td></tr>"
    "<tr><th>Commercial proposal</th><td><a href='https://commercial_proposal.com'>Click here</a></td></tr>"
    "<tr><th>One pager</th><td><a href='https://one_pager.com'>Click here</a></td></tr>"
    "<tr><th>Architecture</th><td><a href='https://architecture.com'>Click here</a></td></tr>"
    "</table>"
    "</ac:layout-section>"
    f"<ac:layout-section><h1>Key learnings</h1><p>{PARAGRAPH_OF_200_CHARACTERS}</p></ac:layout-section>"
    f"<ac:layout-section><h1>I. Context</h1><p>{PARAGRAPH_OF_200_CHARACTERS}</p></ac:layout-section>"
    f"<ac:layout-section><h1>II. Approach</h1><p>{PARAGRAPH_OF_200_CHARACTERS}</p></ac:layout-section>"
    f"<ac:layout-section><h1>III. Conclusion</h1><p>{PARAGRAPH_OF_200_CHARACTERS}</p></ac:layout-section>"
)

CONTENT_DCT = {
    "id": "00001",
    "type": "page",
    "title": "Making API requests with NCK",
    "space": {"name": "How To Guides"},
    "metadata": {"labels": {"results": [{"name": "nck"}, {"name": "api"}]}},
    "_links": {"self": "https://your-domain.com/wiki/rest/api/content/00001", "tinyui": "/x/aBcD"},
    "body": {"storage": {"value": HTML_BODY}},
}

EXPECTED_CLIENT_PROPERTIES = {
    "client_property_CONFIDENTIALITY": "PUBLIC",
    "client_property_ARTICLE STATUS": "IN PROGRESS",
    "client_property_INDUSTRY": "Automotive",
    "client_property_CLIENT COMPANY": "Michelin",
    "client_property_SCOPE": "France",
    "client_property_MISSION START DATE": "2020/01/01",
    "client_property_MISSION END DATE": "8 weeks",
    "client_property_AMOUNT SOLD": "45 KEUR",
    "client_property_MISSION TOPIC": "Precision Marketing",
    "client_property_COMMERCIAL PROPOSAL": "https://commercial_proposal.com",
    "client_property_ONE PAGER": "https://one_pager.com",
    "client_property_ARCHITECTURE": "https://architecture.com",
}

EXPECTED_CLIENT_COMPLETION = {
    "client_completion_KEY LEARNINGS": 1,
    "client_completion_CONTEXT": 1,
    "client_completion_APPROACH": 0,
    "client_completion_CONCLUSION": 1,
}


class CustomFieldsTest(TestCase):
    def test__get_tiny_link(self):
        from nck.helpers.confluence_helper import _get_tiny_link

        field_value = {"self": "https://your-domain.com/wiki/rest/api/content/00001", "tinyui": "/x/aBcD"}
        expected = "https://your-domain.com/wiki/x/aBcD"
        self.assertEqual(_get_tiny_link(field_value), expected)

    @parameterized.expand([([{"name": "nck"}, {"name": "api"}], "name", "nck|api"), ([], "name", "")])
    def test__get_key_values_from_list_of_dct(self, field_value, key, expected):
        from nck.helpers.confluence_helper import _get_key_values_from_list_of_dct

        self.assertEqual(_get_key_values_from_list_of_dct(field_value, key), expected)

    def test__get_client_properties(self):
        from nck.helpers.confluence_helper import _get_client_properties

        self.assertDictEqual(_get_client_properties(HTML_BODY), EXPECTED_CLIENT_PROPERTIES)

    def test__get_client_completion(self):
        from nck.helpers.confluence_helper import _get_client_completion

        self.assertDictEqual(_get_client_completion(HTML_BODY), EXPECTED_CLIENT_COMPLETION)

    @parameterized.expand(
        [
            (
                (
                    "<ac:layout-section><h1>II. Approach</h1><p>In data we trust.</p></ac:layout-section>"
                    "<ac:layout-section><h1>Team</h1><p>B. Gates, M. Zuckerberg</p></ac:layout-section>"
                ),
                "<ac:layout-section><h1>II. Approach</h1><p>In data we trust.</p></ac:layout-section>",
            ),
            (
                (
                    "<ac:layout-section><strong>II. Approach</strong><p>In data we trust.</p></ac:layout-section>"
                    "<ac:layout-section><h1>Team</h1><p>B. Gates, M. Zuckerberg</p></ac:layout-section>"
                ),
                "<ac:layout-section><strong>II. Approach</strong><p>In data we trust.</p></ac:layout-section>",
            ),
        ]
    )
    def test__get_section_by_title(self, html_body, expected):
        from nck.helpers.confluence_helper import _get_section_by_title

        searched_title = "APPROACH"
        html_soup = BeautifulSoup(html_body, "lxml")
        output = _get_section_by_title(html_soup, searched_title)
        self.assertEqual(str(output), expected)


class DictToCleanTest(TestCase):
    def test__clean(self):
        from nck.helpers.confluence_helper import DictToClean

        dct = {"CLIENT COMPANY": "Michelin", "SCOPE": "France", "TEAM SIZE": 10}
        expected_keys = ["CLIENT COMPANY", "AMOUNT SOLD", "SCOPE"]
        default_value = ""
        prefix = "prefix_"

        expected = {"prefix_CLIENT COMPANY": "Michelin", "prefix_AMOUNT SOLD": "", "prefix_SCOPE": "France"}
        output = DictToClean(dct, expected_keys, default_value, prefix).clean()
        self.assertDictEqual(output, expected)


class ParseResponseTest(TestCase):
    @parameterized.expand(
        [("title", ["title"]), ("space.name", ["space", "name"]), ("label_names", ["metadata", "labels", "results"])]
    )
    def test__get_field_path(self, field, expected):
        from nck.helpers.confluence_helper import _get_field_path

        self.assertListEqual(_get_field_path(field), expected)

    @parameterized.expand(
        [
            (["title"], "Making API requests with NCK"),
            (["space", "name"], "How To Guides"),
            (["metadata", "labels"], {"results": [{"name": "nck"}, {"name": "api"}]}),
            (["invalid_key"], None),
        ]
    )
    def test__get_field_value(self, field_path, expected):
        from nck.helpers.confluence_helper import _get_field_value

        self.assertEqual(_get_field_value(CONTENT_DCT, field_path), expected)

    @parameterized.expand(
        [
            ("title", "Making API requests with NCK", {"title": "Making API requests with NCK"}),
            ("space.name", "How To Guides", {"space.name": "How To Guides"}),
            ("label_names", [{"name": "nck"}, {"name": "api"}], {"label_names": "nck|api"}),
        ]
    )
    def test__format_field_as_dct(self, field, field_value, expected):
        from nck.helpers.confluence_helper import _format_field_as_dct

        self.assertDictEqual(_format_field_as_dct(field, field_value), expected)

    def test__parse_response(self):
        from nck.helpers.confluence_helper import parse_response

        raw_response = {
            "results": [
                {
                    "id": "00001",
                    "type": "page",
                    "title": "Making API requests with NCK",
                    "space": {"name": "How To Guides"},
                    "metadata": {"labels": {"results": [{"name": "nck"}, {"name": "api"}]}},
                },
                {
                    "id": "00002",
                    "type": "page",
                    "title": "Writting a Client Case",
                    "space": {"name": "How To Guides"},
                    "metadata": {"labels": {"results": [{"name": "confluence"}]}},
                },
                {
                    "id": "00003",
                    "type": "page",
                    "title": "Developping with Github",
                    "space": {"name": "How To Guides"},
                    "metadata": {"labels": {"results": [{"name": "git"}]}},
                },
            ]
        }
        fields = ["title", "space.name", "label_names"]
        expected = [
            {"title": "Making API requests with NCK", "space.name": "How To Guides", "label_names": "nck|api"},
            {"title": "Writting a Client Case", "space.name": "How To Guides", "label_names": "confluence"},
            {"title": "Developping with Github", "space.name": "How To Guides", "label_names": "git"},
        ]
        output = parse_response(raw_response, fields)
        for output_record, expected_record in zip(iter(output), iter(expected)):
            self.assertDictEqual(output_record, expected_record)

    @parameterized.expand([("\u2705 Title with \ud83d\udd36 emoji \ud83d\udd34", "Title with emoji"), (0, 0)])
    def test__decode(self, raw_value, expected):
        from nck.helpers.confluence_helper import _decode

        self.assertEqual(_decode(raw_value), expected)
