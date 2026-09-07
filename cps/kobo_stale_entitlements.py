# -*- coding: utf-8 -*-
# Calibre-Web Automated – fork of Calibre-Web
# SPDX-License-Identifier: GPL-3.0-or-later

"""Track unknown Kobo entitlements observed immediately before library sync."""

from collections import defaultdict
from threading import RLock
import uuid


_pending = defaultdict(set)
_pending_lock = RLock()
_DUMMY_CATEGORY_ID = "00000000-0000-0000-0000-000000000001"


def queue_unknown_entitlement(user_id, book_uuid):
    """Queue a valid unknown UUID for removal during this user's next sync."""
    try:
        book_uuid = str(uuid.UUID(book_uuid))
    except (AttributeError, TypeError, ValueError):
        return False

    with _pending_lock:
        _pending[user_id].add(book_uuid)
    return True


def take_unknown_entitlements(user_id, limit):
    """Take one deterministic page of queued UUIDs and report whether more remain."""
    with _pending_lock:
        queued = _pending.get(user_id)
        if not queued:
            return [], False

        selected = sorted(queued)[:limit]
        queued.difference_update(selected)
        has_more = bool(queued)
        if not queued:
            _pending.pop(user_id, None)
        return selected, has_more


def create_removed_entitlement(book_uuid):
    """Build the Kobo delta that removes an unavailable library entry."""
    return {
        "ChangedEntitlement": {
            "BookEntitlement": {
                "Id": book_uuid,
                "IsRemoved": True,
            },
            # Older firmware may require metadata to de-index an entitlement.
            "BookMetadata": {
                "Categories": [_DUMMY_CATEGORY_ID],
                "CoverImageId": book_uuid,
                "CrossRevisionId": book_uuid,
                "CurrentDisplayPrice": {"CurrencyCode": "USD", "TotalAmount": 0},
                "EntitlementId": book_uuid,
                "Genre": _DUMMY_CATEGORY_ID,
                "Language": "en",
                "RevisionId": book_uuid,
                "WorkId": book_uuid,
            },
        }
    }
