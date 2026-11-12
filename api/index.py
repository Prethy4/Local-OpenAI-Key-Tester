import os
import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI, AuthenticationError, RateLimitError, APIError

app = FastAPI(title="OpenAI Key Credit Checker")


class KeyRequest(BaseModel):
    api_key: str


HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenAI API Key & Credit Tester</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    code, pre, .font-mono {
      font-family: 'JetBrains Mono', monospace;
    }
    .gradient-bg {
      background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 60%, #030712 100%);
    }
    .glass-panel {
      background: rgba(30, 41, 59, 0.7);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
  </style>
</head>
<body class="min-h-screen gradient-bg text-slate-100 flex flex-col items-center justify-center p-4 selection:bg-emerald-500 selection:text-white">

  <!-- Header & Container -->
  <div class="w-full max-w-xl mx-auto space-y-6">
    
    <!-- Branding Header -->
    <div class="text-center space-y-2">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold tracking-wide uppercase">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        Live API & Quota Verification
      </div>
      <h1 class="text-3xl sm:text-4xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
        OpenAI Key Tester
      </h1>
      <p class="text-slate-400 text-sm max-w-md mx-auto">
        Test if your OpenAI key is authentic and has active available billing credits or quota.
      </p>
    </div>

    <!-- Main Card -->
    <div class="glass-panel rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
      <!-- Glow accent -->
      <div class="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -bottom-24 -left-24 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <form id="checkForm" onsubmit="handleTest(event)" class="space-y-5 relative">
        <div>
          <label for="apiKey" class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            OpenAI API Key
          </label>
          <div class="relative">
            <input
              id="apiKey"
              type="password"
              placeholder="sk-proj-... or sk-..."
              required
              class="w-full px-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-slate-100 placeholder-slate-500 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all pr-12 shadow-inner"
            />
            <button
              type="button"
              onclick="toggleKeyVisibility()"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 transition-colors p-1"
              title="Show/Hide Key"
            >
              <svg id="eyeIcon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
          </div>
          <p class="text-xs text-slate-500 mt-2 flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            Key is sent directly through HTTPS and is never stored or logged.
          </p>
        </div>

        <button
          type="submit"
          id="submitBtn"
          class="w-full py-3.5 px-6 rounded-xl font-semibold text-sm bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-lg shadow-emerald-500/20 active:scale-[0.99] transition-all flex items-center justify-center gap-2"
        >
          <span id="btnText">Check Key & Available Credit</span>
          <svg id="spinner" class="hidden animate-spin w-5 h-5 text-slate-950" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </button>
      </form>

      <!-- Results Container -->
      <div id="resultBox" class="hidden mt-6 pt-6 border-t border-slate-700/60 space-y-4"></div>

    </div>

    <!-- Explanatory note -->
    <div class="text-center text-xs text-slate-500 space-y-1">
      <p>Tests with a minimal 1-token probe using <code class="text-slate-400 bg-slate-800/80 px-1 py-0.5 rounded">gpt-4o-mini</code> (costs &lt; $0.000001).</p>
      <p>Checks HTTP 200 (Active) vs HTTP 429 (<code class="text-slate-400">insufficient_quota</code>) vs HTTP 401 (Invalid).</p>
    </div>

  </div>

  <script>
    function toggleKeyVisibility() {
      const input = document.getElementById('apiKey');
      if (input.type === 'password') {
        input.type = 'text';
      } else {
        input.type = 'password';
      }
    }

    async function handleTest(e) {
      e.preventDefault();
      const apiKey = document.getElementById('apiKey').value.trim();
      const submitBtn = document.getElementById('submitBtn');
      const btnText = document.getElementById('btnText');
      const spinner = document.getElementById('spinner');
      const resultBox = document.getElementById('resultBox');

      if (!apiKey) return;

      submitBtn.disabled = true;
      btnText.textContent = "Testing Key & Credits...";
      spinner.classList.remove('hidden');
      resultBox.classList.add('hidden');
      resultBox.innerHTML = '';

      try {
        const res = await fetch('/api/check-key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ api_key: apiKey })
        });

        const data = await res.json();
        renderResult(data);
      } catch (err) {
        renderResult({
          status: 'error',
          title: 'Network Error',
          message: 'Failed to communicate with API server: ' + err.message
        });
      } finally {
        submitBtn.disabled = false;
        btnText.textContent = "Check Key & Available Credit";
        spinner.classList.add('hidden');
        resultBox.classList.remove('hidden');
      }
    }

    function renderResult(data) {
      const box = document.getElementById('resultBox');
      
      let badgeClass = '';
      let badgeText = '';
      let borderClass = '';
      let icon = '';

      if (data.status === 'active_credit') {
        badgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
        borderClass = 'border-emerald-500/40 bg-emerald-950/20';
        badgeText = 'Active Credits Available';
        icon = `<svg class="w-6 h-6 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
      } else if (data.status === 'no_credit') {
        badgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
        borderClass = 'border-amber-500/40 bg-amber-950/20';
        badgeText = 'No Available Credit (Quota Exceeded)';
        icon = `<svg class="w-6 h-6 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`;
      } else if (data.status === 'invalid_key') {
        badgeClass = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
        borderClass = 'border-rose-500/40 bg-rose-950/20';
        badgeText = 'Invalid or Revoked Key';
        icon = `<svg class="w-6 h-6 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
      } else {
        badgeClass = 'bg-slate-500/10 text-slate-300 border-slate-500/30';
        borderClass = 'border-slate-700 bg-slate-900/50';
        badgeText = 'Test Result';
        icon = `<svg class="w-6 h-6 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
      }

      box.innerHTML = `
        <div class="border rounded-xl p-4 sm:p-5 ${borderClass} space-y-3">
          <div class="flex items-start gap-3">
            ${icon}
            <div class="space-y-1 flex-1">
              <div class="flex items-center justify-between gap-2 flex-wrap">
                <span class="text-sm font-bold text-white">${data.title || badgeText}</span>
                <span class="text-xs px-2.5 py-0.5 rounded-full border font-medium ${badgeClass}">${badgeText}</span>
              </div>
              <p class="text-xs text-slate-300 leading-relaxed">${data.message}</p>
            </div>
          </div>

          <div class="pt-2 border-t border-slate-800/80 text-xs text-slate-400 space-y-1 font-mono">
            <div class="flex justify-between">
              <span>Authentication:</span>
              <span class="${data.auth_ok ? 'text-emerald-400' : 'text-rose-400'} font-semibold">
                ${data.auth_ok ? 'PASS (Valid Key)' : 'FAIL'}
              </span>
            </div>
            <div class="flex justify-between">
              <span>Generation Quota:</span>
              <span class="${data.status === 'active_credit' ? 'text-emerald-400' : 'text-amber-400'} font-semibold">
                ${data.status === 'active_credit' ? 'AVAILABLE' : (data.auth_ok ? 'EXHAUSTED / $0' : 'N/A')}
              </span>
            </div>
            ${data.model ? `
            <div class="flex justify-between">
              <span>Tested Model:</span>
              <span class="text-slate-200">${data.model}</span>
            </div>` : ''}
          </div>

          ${data.status === 'no_credit' ? `
          <div class="mt-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200">
            <strong>How to add credits:</strong> Go to your OpenAI Dashboard under <a href="https://platform.openai.com/settings/organization/billing" target="_blank" class="underline text-amber-300 hover:text-white font-medium">Billing Settings</a> and add prepaid balance.
          </div>` : ''}
        </div>
      `;
    }
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return HTML_CONTENT


