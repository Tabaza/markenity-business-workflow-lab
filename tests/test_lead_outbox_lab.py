import unittest
from lead_outbox_lab import database, accept, deliver, FakeProvider


class OutboxContract(unittest.TestCase):
    def setUp(self):
        self.db = database()
        self.provider = FakeProvider()

    def tearDown(self):
        self.db.close()

    def count(self, table):
        return self.db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0]

    def test_atomic_acceptance(self):
        result = accept(self.db, 'synthetic-1', {'service': 'web'})
        self.assertTrue(result['new'])
        self.assertEqual((self.count('intake'), self.count('outbox')), (1, 1))

    def test_interruption_rolls_back_both_records(self):
        with self.assertRaises(RuntimeError):
            accept(self.db, 'synthetic-1', {'service': 'web'}, fail_before_job=True)
        self.assertEqual((self.count('intake'), self.count('outbox')), (0, 0))

    def test_same_request_is_not_a_second_acceptance(self):
        accept(self.db, 'synthetic-1', {'service': 'web'})
        again = accept(self.db, 'synthetic-1', {'service': 'web'})
        self.assertFalse(again['new'])
        self.assertEqual(self.count('outbox'), 1)

    def test_changed_request_cannot_reuse_reference(self):
        accept(self.db, 'synthetic-1', {'service': 'web'})
        with self.assertRaises(ValueError):
            accept(self.db, 'synthetic-1', {'service': 'ai'})
        self.assertEqual(self.count('outbox'), 1)

    def test_distinct_enquiries_remain_distinct(self):
        for ref in ('synthetic-1', 'synthetic-2'):
            accept(self.db, ref, {'service': 'web'})
        self.assertEqual(self.count('outbox'), 2)

    def test_provider_failure_does_not_lose_accepted_record(self):
        accept(self.db, 'synthetic-1', {'service': 'web'})
        self.assertEqual(deliver(self.db, self.provider, unavailable=True), 'retry')
        self.assertEqual(self.count('intake'), 1)
        self.assertEqual(deliver(self.db, self.provider), 'sent')
        self.assertEqual(len(self.provider.keys), 1)

    def test_lost_ack_uses_same_provider_key(self):
        accept(self.db, 'synthetic-1', {'service': 'web'})
        self.assertEqual(deliver(self.db, self.provider, lose_ack=True), 'retry')
        self.assertEqual(deliver(self.db, self.provider), 'sent')
        self.assertEqual(len(self.provider.keys), 1)

    def test_retry_exhaustion_requires_review(self):
        accept(self.db, 'synthetic-1', {'service': 'web'})
        self.assertEqual([deliver(self.db, self.provider, unavailable=True) for _ in range(3)],
                         ['retry', 'retry', 'review'])
        self.assertEqual(deliver(self.db, self.provider), 'idle')
        self.assertEqual(self.count('intake'), 1)

    def test_completed_job_is_not_sent_again(self):
        accept(self.db, 'synthetic-1', {'service': 'web'})
        self.assertEqual(deliver(self.db, self.provider), 'sent')
        self.assertEqual(deliver(self.db, self.provider), 'idle')

    def test_no_jobs_means_no_provider_call(self):
        self.assertEqual(deliver(self.db, self.provider), 'idle')
        self.assertEqual(len(self.provider.keys), 0)


if __name__ == '__main__':
    unittest.main()
