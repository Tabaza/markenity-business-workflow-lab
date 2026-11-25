"""Synthetic teaching lab, not Markenity production code. No network or personal data.

Run: python -m unittest discover -s tests -v
Single worker; explicit transactions; no durable hosting, HTTP, CAPTCHA or CRM adapter.
"""
import hashlib
import json
import sqlite3


def database():
    db = sqlite3.connect(':memory:', isolation_level=None)
    db.executescript('''
        CREATE TABLE intake(ref TEXT PRIMARY KEY, fingerprint TEXT NOT NULL);
        CREATE TABLE outbox(ref TEXT PRIMARY KEY REFERENCES intake(ref),
                            attempts INTEGER NOT NULL DEFAULT 0,
                            state TEXT NOT NULL DEFAULT 'pending');
    ''')
    db.execute('PRAGMA foreign_keys=ON')
    return db


def accept(db, ref, payload, fail_before_job=False):
    """Caller has already authenticated/validated the intake. Stable ref is server-bound."""
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    db.execute('BEGIN IMMEDIATE')
    try:
        existing = db.execute('SELECT fingerprint FROM intake WHERE ref=?', (ref,)).fetchone()
        if existing:
            if existing[0] != fingerprint:
                raise ValueError('same reference with different content')
            db.execute('COMMIT')
            return {'accepted': True, 'new': False, 'reference': ref}
        db.execute('INSERT INTO intake VALUES (?, ?)', (ref, fingerprint))
        if fail_before_job:
            raise RuntimeError('injected interruption before outbox insert')
        db.execute('INSERT INTO outbox(ref) VALUES (?)', (ref,))
        db.execute('COMMIT')
        return {'accepted': True, 'new': True, 'reference': ref}
    except BaseException:
        db.execute('ROLLBACK')
        raise


class FakeProvider:
    """Models a provider honoring a stable key; no email or CRM calls."""
    def __init__(self):
        self.keys = set()

    def send(self, key, unavailable=False):
        if unavailable:
            raise ConnectionError('injected temporary provider failure')
        self.keys.add(key)


def deliver(db, provider, unavailable=False, lose_ack=False, max_attempts=3):
    """One synthetic job/worker, sequential only; no claim of exactly-once delivery."""
    row = db.execute("SELECT ref, attempts FROM outbox WHERE state='pending' ORDER BY ref LIMIT 1").fetchone()
    if row is None:
        return 'idle'
    ref, attempts = row
    db.execute('UPDATE outbox SET attempts=attempts+1 WHERE ref=?', (ref,))
    try:
        provider.send('enquiry-notification/' + ref, unavailable=unavailable)
        if lose_ack:
            raise ConnectionError('provider accepted; acknowledgement lost')
    except ConnectionError:
        if attempts + 1 >= max_attempts:
            db.execute("UPDATE outbox SET state='review' WHERE ref=?", (ref,))
            return 'review'
        return 'retry'
    db.execute("UPDATE outbox SET state='sent' WHERE ref=?", (ref,))
    return 'sent'
