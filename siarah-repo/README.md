# Siarah

Siarah is a static, browser-based preview for a made-to-order corset collection. It uses HTML, CSS, vanilla JavaScript, JSON catalogue data, and a Python build script. It is a public demonstration, not a transactional storefront.

## What's included

- `src/template.html` — site layout, styles, hash routes, customiser, bag, and preview checkout.
- `data/designs.json` and `data/prints.json` — catalogue content and image paths.
- `assets/` — design and print artwork.
- `scripts/build.py` — embeds the artwork and writes the self-contained `dist/index.html`.
- `docs/API_CONTRACT.md` — proposed backend and payment handover contract; it is not implemented by this frontend.
- `vercel.json` — Vercel build and static output settings.

## Build and preview

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build.py
python3 -m http.server --directory dist 8000
```

Open `http://localhost:8000/`. The generated `dist/` directory is ignored by Git because Vercel regenerates it during deployment. Do not edit `dist/index.html` by hand.

## Demo limits

- The bag and customiser use browser storage. There is no order API, payment gateway, customer account, or newsletter storage.
- Checkout is a preview only. It does not submit an order or payment, and the bag remains unchanged. Checkout fields stay in the current page and are not sent to a server or saved by the site.
- `.env.example` lists future backend placeholders only; this static preview does not read those variables.
- Satin and lace are marked as coming soon. Shipping, GST, dispatch estimates, support details, and the returns policy still need owner confirmation.
- Account and About pages are informational placeholders. Hero video and lifestyle photography have not been supplied.

Do not treat this project as ready to accept customer orders or real payments until an approved backend, payment integration, customer-facing policies, and support details are in place.

## Vercel

The root `vercel.json` selects Vercel's **Other** preset, creates a project-local Python virtual environment, installs the dependency there, runs `scripts/build.py` with that environment, and serves `dist/`. Deploy from the repository root so the source, assets, build script, and requirements file are available. The generated site uses an embedded asset bundle and hash-based routes, so it does not need a custom domain or route rewrite.

## Catalogue and pricing

The current preview contains 26 designs and 18 prints. Prices are displayed from the frontend's `PRICE` object for demonstration only; a production server must validate catalogue selections and calculate all prices itself. Do not change product names, IDs, prices, or measurement limits without owner approval.
