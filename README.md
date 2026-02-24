# ERP ↔ Shopify Custom App Connector

تطبيق ربط Shopify Custom App مع ERP، ويحتوي الآن على HTTP server فعلي يستقبل webhook من Shopify.

## اللي اشتغل فعليًا الآن

- Endpoint صحة الخدمة: `GET /health`
- Endpoint استقبال Webhook: `POST /webhooks/shopify`
- تحقق HMAC للويبهوك
- تحويل `orders/create` وإرساله إلى ERP (`orders/import`)
- دعم ERP auth بطريقتين: `bearer` أو `basic`

## متغيرات البيئة (إجباري)

- `SHOPIFY_SHOP_DOMAIN`
- `SHOPIFY_ADMIN_ACCESS_TOKEN`
- `SHOPIFY_WEBHOOK_SECRET`
- `ERP_BASE_URL`
- `ERP_AUTH_MODE` (`bearer` أو `basic`)
- إذا `bearer`:
  - `ERP_API_KEY`
- إذا `basic`:
  - `ERP_USERNAME`
  - `ERP_PASSWORD`

راجع المثال في `.env.example`.

## تشغيل محلي

```bash
cp .env.example .env
# عدّل القيم
set -a; source .env; set +a
python app.py
```

بعدها:
- `http://localhost:8080/health`
- Webhook URL يكون: `http://localhost:8080/webhooks/shopify`

## تشغيل على هوست (Production)

1. ارفع المشروع على السيرفر.
2. اضبط `.env` بالقيم الصحيحة.
3. شغّل الخدمة:

```bash
set -a; source .env; set +a
nohup python app.py > app.log 2>&1 &
```

4. اربط Shopify webhook على:

`https://YOUR-HOST/webhooks/shopify`

5. Shopify scopes المطلوبة:
- `read_orders`
- `read_products`
- `write_inventory`
- `read_inventory`

## ملاحظات

- أي متغير ناقص هيرجع خطأ واضح (مش silent failure).
- لو ERP بيستخدم username/password استخدم `ERP_AUTH_MODE=basic`.
