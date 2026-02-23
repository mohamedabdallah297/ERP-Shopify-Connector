import base64
import hashlib
import hmac
import unittest

from connector import verify_shopify_webhook


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


if __name__ == "__main__":
    unittest.main()
