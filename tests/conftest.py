# -*- coding: utf-8 -*-
"""Keep the whole test suite offline.

Every generator network call goes through urllib.request.urlopen (the
favicon/social/emoji downloads). The autouse stub below replaces it for
every test, so an accidental real network attempt fails instantly with a
loud message instead of hanging for a 30s socket timeout. The generator
degrades gracefully on fetch failure (warning + skipped asset), so all
builds stay green offline; tests that exercise the download pipeline
patch their own fake response, which shadows this stub for that test.
"""
import pytest

from internote import generator


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    def _no_network(request, timeout=None):
        raise AssertionError(
            "test reached for the network: {!r} - the suite is "
            "offline by design; patch urlopen with a fake response".format(
                getattr(request, "full_url", request)
            )
        )

    monkeypatch.setattr(
        generator.urllib.request, "urlopen", _no_network, raising=False
    )
