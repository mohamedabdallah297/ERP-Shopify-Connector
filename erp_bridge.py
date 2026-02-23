"""Application-level bridge logic between Shopify and ERP."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

from connector import ShopifyConfig, ShopifyConnector, verify_shopify_webhook


def _post_to_erp(endpoint: str, payload: dict[str, Any]) -> None:
    """Placeholder ERP POST. Replace mapping and auth as required by Phoenix ERP API."""
    erp_base = os.getenv("ERP_BASE_URL", "")
    erp_key = os.getenv("ERP_API_KEY", "")
    if not erp_base:
        return

    url = f"{erp_base.rstrip('/')}/{endpoint.lstrip('/')}"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {erp_key}",
        },
        data=data,
    )
    with request.urlopen(req, timeout=20):
        return


def _map_shopify_order_to_erp(order: dict[str, Any]) -> dict[str, Any]:
    return {
        "external_order_id": str(order.get("id", "")),
        "order_number": order.get("name", ""),
        "customer_email": order.get("email", ""),
        "currency": order.get("currency", ""),
        "total_price": order.get("total_price", "0"),
        "lines": [
            {
                "sku": item.get("sku", ""),
                "title": item.get("title", ""),
                "qty": item.get("quantity", 0),
                "unit_price": item.get("price", "0"),
            }
            for item in order.get("line_items", [])
        ],
    }


def handle_shopify_webhook(raw_body: bytes, headers: dict[str, str]) -> dict[str, Any]:
    cfg = ShopifyConfig.from_env()
    hmac_header = headers.get("X-Shopify-Hmac-Sha256", "")
    if not verify_shopify_webhook(raw_body, hmac_header, cfg.webhook_secret):
        return {"ok": False, "error": "invalid_hmac"}

    topic = headers.get("X-Shopify-Topic", "")
    payload = json.loads(raw_body.decode("utf-8"))

    if topic == "orders/create":
        mapped = _map_shopify_order_to_erp(payload)
        _post_to_erp("orders/import", mapped)

    return {"ok": True, "topic": topic}


def sync_inventory_from_erp(location_id: int, updates: list[dict[str, int]]) -> list[dict[str, Any]]:
    cfg = ShopifyConfig.from_env()
    client = ShopifyConnector(cfg)
    results: list[dict[str, Any]] = []

    for item in updates:
        res = client.set_inventory_level(
            location_id=location_id,
            inventory_item_id=item["inventory_item_id"],
            available=item["available"],
        )
        results.append(res)

    return results