@app.post("/api/check-key")
async def check_key(req: KeyRequest):
    key = req.api_key.strip()
    if not key:
        return {
            "status": "error",
            "title": "Missing API Key",
            "message": "Please enter an OpenAI API key.",
            "auth_ok": False,
        }

    client = OpenAI(api_key=key)

    # Step 1: Authentication Check
    try:
        client.models.list()
        auth_ok = True
    except AuthenticationError as e:
        return {
            "status": "invalid_key",
            "title": "Authentication Failed",
            "message": "The API key provided is invalid, malformed, or has been revoked.",
            "auth_ok": False,
            "error_detail": str(e),
        }
    except Exception as e:
        return {
            "status": "error",
            "title": "Connection Error",
            "message": f"Failed to connect to OpenAI API: {str(e)}",
            "auth_ok": False,
        }

    # Step 2: Quota & Token Generation Check
    test_models = ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"]

    for model_name in test_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            return {
                "status": "active_credit",
                "title": "Key is Active & Funded!",
                "message": f"Successfully performed test completion using {response.model}. This key has available credit/quota.",
                "auth_ok": True,
                "model": response.model,
            }

        except RateLimitError as e:
            err_body = getattr(e, "body", {}) or {}
            err_code = err_body.get("code") if isinstance(err_body, dict) else None

            if err_code == "insufficient_quota" or "quota" in str(e).lower():
                return {
                    "status": "no_credit",
                    "title": "Quota Exceeded ($0 Balance)",
                    "message": "Your API key is valid and authentic, but your OpenAI account has exhausted its available credits or has $0 prepaid balance.",
                    "auth_ok": True,
                    "model": model_name,
                }
            else:
                return {
                    "status": "rate_limited",
                    "title": "Rate Limit Reached",
                    "message": f"Key is valid, but hit rate limit: {e.message}",
                    "auth_ok": True,
                    "model": model_name,
                }

        except APIError as e:
            if "model" in str(e).lower() and ("not found" in str(e).lower() or "does not exist" in str(e).lower()):
                continue
            return {
                "status": "error",
                "title": "API Error",
                "message": f"OpenAI returned an error: {e.message if hasattr(e, 'message') else str(e)}",
                "auth_ok": True,
            }
        except Exception as e:
            return {
                "status": "error",
                "title": "Unexpected Error",
                "message": str(e),
                "auth_ok": True,
            }

    return {
        "status": "error",
        "title": "Test Inconclusive",
        "message": "None of the standard test models (gpt-4o-mini, gpt-3.5-turbo, gpt-4o) were accessible.",
        "auth_ok": True,
    }

