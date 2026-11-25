"""Teaching fixture: extract only pre-approved campaign labels, not full URLs."""
from urllib.parse import parse_qs, urlsplit

APPROVED = {
    'utm_source': frozenset({'linkedin', 'facebook', 'x', 'medium', 'wordpress'}),
    'utm_medium': frozenset({'organic_social', 'referral', 'email'}),
    'utm_campaign': frozenset({'launch_2026', 'bilingual_forms', 'workflow_checks'}),
    'utm_content': frozenset({'en', 'ar', 'checklist'}),
}


def campaign_labels(url):
    """Unknown/duplicate/unapproved values are omitted, never sent as raw fallback.

    This does not control cookies, network metadata or third-party tracking SDKs.
    A real integration must inspect the actual analytics payload separately.
    """
    query = parse_qs(urlsplit(url).query, keep_blank_values=True, max_num_fields=100)
    return {name: values[0] for name, allowed in APPROVED.items()
            if len(values := query.get(name, [])) == 1 and values[0] in allowed}
