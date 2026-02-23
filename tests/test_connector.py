import base64
import hashlib
import hmac
import os
import unittest

from connector import ConfigError, ShopifyConfig, verify_shopify_webhook


class VerifyWebhookTests(unittest.TestCase):
    def test_verify_shopify_webhook_valid_signature(self) -> None:
        payload = b'{"id":1,"topic":"orders/create"}'
        secret = "super-secret"
        digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
        hmac_header = base64.b64encode(digest).decode("utf-8")

        self.assertTrue(verify_shopify_webhook(payload, hmac_header, secret))

    def test_verify_shopify_webhook_invalid_signature(self) -> None:
        payload = b'{"id":1}'
        self.assertFalse(verify_shopify_webhook(payload, "bad-signature", "super-secret"))

    def test_verify_shopify_webhook_requires_secret(self) -> None:
        with self.assertRaises(ConfigError):
            verify_shopify_webhook(b"{}", "x", "")


class ShopifyConfigTests(unittest.TestCase):
    def test_from_env_requires_mandatory_values(self) -> None:
        keys = [
            "SHOPIFY_SHOP_DOMAIN",
            "SHOPIFY_ADMIN_ACCESS_TOKEN",
            "SHOPIFY_WEBHOOK_SECRET",
        ]
        original = {k: os.environ.get(k) for k in keys}
        try:
            for k in keys:
                os.environ.pop(k, None)
            with self.assertRaises(ConfigError):
                ShopifyConfig.from_env()
        finally:
            for k, v in original.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


if __name__ == "__main__":
    unittest.main()
