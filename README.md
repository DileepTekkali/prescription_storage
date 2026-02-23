# Flask + Supabase Prescription App

This project has:
- User registration with Gmail, username, age, password
- User login/logout
- Prescription image upload with selected date
- Save image in Supabase Storage
- Save prescription data in Supabase Database
- View all prescriptions with date

## 1) Supabase setup (first step)

1. Open your Supabase project.
2. Go to `SQL Editor`.
3. Open local file `schema.sql` from this project.
4. Copy and run the full SQL in Supabase SQL Editor.
5. Go to `Project Settings` -> `API`.
6. Copy:
   - `Project URL` (for `SUPABASE_URL`)
   - `service_role` key (for `SUPABASE_SERVICE_ROLE_KEY`)

## 2) Configure `.env`

File already exists: `.env`

Put your real values:

```env
FLASK_SECRET_KEY=your_long_random_secret
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY
SUPABASE_STORAGE_BUCKET=prescriptions
FLASK_DEBUG=1
```

Generate `FLASK_SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 3) Run locally

```bash
pip install -r requirements.txt
python3 app.py
```

Open:
- `http://127.0.0.1:5000`

## 4) Push code to GitHub

Run these commands in project folder:

```bash
git init
git add .
git commit -m "flask supabase app setup"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## 5) Deploy on Render (recommended)

1. Open Render dashboard.
2. Click `New` -> `Blueprint`.
3. Select your GitHub repo.
4. Render auto-detects `render.yaml`.
5. In Render service settings, add Environment Variables:
   - `FLASK_SECRET_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_STORAGE_BUCKET` = `prescriptions`
   - `FLASK_DEBUG` = `0`
6. Click `Apply` / `Deploy`.
7. Open your Render URL and test register/login/upload/all prescriptions.

## 6) Deploy on Vercel

1. Open Vercel dashboard.
2. Click `Add New` -> `Project`.
3. Import your GitHub repository.
4. Vercel auto-detects Flask from `app.py`.
5. Add Environment Variables:
   - `FLASK_SECRET_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_STORAGE_BUCKET` = `prescriptions`
   - `FLASK_DEBUG` = `0`
6. Click `Deploy`.
7. Open your Vercel URL and test app flow.

## 7) Important notes

- Do not commit `.env` to GitHub.
- Keep `SUPABASE_SERVICE_ROLE_KEY` private.
- You do not need to add Render/Vercel URL inside Supabase for this app flow.
