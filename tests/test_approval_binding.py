import unittest
from approval_binding import Proposal, digest, record_approval, matches_current_revision


class ApprovalBinding(unittest.TestCase):
    def setUp(self):
        self.proposal = Proposal('draft-1', 2, {'subject': 'Synthetic example', 'recipient_group': 'internal-review'})
        self.approval = record_approval(self.proposal, 'send', 200)

    def test_current_exact_revision(self):
        self.assertTrue(matches_current_revision(self.approval, self.proposal, 'send', 100))

    def test_changed_text_without_revision_change(self):
        changed = Proposal('draft-1', 2, {'subject': 'Edited after approval', 'recipient_group': 'internal-review'})
        self.assertFalse(matches_current_revision(self.approval, changed, 'send', 100))

    def test_new_revision_with_same_text(self):
        self.assertFalse(matches_current_revision(self.approval, Proposal('draft-1', 3, self.proposal.payload), 'send', 100))

    def test_other_proposal(self):
        self.assertFalse(matches_current_revision(self.approval, Proposal('draft-2', 2, self.proposal.payload), 'send', 100))

    def test_other_action(self):
        self.assertFalse(matches_current_revision(self.approval, self.proposal, 'publish', 100))

    def test_expiry_boundary(self):
        self.assertFalse(matches_current_revision(self.approval, self.proposal, 'send', 200))

    def test_key_order_is_not_a_content_change(self):
        self.assertEqual(digest({'a': 1, 'b': 2}), digest({'b': 2, 'a': 1}))

    def test_arabic_content_change_is_detected(self):
        first = Proposal('ar-1', 1, {'message': '\u0623\u0631\u0633\u0644 \u0627\u0644\u0639\u0631\u0636'})
        changed = Proposal('ar-1', 1, {'message': '\u0623\u0631\u0633\u0644 \u0627\u0644\u0639\u0642\u062f'})
        approval = record_approval(first, 'send', 200)
        self.assertFalse(matches_current_revision(approval, changed, 'send', 100))
