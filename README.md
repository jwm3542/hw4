# Campus Customs: Shop + AI Shopping Assistant (MGT 409E, HW 4)

A storefront website for **Campus Customs / Yale Bulldog Blue** with an AI chat clerk that answers honestly about price and stock from a local database, puts matching products on the page, and remembers logged-in shoppers.

- **Front end:** React + Vite + TypeScript (`frontend/`)
- **Back end:** FastAPI (`backend/main.py`), whose brain is a **PydanticAI agent** made of 4 files:
  - `backend/prompts/prompt.md`: system prompt (voice, tool rules, safety rules)
  - `backend/agent.py`: agent wiring (prompt, model tiers through Portkey, tools, session context)
  - `backend/tools.py`: read-only catalogue and inventory tools the agent calls
  - `backend/models.py`: Pydantic types for tool results, the agent's structured reply, and API payloads
- **Docs:** `output/harness.md` (how the system works and its specs), `output/usability.md`, `output/design.md`, `output/app_check.html` (screenshots from the live app), `output/audit_trail.json` (append-only agent log), `AI_prompts.md` (my prompt log)

## 1. Get the code and place the data pack

```bash
git clone <this repo URL> hw4
cd hw4
```

The database and product photos are **not** in this repo. Unzip the course data pack (`data.zip`) into the project folder so you have:

```
hw4/
  data/
    campus_customs.db
    products/            <- product .jpg images
  backend/
  frontend/
```

## 2. Add your API key

Copy `.env.example` to `.env` (in `hw4/` or `hw4/backend/`) and fill in your key. Never commit `.env`.

```bash
cp .env.example .env          # Windows: copy .env.example .env
```

```ini
PORTKEY_API_KEY=your-portkey-api-key
OPENAI_MODEL=gpt-5.6-luna            # fast tier (every turn)
OPENAI_MODEL_STANDARD=gpt-5.6-terra  # fallback 1
OPENAI_MODEL_SMART=gpt-6-astra       # fallback 2
```

All AI calls go through Portkey (`https://api.portkey.ai/v1`).

## 3. Run the back end (FastAPI, port 8000)

Requires Python 3.11+. From `hw4/backend`:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Check that it's up: <http://localhost:8000/api/health> should show `"ok": true`. If it's `false`, the data pack isn't in `hw4/data/`.

## 4. Run the front end (React + Vite, port 5173)

Requires Node 18+. In a second terminal, from `hw4/frontend`:

```bash
npm install
npm run dev
```

Open **<http://localhost:5173>**. Vite forwards `/api` and `/images` to the back end on port 8000, so keep both running.

## 5. Try it

- **Browse:** Home → Products → click any card for its product page (stock by size, size guide, "You may also like").
- **Chat:** click the brass bell 🛎️ in the bottom right ("Ask the Clerk"):
  - "What hoodies do you have?" → matching cards drop onto the page
  - On a product page: "Is this in stock in L?" → an honest answer from the database
- **Accounts:** Create Account, or log in with the seed test user `test@campuscustoms.yale.edu` / `password`. Logged-in chats are saved and reload on your next visit.
- **Easter egg:** turn the footer amp knob to **11**.

## Notes

- Not in the repo (see `.gitignore`): `.env`, `data/` (database and product images), `data.zip`, `.venv/`, `node_modules/`.
- Chat is rate-limited (8 messages/min per visitor). Every chat turn is appended to `output/audit_trail.json`.
- The full design (models, tools, safety rules, loop limits, result caps) is in **`output/harness.md`**.
