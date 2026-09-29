# Fictional MRI Prior Authorization Assistant

Python 3.11+ demo using synthetic data only. **No real patient data.** Not a clinical decision system.

## Setup and run

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env  # On Windows, copy .env.example .env
# Edit .env and set GEMINI_API_KEY for real LLM use.
python web.py                  # visit http://127.0.0.1:8000
python cli.py P001 data/P001.txt
python test.py                 # no API key required; simulated reader and reviewer
```

To share a live demo through GitHub and a Python host, follow [DEPLOY.md](DEPLOY.md).

## Workflow

```text
Patient ID + note -> MCP get_patient/get_rule -> Reader agent (Gemini JSON)
  -> Decision agent (ordered Python rule) -> LangGraph interrupt
  -> human yes: final decision / human no: exact rejection message
```

`mcp_server.py` is the single official-SDK stdio server; the workflow accesses patient and rule files **only via its two tools**. The note is input to the graph. Google's Gemini LLM extracts two nullable week values; deterministic code applies the tool-supplied thresholds and rule order. Get a Gemini API key at https://aistudio.google.com/api-keys (a free tier is available for eligible models/accounts). An `InMemorySaver` checkpointer and unique thread ID preserve the pending proposal across review. The web page and CLI both show a *proposed* recommendation before accepting a reviewer answer. `test.py` uses a simulated LLM extraction but exercises the real MCP subprocess, graph interrupt, and yes/no resume. The mock PDFs in `data/` are supplementary fictional documents; the app accepts plain-text notes.

Assumptions: a note may express unambiguous durations in non-week units, converted to weeks; ambiguous durations remain null. Invalid reader output is an error. The demo holds pending reviews in memory and runs in one process; restarting it discards pending reviews. It uses synthetic data only and is not for real medical decisions. An unknown patient or tool failure returns an error, not a decision.

AI coding assistant used: OpenAI Codex (ChatGPT Work) generated the code and synthetic PDFs; human review remains required for every outcome.
