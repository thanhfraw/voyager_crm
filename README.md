# Customer Database App

FastAPI backend + HTML frontend with auth, CRUD, Excel import, and version history.

---

## Stack
- **Backend**: FastAPI (Python) → Railway
- **Frontend**: HTML/JS → Vercel
- **Database**: PostgreSQL → Supabase

---

## Step 1 — Supabase (Database)

1. Go to https://supabase.com → New project
2. Save your **database password**
3. Go to **SQL Editor** → paste contents of `schema.sql` → Run
4. Go to **Settings → Database** → copy the **Connection string (URI)**
   - Looks like: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`

---

## Step 2 — Create first admin user

In Supabase SQL Editor, run:

```sql
-- Replace 'yourpassword' with a real password
-- You will get the hash by running the setup script below
```

Or use the setup script after deploying backend:
```
POST /api/auth/users
{ "username": "admin", "password": "yourpassword", "role": "admin" }
```
(Temporarily remove auth from create_user endpoint for first run, then re-add)

---

## Step 3 — Railway (Backend)

1. Go to https://railway.app → New Project → Deploy from GitHub
2. Select your repo, choose the `backend/` folder as root
3. Add environment variables:
   ```
   DATABASE_URL=postgresql://...  (from Supabase)
   SECRET_KEY=any-long-random-string
   FRONTEND_URL=https://your-app.vercel.app
   ```
4. Railway will auto-detect `Procfile` and deploy
5. Copy your Railway app URL: `https://your-app.railway.app`

---

## Step 4 — Update frontend API URL

In `frontend/index.html`, find line:
```js
const API = 'https://YOUR-APP.railway.app';
```
Replace with your actual Railway URL.

---

## Step 5 — Vercel (Frontend)

1. Go to https://vercel.com → New Project → Import from GitHub
2. Set **Root Directory** to `frontend/`
3. Deploy — done!

---

## Project Structure

```
customer-app/
├── schema.sql              ← Run in Supabase
├── .gitignore
├── backend/
│   ├── main.py             ← FastAPI entry point
│   ├── config.py           ← DB connection, settings
│   ├── models.py           ← SQLAlchemy table definitions
│   ├── auth.py             ← JWT auth, role guards
│   ├── requirements.txt
│   ├── Procfile            ← Railway start command
│   ├── .env.example        ← Copy to .env
│   └── routers/
│       ├── auth_router.py      ← Login, users, roles
│       ├── customers_router.py ← CRUD + history + revert
│       └── import_router.py    ← Excel import
└── frontend/
    ├── index.html          ← Full app (single file)
    └── vercel.json
```

---

## Roles

| Action | Viewer | Editor | Admin |
|--------|--------|--------|-------|
| Search / view | ✓ | ✓ | ✓ |
| Add customer | — | ✓ | ✓ |
| Edit customer | — | ✓ | ✓ |
| Delete customer | — | — | ✓ |
| Import Excel | — | ✓ | ✓ |
| View history | ✓ | ✓ | ✓ |
| Revert record | — | — | ✓ |
| Manage users | — | — | ✓ |

---

## Excel Import Format

Your Excel file columns map automatically:

| Excel Column | Database Field |
|---|---|
| CustomerID | customer_id |
| ShortName | short_name |
| CustKeyCode | cust_key_code |
| CustomerNameEN | name_en |
| CustomerNameVN | name_vn |
| TaxCode | tax_code |
| CustomerTypeID | customer_type (by name) |
| NationalityID | nationality (by name) |
| CompanyPhone | phone |
| CompanyEmail | email |
| Status | status |

Existing records (same CustomerID) will be **updated**, new ones **inserted**.

---

## Local Development

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # fill in your values
uvicorn main:app --reload
```

API docs available at: http://localhost:8000/docs
