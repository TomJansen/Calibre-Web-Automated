# Calibre-Web Automated – fork of Calibre-Web
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib.util
from pathlib import Path
import uuid

import pytest


MODULE_PATH = Path(__file__).resolve().parents[2] / "cps" / "kobo_stale_entitlements.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("kobo_stale_entitlements_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def stale_entitlements():
    return _load_module()


@pytest.mark.unit
def test_unknown_entitlements_are_deduplicated_and_scoped_by_user(stale_entitlements):
    book_uuid = str(uuid.uuid4())

    assert stale_entitlements.queue_unknown_entitlement(1, book_uuid)
    assert stale_entitlements.queue_unknown_entitlement(1, book_uuid)
    assert stale_entitlements.queue_unknown_entitlement(2, book_uuid)

    assert stale_entitlements.take_unknown_entitlements(1, 100) == ([book_uuid], False)
    assert stale_entitlements.take_unknown_entitlements(2, 100) == ([book_uuid], False)


@pytest.mark.unit
def test_invalid_cover_id_is_not_queued(stale_entitlements):
    assert not stale_entitlements.queue_unknown_entitlement(1, "not-a-uuid")
    assert stale_entitlements.take_unknown_entitlements(1, 100) == ([], False)


@pytest.mark.unit
def test_unknown_entitlements_are_paged(stale_entitlements):
    book_uuids = sorted(str(uuid.uuid4()) for _ in range(3))
    for book_uuid in book_uuids:
        stale_entitlements.queue_unknown_entitlement(1, book_uuid)

    assert stale_entitlements.take_unknown_entitlements(1, 2) == (book_uuids[:2], True)
    assert stale_entitlements.take_unknown_entitlements(1, 2) == (book_uuids[2:], False)


@pytest.mark.unit
def test_removed_entitlement_marks_cached_entry_as_removed(stale_entitlements):
    book_uuid = str(uuid.uuid4())

    result = stale_entitlements.create_removed_entitlement(book_uuid)

    change = result["ChangedEntitlement"]
    assert change["BookEntitlement"] == {"Id": book_uuid, "IsRemoved": True}
    assert change["BookMetadata"]["EntitlementId"] == book_uuid
    assert "DownloadUrls" not in change["BookMetadata"]
