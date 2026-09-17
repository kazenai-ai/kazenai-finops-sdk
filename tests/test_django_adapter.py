"""Django spend middleware tests."""

from __future__ import annotations

import os

import pytest

django = pytest.importorskip("django")
from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test",
        ROOT_URLCONF=__name__,
        MIDDLEWARE=["kazenai_finops.spend.adapters.django.FinOpsSpendMiddleware"],
        ALLOWED_HOSTS=["*"],
    )
    django.setup()

from kazenai_finops.spend.adapters.django import FinOpsSpendMiddleware


def test_django_middleware_adds_header(monkeypatch, finops_client):
    monkeypatch.setenv("KAZENAI_FINOPS_URL", finops_client.base_url)
    monkeypatch.setenv("KAZENAI_FINOPS_API_KEY", "k")
    monkeypatch.setenv("KAZENAI_FINOPS_ORG_ID", "org-a")

    def get_response(request):
        return HttpResponse("ok")

    mw = FinOpsSpendMiddleware(get_response)
    mw._client = finops_client
    mw._org_id = "org-a"
    request = RequestFactory().get("/")
    response = mw(request)
    assert response["X-Kazen-Spend-USD"]


def test_django_middleware_blocks(monkeypatch, finops_client, mock_finops_state):
    mock_finops_state["blocked"] = True
    monkeypatch.setenv("KAZENAI_FINOPS_URL", finops_client.base_url)
    monkeypatch.setenv("KAZENAI_FINOPS_ENFORCE_BUDGET", "1")

    def get_response(request):
        return HttpResponse("ok")

    mw = FinOpsSpendMiddleware(get_response)
    mw._client = finops_client
    mw._org_id = "org-a"
    mw._enforce = True
    request = RequestFactory().get("/")
    response = mw(request)
    assert response.status_code == 402
