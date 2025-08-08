
# ⚙️ Agent Prompt Sheet: MVP Fixes for Quick Vendor

This prompt sheet contains a set of well-defined tasks based on user feedback and logs. Follow each prompt step by step. **Do not hallucinate**. Stick strictly to the instructions and the application context.

---

## 🔧 Prompt 1: Fix Broken Image Upload & Display

> **Issue:**  
The frontend is failing to display product images due to `404` errors when attempting to load them from the `/uploads/` path.

> **Fix Instructions:**  
- Verify FastAPI serves static/media files correctly.
- Ensure image paths are saved properly in PostgreSQL (Render).
- Make sure returned URLs are accessible and public.

> **Context:**  
Backend: FastAPI | Frontend: React | Database: PostgreSQL on Render

---

## 🔧 Prompt 2: Fix bcrypt Compatibility Error

> **Issue:**  
`AttributeError: module 'bcrypt' has no attribute '__about__'`

> **Fix Instructions:**  
- Downgrade or upgrade as necessary: `bcrypt==4.0.1`, `passlib==1.7.4`
- Rebuild environment to match dependencies.

> **Context:**  
Backend auth with FastAPI. PostgreSQL is used for user data.

---

## 🔧 Prompt 3: Fix Image Upload FormData Warning

> **Issue:**  
Backend warning: `Skipping data after last boundary`

> **Fix Instructions:**  
- Check how React frontend sends `FormData`.
- Verify `Content-Type` boundary headers.
- Ensure FastAPI receives all fields correctly.

> **Context:**  
React + FastAPI. Files stored locally; metadata stored in PostgreSQL.

---

## 🔧 Prompt 4: Fix Product Deletion (400 Bad Request)

> **Issue:**  
Deleting a product results in 400 Bad Request.

> **Fix Instructions:**  
- Check route `/api/products/{product_id}` supports DELETE.
- Ensure product_id exists and is validated.
- Cleanly delete associated image links if any.

> **Context:**  
Backend: FastAPI | Database: PostgreSQL on Render

---

## 🔧 Prompt 5: Prevent 307 Redirect on Product Fetch

> **Issue:**  
`GET /api/products` triggers a `307 Temporary Redirect`

> **Fix Instructions:**  
- Normalize routes in FastAPI (e.g., avoid trailing slash conflicts).
- Align frontend request paths with backend expectations.

> **Context:**  
Data source: PostgreSQL on Render

---

## 🔧 Prompt 6: Prevent Feedback Resubmission

> **Issue:**  
Multiple feedback form submissions possible.

> **Fix Instructions:**  
- Disable submit button after one click.
- Add loading indicator and debounce.
- Only store feedback once in PostgreSQL.

> **Context:**  
React + FastAPI + PostgreSQL (Render)

---

## 🚨 Final Instructions

- Do not go outside of prompt scope.
- Stick to the application context: FastAPI backend, React frontend, PostgreSQL on Render.
- Do not hallucinate or create components/features that were not explicitly requested.
- Execute each task one at a time.

---
