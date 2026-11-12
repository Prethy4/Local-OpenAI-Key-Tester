# OpenAI API Key & Credit Tester

A lightweight web application & CLI tool to verify OpenAI API keys and check whether the associated account has active credits or is rate-limited/out of quota.

## Project Structure (Vercel Ready)
```text
├── api/
│   └── index.py         # Vercel Serverless Function & FastAPI app
├── app.py               # Local dev server runner
├── test_openai_key.py   # CLI tester script
├── requirements.txt     # Python dependencies for Vercel & local
└── vercel.json          # Vercel URL rewrite routing
```

## Running Locally
```bash
pip install -r requirements.txt
python app.py
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

## Deploying to Vercel

### Option 1: Using GitHub / Vercel Dashboard (Easiest)
1. Push this folder to a GitHub repository.
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Import your repository.
4. Leave the default settings (Framework Preset: **Other**) and click **Deploy**.

### Option 2: Using Vercel CLI
```bash
npm install -g vercel
vercel
```
Follow the interactive prompts to deploy.
