# Deployment Steps (Render or Vercel)

## 1) Supabase setup (do this once)

1. Open your Supabase project dashboard.
2. Go to `SQL Editor` and run `schema.sql` from this project.
3. Go to `Project Settings` -> `API`.
4. Copy these values:
   - `Project URL` -> this is `SUPABASE_URL`
   - `service_role` key -> this is `SUPABASE_SERVICE_ROLE_KEY`

## 2) Local `.env` file

The file is already created: `.env`

Put these values:

```env
FLASK_SECRET_KEY=put_any_long_random_secret
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY
SUPABASE_STORAGE_BUCKET=prescriptions
FLASK_DEBUG=1
```

Generate a secret quickly:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 3) Deploy on Render (recommended for Flask)

1. Push this project to GitHub.
2. Open Render -> `New` -> `Blueprint`.
3. Select your GitHub repository.
4. Render will detect `render.yaml`.
5. In Render service environment variables, add:
   - `FLASK_SECRET_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_STORAGE_BUCKET` (value: `prescriptions`)
   - `FLASK_DEBUG` (value: `0`)
6. Click `Apply` / `Deploy`.
7. After deploy, open the Render URL and test register/login/upload/list.

## 4) Deploy on Vercel (alternative)

1. Push this project to GitHub.
2. Open Vercel -> `Add New` -> `Project`.
3. Import your GitHub repository.
4. Vercel auto-detects Flask from `app.py` (no extra Vercel config needed).
5. In Vercel -> `Settings` -> `Environment Variables`, add:
   - `FLASK_SECRET_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_STORAGE_BUCKET` (value: `prescriptions`)
   - `FLASK_DEBUG` (value: `0`)
6. Deploy.
7. Open Vercel URL and test register/login/upload/list.

## 5) What URL to paste where

- In `.env`, `SUPABASE_URL` must be your Supabase `Project URL`.
- In `.env`, `SUPABASE_SERVICE_ROLE_KEY` must be your Supabase `service_role` key.
- You do not need to paste Render/Vercel site URL into Supabase for this app flow.
