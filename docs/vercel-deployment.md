# Deploying on Vercel

Deploy the application as two Vercel projects from this repository. Keeping the
frontend and API separate prevents the FastAPI function from handling static
site routes and gives each project an independent deployment URL.

## 1. Provision PostgreSQL

Create a managed PostgreSQL database (for example, Neon, Supabase, or another
provider) and copy its SQLAlchemy-compatible connection string. It must use the
following form:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=require
```

## 2. Deploy the API

1. Import the Git repository into Vercel as a new project.
2. Keep the repository root as the project's Root Directory.
3. Vercel detects `app.py`, which exposes the FastAPI application in
   `backend.main`.
4. Add these Environment Variables for Production (and Preview if required):

   | Name | Value |
   | --- | --- |
   | `DATABASE_URL` | The managed PostgreSQL connection string |
   | `SECRET_KEY` | A unique random value of at least 32 characters |
   | `ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
   | `CORS_ORIGINS` | The deployed frontend origin, for example `https://quiz-frontend.vercel.app` |

5. Deploy and verify `https://<api-project>.vercel.app/api/health` returns a
   successful health response.

Never commit a production `.env` file or database password. Set secrets only in
Vercel's Environment Variables UI or with its CLI.

## 3. Deploy the frontend

1. Import the same Git repository into Vercel as a second project.
2. Set its Root Directory to `frontend`.
3. Deploy it as a static site.

The frontend is currently in Offline Demo Mode. Before production launch, add
its deployed API base URL as a frontend environment/config value and replace the
localStorage-only data flows with API calls.

## 4. Final production checks

- Update the API's `CORS_ORIGINS` with the actual frontend URL and redeploy it.
- Check `/api/health` and `/docs` from the deployed API.
- Register, log in, load quizzes, start an attempt, submit answers, and view
  history from the deployed frontend.
- Use a separate database and separate secrets for Preview and Production.
