# Siarah: API contract and backend handover

This document is a proposed backend contract for the current static frontend preview. The API, order submission, and Razorpay integration described here are not implemented. Update this contract with the project owner before building the backend.

## 1. What the frontend does today

The preview lets visitors choose a design, fabric, print and fit, add configured pieces to a browser-stored bag, and review the checkout screen. The payment-preview dialog explicitly says that no payment or order is submitted. It does not create fake order IDs or successful payment results, and it does not clear the bag.

There are no frontend API calls today. The checkout fields are validated in the page but are not sent to a server or saved by the site. The bag uses browser storage; a production backend must validate all submitted data and calculate prices independently.

The endpoints below describe a future integration. They must not be treated as live behavior or advertised as available until implemented and verified.

## 2. Identifiers

| Thing | Values |
|---|---|
| fabric | `linen-prints`, `linen-plains`, `chanderi-prints`, `chanderi-embroidery`, `organza`, `cotton-satin`, `satin`, `lace` |
| design | `"01"` to `"26"` (strings) |
| print | `"01"` to `"18"` (strings) |
| size | `XS`, `S`, `M`, `L`, `XL`, or custom measurements |

- `satin` and `lace` exist as fabrics but have no designs or prints yet. Reject them with `ITEM_UNAVAILABLE` until they are filled in.
- Prints apply to every fabric (client's rule). Satin and lace will get their own design and print sets later.
- Catalog data lives in `designs.json` and `prints.json` (names, taglines, images).
- Design names 11 and 13, 12 and 14, 23 and 25 repeat. Always use ids, never names.

## 3. Prices

- Price depends on the fabric only. Designs and prints do not change the price. One piece costs:

| fabric | price (INR) | paise |
|---|---|---|
| linen-prints, linen-plains, chanderi-prints, chanderi-embroidery | 9,999 | 999900 |
| cotton-satin | 12,999 | 1299900 |
| satin | 15,999 | 1599900 |
| organza | 16,999 | 1699900 |
| lace | 18,999 | 1899900 |

- The server owns all prices. The frontend only displays them.
- The server must ignore any price the client sends and recompute from its own price table.
- Shipping is charged separately, on top of the item prices. The server adds it when creating the order and returns `shippingPaise` and the final `amountPaise` (items plus shipping). The shipping amount or rule is still to be confirmed with the client.
- GST: not yet known whether the prices include it. To be confirmed with the client.
- All money on the wire is in paise (integer). 1 rupee = 100 paise.

## 4. Endpoints

### 4.1 `GET /api/catalog` (optional)

Returns fabrics, designs, prints and prices so the frontend can drop its hardcoded price formula.

```json
{
  "fabrics": [{ "id": "organza", "name": "Organza", "available": true, "pricePaise": 1699900 }],
  "designs": [{ "id": "07", "name": "Ruffled Romance Corset" }],
  "prints":  [{ "id": "08", "name": "Ruby Orchard" }]
}
```

### 4.2 `POST /api/orders`

Creates an order in `pending_payment` and a Razorpay order.

Request:

```json
{
  "items": [
    {
      "fabric": "organza",
      "design": "07",
      "print": "08",
      "size": "M",
      "measurements": null
    },
    {
      "fabric": "cotton-satin",
      "design": "12",
      "print": "03",
      "size": null,
      "measurements": { "bust": 88, "waist": 70, "hips": 96 }
    }
  ],
  "customer": {
    "name": "Asha Rao",
    "phone": "9876543210",
    "email": "asha@example.com",
    "address": "12 Road No 5, Banjara Hills",
    "city": "Hyderabad",
    "state": "Telangana",
    "pin": "500034"
  }
}
```

Rules:
- `items`: 1 or more. Each item has exactly one of `size` or `measurements`.
- `measurements`: bust, waist, hips in cm, numbers. Set sensible min and max limits.
- `phone`: at least 10 digits. `pin`: exactly 6 digits. `email`: valid format. All customer fields required.
- Check every fabric, design and print id against the catalog.

Response `201`:

```json
{
  "orderId": "SR-1042",
  "razorpayOrderId": "order_Nxxxxxxxx",
  "shippingPaise": 0,
  "amountPaise": 900000,
  "currency": "INR",
  "keyId": "rzp_test_xxxxx"
}
```

### 4.3 Razorpay Checkout (frontend)

The frontend opens Razorpay Checkout with `razorpayOrderId`, `amountPaise` and `keyId`. On success Razorpay returns `razorpay_payment_id`, `razorpay_order_id` and `razorpay_signature`.

### 4.4 `POST /api/payments/verify`

Request:

```json
{
  "orderId": "SR-1042",
  "razorpay_order_id": "order_Nxxxxxxxx",
  "razorpay_payment_id": "pay_Nxxxxxxxx",
  "razorpay_signature": "..."
}
```

Server: compute HMAC SHA256 of `razorpay_order_id|razorpay_payment_id` with the Razorpay key secret and compare with the signature. If it matches, set status `paid`, store the payment id, and trigger notifications (section 7).

Response `200`: `{ "ok": true, "orderId": "SR-1042", "status": "paid" }`

On mismatch: `400 PAYMENT_VERIFICATION_FAILED`. The frontend must not clear the bag or show the success page unless `ok` is true.

### 4.5 `POST /api/webhooks/razorpay`

Razorpay calls this directly. It is the source of truth if the customer closes the tab before verify runs.
- Verify the `X-Razorpay-Signature` header with the webhook secret.
- Handle `payment.captured` (mark `paid`) and `payment.failed` (mark `payment_failed`).
- Must be idempotent: the same event can arrive more than once. Never send duplicate confirmation messages.

### 4.6 `GET /api/orders/:id` (optional)

Public order status for the confirmation page. Use an unguessable token in the link, not the sequential order number.

### 4.7 Admin (login required)

- `GET /api/admin/orders?status=paid`: list with filters
- `GET /api/admin/orders/:id`: full detail, including measurements
- `PATCH /api/admin/orders/:id`: change status, add tracking info

### 4.8 `POST /api/subscribe` (optional)

Footer newsletter signup. Request: `{ "email": "asha@example.com" }`. Response `200`: `{ "ok": true }`. Validate the email, ignore duplicates quietly, and rate limit. The preview only checks the format and shows a thank-you message; nothing is saved yet.

## 5. Order statuses

`pending_payment`, `paid`, `payment_failed`, `in_production`, `shipped`, `delivered`, `cancelled`

## 6. Suggested data model

`orders`: id, order_number (unique, e.g. SR-1042), status, customer_name, phone, email, address, city, state, pin, amount_paise, razorpay_order_id, razorpay_payment_id, created_at, paid_at

`order_items`: id, order_id, fabric_id, design_id, print_id, size, bust_cm, waist_cm, hips_cm, unit_price_paise

Catalog and price table: tables or a config file. Order number must be unique and sequential (the preview uses a random one).

## 7. Notifications after payment

- Email to the customer: order number, items, ship-to address, dispatch in 2 to 3 weeks.
- Email to the shop: new paid order with measurements.
- WhatsApp to the customer: needs WhatsApp Business API approval, which can take days. Fallback: email plus a click-to-chat link.

## 8. Errors

Format: `{ "error": { "code": "...", "message": "...", "fields": { "pin": "Enter 6 digits." } } }`

| Code | HTTP | When |
|---|---|---|
| `VALIDATION_FAILED` | 422 | bad or missing fields |
| `ITEM_UNAVAILABLE` | 409 | unknown id, or satin and lace not yet available |
| `PAYMENT_VERIFICATION_FAILED` | 400 | signature mismatch |
| `NOT_FOUND` | 404 | unknown order |
| `RATE_LIMITED` | 429 | too many requests |

## 9. Security checklist

- Price always recomputed on the server.
- Razorpay key secret and webhook secret live in environment variables only, never in the frontend.
- Only the public `keyId` goes to the browser.
- CORS limited to the site's domain. HTTPS everywhere.
- Rate limit order creation.
- No card data is ever touched or stored. Razorpay hosts the payment form.
- Store only the customer data the shop needs.

## 10. Frontend changes needed when the backend is ready

1. Add a clear API base URL setting and implement real `fetch` calls for order creation and verification.
2. Integrate Razorpay Checkout using the server-created order and public key ID.
3. Clear the bag only after the server verifies payment. Handle payment failure, cancellation, retry, and pending status without claiming success prematurely.
4. Current bag items store `m: { bust, waist, hips }` (null for standard sizing), and `s` is null when custom measurements are used. When calling `POST /api/orders`, map `s` to `size` and `m` to `measurements`.

## 11. Open questions for the client

- Shipping charge: flat fee, by region, or by weight? What amount? Delivery estimate?
- GST: are the prices inclusive or exclusive?
- Cancellation and returns policy for made-to-order pieces
- Cash on delivery: yes or no
- Satin and lace: number of designs and prints, shared or separate
- Account login and order history are not implemented. Decide whether they belong in the production scope; the account route is currently a placeholder and its header link is hidden.

## 12. Handover package

- `src/template.html`, `scripts/build.py`, `requirements.txt`, and `vercel.json`
- `data/designs.json`, `data/prints.json`, and the `assets/` image folders
- `README.md` and this API handover contract
- Razorpay test keys, once the account exists
