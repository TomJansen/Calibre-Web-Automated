# Calibre-Web Automated – fork of Calibre-Web
# Copyright (C) 2018-2026 Calibre-Web contributors
# Copyright (C) 2024-2026 Calibre-Web Automated contributors
# SPDX-License-Identifier: GPL-3.0-or-later
# See CONTRIBUTORS for full list of authors.

"""Regression tests for Kobo device authentication routes."""

import ast
from pathlib import Path

import pytest


KOBO_MODULE = Path(__file__).resolve().parents[2] / "cps" / "kobo.py"
MAIN_MODULE = Path(__file__).resolve().parents[2] / "cps" / "main.py"


def _auth_request_routes():
    module = ast.parse(KOBO_MODULE.read_text(encoding="utf-8"))
    handler = next(
        node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "HandleAuthRequest"
    )

    routes = {}
    for decorator in handler.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        if not (
            isinstance(decorator.func, ast.Attribute)
            and isinstance(decorator.func.value, ast.Name)
            and decorator.func.value.id == "kobo"
            and decorator.func.attr == "route"
        ):
            continue

        path = ast.literal_eval(decorator.args[0])
        methods = next(
            (
                ast.literal_eval(keyword.value)
                for keyword in decorator.keywords
                if keyword.arg == "methods"
            ),
            ["GET"],
        )
        routes[path] = methods
    return routes


@pytest.mark.unit
def test_device_auth_handler_covers_first_pairing_and_refresh_routes():
    routes = _auth_request_routes()

    assert routes["/v1/auth/device"] == ["POST"]
    assert routes["/v1/auth/refresh"] == ["POST"]
    assert routes["/v1/user/add-device"] == ["POST"]


@pytest.mark.unit
def test_kobo_blueprint_has_no_global_rate_limit():
    module = ast.parse(MAIN_MODULE.read_text(encoding="utf-8"))

    for call in (node for node in ast.walk(module) if isinstance(node, ast.Call)):
        if not call.args:
            continue
        assert not (
            isinstance(call.args[0], ast.Name)
            and call.args[0].id == "kobo"
            and isinstance(call.func, ast.Call)
            and isinstance(call.func.func, ast.Attribute)
            and call.func.func.attr == "limit"
        )
