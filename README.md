# ERP ↔ Shopify Custom App Connector

هذا المشروع هو **MVP** لربط ERP (مثل فونيكس) مع Shopify باستخدام Custom App، لكنه **لن يعمل في بيئة حقيقية بدون المدخلات المطلوبة**.

## ماذا يفعل؟

- استقبال Webhooks من Shopify (مثال: `orders/create`).
- التحقق من HMAC لتأمين الطلبات الواردة.
- سحب طلبات Shopify برمجيًا من Admin REST API.
- تحديث المخزون على Shopify من ERP.
- توفير نقاط تمديد واضحة لربط API الخاص بالـ ERP.

## المدخلات المطلوبة (إجباري)

- `SHOPIFY_SHOP_DOMAIN`
- `SHOPIFY_ADMIN_ACCESS_TOKEN`
- `SHOPIFY_WEBHOOK_SECRET`
- `ERP_BASE_URL` (مطلوب عند دفع الطلبات إلى ERP)
- `ERP_API_KEY` (مطلوب عند دفع الطلبات إلى ERP)

> إذا أي قيمة من القيم الإلزامية ناقصة، الكود سيرجع خطأ واضح بدل ما "يكمل صامت".

## المتطلبات

- Python 3.10+
- Shopify Custom App مع الصلاحيات المناسبة:
  - `read_orders`
  - `read_products`
  - `write_inventory`
  - `read_inventory`

## الإعداد

1. انسخ ملف البيئة:

```bash
cp .env.example .env
```

2. عدّل القيم:

- `SHOPIFY_SHOP_DOMAIN`: مثل `your-store.myshopify.com`
- `SHOPIFY_ADMIN_ACCESS_TOKEN`: Access Token من Custom App
- `SHOPIFY_API_VERSION`: مثل `2024-10`
- `SHOPIFY_WEBHOOK_SECRET`: Webhook shared secret
- `ERP_BASE_URL`: رابط ERP API
- `ERP_API_KEY`: مفتاح ERP API

3. شغّل اختبار الوحدة:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## استخدام سريع

### 1) سحب آخر الطلبات

```python
from connector import ShopifyConnector, ShopifyConfig

cfg = ShopifyConfig.from_env()  # يتأكد من القيم المطلوبة
client = ShopifyConnector(cfg)
orders = client.fetch_orders(limit=20)
print(orders)
```

### 2) تحديث كمية مخزون

```python
client.set_inventory_level(location_id=12345678, inventory_item_id=987654321, available=42)
```

### 3) استقبال Webhook

```python
from erp_bridge import handle_shopify_webhook

payload = b'{"id": 1001}'
headers = {
    "X-Shopify-Topic": "orders/create",
    "X-Shopify-Hmac-Sha256": "...",
}
result = handle_shopify_webhook(payload, headers)
print(result)
```

## ملاحظات مهمة للإنتاج

- فعّل queue (مثل RabbitMQ/Kafka/SQS) بدل التنفيذ المتزامن.
- استخدم idempotency key لمنع تكرار معالجة نفس الحدث.
- لا تخزن الأسرار داخل الكود؛ استخدم Vault/Secrets Manager.
- يفضل الانتقال إلى GraphQL Admin API حسب الحاجة للأداء.
