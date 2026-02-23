"""Core Shopify client utilities for ERP integration."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import request
from urllib.error import HTTPError


@dataclass(frozen=True)
class ShopifyConfig:
    shop_domain: str
    admin_access_token: str
    api_version: str
    webhook_secret: str

    @classmethod
    def from_env(cls) -> "ShopifyConfig":
        return cls(
            shop_domain=os.getenv("SHOPIFY_SHOP_DOMAIN", ""),
            admin_access_token=os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN", ""),
            api_version=os.getenv("SHOPIFY_API_VERSION", "2024-10"),
            webhook_secret=os.getenv("SHOPIFY_WEBHOOK_SECRET", ""),
        )


class ShopifyConnector:
    def __init__(self, config: ShopifyConfig) -> None:
        self.config = config

    @property
    def _base_url(self) -> str:
        return f"https://{self.config.shop_domain}/admin/api/{self.config.api_version}"

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        data = None
        headers = {
            "X-Shopify-Access-Token": self.config.admin_access_token,
            "Content-Type": "application/json",
        }

        if body is not None:
            data = json.dumps(body).encode("utf-8")

        req = request.Request(url=url, method=method, headers=headers, data=data)
        try:
            with request.urlopen(req, timeout=30) as resp:
                payload = resp.read().decode("utf-8")
                return json.loads(payload) if payload else {}
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Shopify API error {exc.code}: {detail}") from exc

    def fetch_orders(self, limit: int = 50, status: str = "any") -> list[dict[str, Any]]:
        response = self._request("GET", f"/orders.json?limit={limit}&status={status}")
        return response.get("orders", [])

    def set_inventory_level(
        self,
        location_id: int,
        inventory_item_id: int,
        available: int,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/inventory_levels/set.json",
            body={
                "location_id": location_id,
                "inventory_item_id": inventory_item_id,
                "available": available,
            },
        )


def verify_shopify_webhook(payload: bytes, hmac_header: str, secret: str) -> bool:
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
    computed = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(computed, hmac_header)
