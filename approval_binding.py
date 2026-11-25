"""Synthetic revision-integrity model, not an authentication/authorization service."""
from dataclasses import dataclass
from hashlib import sha256
import json


def digest(payload):
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return sha256(encoded.encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class Proposal:
    identifier: str
    revision: int
    payload: dict


@dataclass(frozen=True)
class Approval:
    identifier: str
    revision: int
    payload_digest: str
    action: str
    expires_at: int


def record_approval(proposal, action, expires_at):
    """Caller must authenticate, authorize, display exact revision and persist safely.

    This lab intentionally does not implement those responsibilities. These plain
    data objects are not signed tokens and must not be trusted from a client.
    """
    return Approval(proposal.identifier, proposal.revision, digest(proposal.payload), action, expires_at)


def matches_current_revision(approval, proposal, action, now):
    return (approval.identifier == proposal.identifier
            and approval.revision == proposal.revision
            and approval.payload_digest == digest(proposal.payload)
            and approval.action == action
            and now < approval.expires_at)
