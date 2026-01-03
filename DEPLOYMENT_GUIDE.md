# Free Hosting Guide: Delhi Water-Logging Platform

For a hackathon MVP, you can host this entire stack for **$0** using these services.

## 📁 File Organization & Repository Setup

You should ideally have two separate GitHub repositories (or two distinct deployments from one repo).

### 1. Backend Hub (Render/Supabase)
**Upload these files/folders from your `backend/` directory:**
*   `main.py` (entry point)
*   `requirements.txt` (dependencies)
*   `routes/`, `models/`, `schemas/`, `services/`, `gis/`, `ml/` (logic folders)
*   `database.py`, `config.py` (core setup)
*   `alembic/`, `alembic.ini` (migrations)
*   `data/` (essential GeoJSON and ward data)
*   **DO NOT UPLOAD**: `__pycache__`, `.env`, `uploads/` (these are local/private)

### 2. Frontend Hub (Vercel)
**Upload these files/folders from your `frontend/` directory:**
*   `index.html`
*   `package.json` & `package-lock.json`
*   `src/` (all your components and logic)
*   `vite.config.ts`, `tailwind.config.js`, `postcss.config.cjs`
*   `tsconfig.json`

---

## 🏗️ Step-by-Step Deployment

### 1. Database (Supabase)
1.  **Create Project**: Sign up at [Supabase](https://supabase.com/).
2.  **Enable PostGIS**: Go to **SQL Editor** and run:
    ```sql
    CREATE EXTENSION postgis;
    ```
3.  **Connection**: Copy the "Connection String" (URI) to your Backend's `.env` (locally) and Render's environment variables.

### 2. Backend (Render)
1.  **Connect GitHub**: Select your backend repo.
2.  **Runtime**: Python 3.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables**:
    *   `DATABASE_URL`: Your Supabase URI.
    *   `JWT_SECRET_KEY`: This is a long random string used to sign your login tokens. **Keep it secret!**
        *   *How to generate one:* Run `python -c "import secrets; print(secrets.token_urlsafe(32))"` in your terminal and copy the result.
    *   `CORS_ORIGINS`: `["https://your-frontend.vercel.app"]`

### 3. Frontend (Vercel)
1.  **Edit API URL**: In `src/services/api.ts`, change line 4:
    ```typescript
    const API_BASE_URL = 'https://your-backend.onrender.com'; 
    ```
2.  **Connect GitHub**: Select your frontend repo.
3.  **Framework Preset**: Vite.
4.  **Build Command**: `npm run build`
5.  **Output Directory**: `dist`

---

## 🚀 The "Hackathon Demo" Cheat Sheet
| Task | Action |
| :--- | :--- |
| **Seeding Data** | Once the Supabase DB is up, run `python scripts/seed_data.py` locally on your machine with the `DATABASE_URL` changed to the Supabase URL. This pushes the maps/reports to the cloud. |
| **Cold Starts** | Render's free tier "sleeps". **Wake it up** by clicking your URL 2 minutes before the judges arrive! |
| **PostGIS Check** | If the map doesn't show wards, ensure you ran the `CREATE EXTENSION postgis;` query in Supabase. |
