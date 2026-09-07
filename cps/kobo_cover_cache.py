# -*- coding: utf-8 -*-
# Calibre-Web Automated – fork of Calibre-Web
# Copyright (C) 2018-2026 Calibre-Web contributors
# Copyright (C) 2024-2026 Calibre-Web Automated contributors
# SPDX-License-Identifier: GPL-3.0-or-later
# See CONTRIBUTORS for full list of authors.

"""Helpers for Kobo cover cache-busting IDs.

These functions are intentionally dependency-light so they can be tested without
importing the full application package.
"""

import base64
from datetime import datetime
import os
import uuid as uuidlib


# A valid 1x1 JPEG used when a Kobo requests a cover for a stale local
# entitlement. Returning 404 can abort the device's pre-sync request queue.
MISSING_COVER_JPEG = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS"
    "Ew8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJ"
    "CQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
    "MjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAA"
    "AAAAAAAAAAf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAA"
    "AAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AL+AD//Z"
)


def normalize_cover_uuid(image_id):
    if not image_id:
        return image_id
    try:
        uuidlib.UUID(image_id)
        return image_id
    except (ValueError, AttributeError, TypeError):
        pass

    parts = str(image_id).rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        base_id = parts[0]
        try:
            uuidlib.UUID(base_id)
            return base_id
        except (ValueError, AttributeError, TypeError):
            return image_id
    return image_id


def build_cover_image_id(base_id, *, use_google_drive, last_modified, cover_path):
    if use_google_drive:
        if isinstance(last_modified, datetime):
            return f"{base_id}-{int(last_modified.timestamp())}"
        return base_id

    if cover_path and os.path.isfile(cover_path):
        cover_mtime = int(os.path.getmtime(cover_path))
        return f"{base_id}-{cover_mtime}"

    return base_id
