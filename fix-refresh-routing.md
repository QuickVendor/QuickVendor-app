# 🚧 Fixing Route Refresh Redirect Issue in Quick Vendor

**Created:** 2025-08-08 18:15 UTC

---

## 🧩 Problem Summary

Whenever a user refreshes the page on any route (e.g., `/dashboard`, `/login`), the application redirects them to the homepage (`/`). This breaks the expected routing behavior in a Single Page Application (SPA).

---

## ✅ Root Cause

**Client-side routing is not correctly supported in production on Render.**

When refreshing, Render tries to resolve `/dashboard` or `/login` as file paths — which do not exist — and defaults to the homepage or 404, causing unintended redirection.

---

## 🛠️ Solution Steps (Follow in Order)

### 1. 🔁 Add Rewrite Rule on Render

> Ensure all unknown routes point to `/index.html`.

If you're using **Render's redirect settings manually**:

- Go to **Render Dashboard → Your Static Site → Settings → Redirects/Rewrites**
- Add the following rule:

| Source | Destination   | Type    |
|--------|----------------|---------|
| `/*`   | `/index.html` | Rewrite |

If using a `render.yaml` file for infrastructure-as-code:

```yaml
routes:
  - type: rewrite
    source: /.*
    destination: /index.html
```

---

### 2. 🔍 Confirm React Router Setup

Ensure your frontend uses `BrowserRouter` (NOT `HashRouter`).

In `main.tsx` or `App.tsx`:

```tsx
import { BrowserRouter } from 'react-router-dom';

<BrowserRouter>
  <App />
</BrowserRouter>
```

---

### 3. 🔐 Handle Authentication on Refresh

If your app uses token-based auth in `localStorage`:

- On load, check if the token is valid.
- If invalid, redirect to `/login`.
- Never redirect to `/` unless explicitly required.

---

## ✅ Validation Checklist

- [ ] Refreshing on `/dashboard` stays on `/dashboard`
- [ ] Refreshing on `/login` stays on `/login`
- [ ] Token expiration redirects to `/login`, not `/`
- [ ] Homepage (`/`) still works normally

---

## 🚫 Agent Instructions

- Do NOT hallucinate solutions.
- Only follow the above steps in the order listed.
- Ensure your updates work for **PostgreSQL on Render**.
- Log any assumptions made in implementation.

---

**End of Instruction**
