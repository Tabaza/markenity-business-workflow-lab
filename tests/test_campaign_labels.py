import unittest
from campaign_labels import campaign_labels


class CampaignLabels(unittest.TestCase):
    def test_accepts_approved_labels(self):
        self.assertEqual(campaign_labels('https://example.test/?utm_source=linkedin&utm_medium=organic_social'),
                         {'utm_source': 'linkedin', 'utm_medium': 'organic_social'})

    def test_drops_contact_query_and_fragment(self):
        self.assertEqual(campaign_labels('https://example.test/private?email=sample%40example.test&phone=123&utm_source=x#message'), {'utm_source': 'x'})

    def test_rejects_email_inside_utm_field(self):
        self.assertEqual(campaign_labels('https://example.test/?utm_campaign=sample%40example.test'), {})

    def test_drops_duplicate_label_instead_of_choosing_first(self):
        self.assertEqual(campaign_labels('https://example.test/?utm_source=linkedin&utm_source=x'), {})

    def test_no_partial_match(self):
        self.assertEqual(campaign_labels('https://example.test/?utm_source=linkedin-person'), {})

    def test_blank_and_wrong_case_do_not_pass(self):
        self.assertEqual(campaign_labels('https://example.test/?utm_source=&utm_medium=EMAIL'), {})

    def test_percent_encoded_valid_label(self):
        self.assertEqual(campaign_labels('https://example.test/?utm_source=%6cinkedin'), {'utm_source': 'linkedin'})

    def test_excessive_field_count_fails_closed(self):
        with self.assertRaises(ValueError):
            campaign_labels('https://example.test/?' + '&'.join('x=1' for _ in range(101)))
