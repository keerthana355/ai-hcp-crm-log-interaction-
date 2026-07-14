# AI-First HCP CRM — Log Interaction Module

An AI-driven "Log HCP Interaction" screen for pharmaceutical field reps.
The left panel displays interaction data; the right panel is an AI Assistant
that is the **only** way that data gets written — per the assignment's
explicit rule, there is no manual form entry.

Built with: **React + Redux** (frontend), **FastAPI** (backend),
**LangGraph + Groq LLM** (agent), **MySQL** (database), **JWT** (auth).

---

## 1. What's included

- Full backend: MySQL schema, JWT auth, REST endpoints, and a LangGraph
  agent with **5 tools**:
  1. `log_interaction` — extracts a new interaction from natural language
  2. `edit_interaction` — patches only the fields being corrected (and
     regenerates follow-up suggestions automatically if sentiment changes)
  3. `search_interaction_history` — recalls past interactions with an HCP
  4. `suggest_followups` — generates follow-up actions after logging
  5. `flag_compliance_risk` — flags potential compliance concerns
- Full frontend: split-pane layout matching the provided mockup, with a
  read-only form (left) driven entirely by the AI chat (right). Updated
  fields briefly highlight so it's visually obvious the AI wrote them.
- JWT-based rep login/registration.

Every piece has been tested end-to-end (auth flow, all 5 tools against
a real database, and a full frontend production build).

---

## 2. Prerequisites

- **Python 3.10, 3.11, or 3.12** — avoid 3.13+ for now. Some packages
  (e.g. `pydantic-core`) may not have prebuilt wheels yet for very new
  Python versions, which forces a Rust compile that often fails without
  extra toolchain setup. 3.12 is the safest choice.
- Node.js 18+ and npm
- MySQL Server
- A free Groq API key

---

## 3. Database setup (MySQL)

### Ubuntu / Linux

```bash
sudo apt update
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
```

Log in and create the database + a dedicated app user:

```bash
sudo mysql -u root
```
```sql
CREATE DATABASE hcp_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hcp_app'@'localhost' IDENTIFIED BY 'YourStrongPassword123';
GRANT ALL PRIVILEGES ON hcp_crm.* TO 'hcp_app'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Verify:
```bash
mysql -u hcp_app -p hcp_crm -e "SHOW TABLES;"
```

### Windows

1. Download MySQL Installer from **https://dev.mysql.com/downloads/installer/**
2. Run it → choose **"Developer Default"** setup type → follow the wizard
   (it installs MySQL Server + MySQL Workbench together)
3. During setup, you'll be asked to set a **root password** — remember it
4. Once installed, open **MySQL Workbench** (or **Command Line Client**
   from the Start Menu) and connect using the root password you set
5. Run the same SQL as above to create the database and app user:
   ```sql
   CREATE DATABASE hcp_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'hcp_app'@'localhost' IDENTIFIED BY 'YourStrongPassword123';
   GRANT ALL PRIVILEGES ON hcp_crm.* TO 'hcp_app'@'localhost';
   FLUSH PRIVILEGES;
   ```
6. Verify from **Command Prompt** (MySQL's `bin` folder must be on your
   PATH — the installer usually does this automatically):
   ```cmd
   mysql -u hcp_app -p hcp_crm -e "SHOW TABLES;"
   ```

> **Both platforms:** if your password has special characters like `@`
> or `!`, URL-encode them in the connection string later
> (`@` → `%40`, `!` → `%21`).
>
> If MySQL rejects your password as "too weak," use something with
> upper+lowercase, a number, and a special character —
> e.g. `HcpCrm@2026!Secure`.

---

## 4. Groq API key (mandatory — powers the LangGraph agent)

1. Go to **https://console.groq.com** → sign up free
2. **API Keys** (left sidebar) → **Create API Key** → copy it immediately
3. Paste it into `backend/.env` as `GROQ_API_KEY` (next step)

Models used:
- `openai/gpt-oss-20b` — primary model driving all 5 tools
- `openai/gpt-oss-120b` — available as a fallback for heavier reasoning

> **Note on model choice:** the assignment brief specified `gemma2-9b-it`
> (with `llama-3.3-70b-versatile` as a fallback). Both have since been
> decommissioned by Groq — `gemma2-9b-it` in August 2025, and
> `llama-3.3-70b-versatile` in June 2026 — independent of this project.
> This project uses Groq's current recommended replacements instead.
> Worth mentioning in your video/interview: hosted-LLM model IDs aren't
> permanent, and handling that gracefully is a real production concern.

---

## 5. Backend setup

### Ubuntu / Linux

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# now edit .env:
#   DATABASE_URL=mysql+pymysql://hcp_app:YourStrongPassword123@localhost:3306/hcp_crm
#   GROQ_API_KEY=gsk_your_real_key_here

uvicorn app.main:app --reload
```

### Windows

Open **Command Prompt** or **PowerShell**:

```cmd
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

copy .env.example .env
```

Open `.env` in Notepad (or any text editor) and fill in:
```
DATABASE_URL=mysql+pymysql://hcp_app:YourStrongPassword123@localhost:3306/hcp_crm
GROQ_API_KEY=gsk_your_real_key_here
```

Then run:
```cmd
uvicorn app.main:app --reload
```

> If `py -3.12` isn't recognized, install Python 3.12 from
> **https://www.python.org/downloads/** — during install, check
> **"Add python.exe to PATH."** You can have multiple Python versions
> installed side by side; use `py -3.12` to pick this one specifically.

### Verify (both platforms)

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```
(On Windows without `curl`, just open **http://localhost:8000/health** in a browser instead.)

Interactive API docs: **http://localhost:8000/docs** — useful for testing
endpoints directly and for showing in your video.

Check tables were created:
```bash
mysql -u hcp_app -p hcp_crm -e "SHOW TABLES;"
# users, hcps, interactions
```

---

## 6. Frontend setup (same on both platforms)

In a **new terminal** (keep the backend running):

```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173**.

1. Register a new rep account (Name / Email / Password)
2. Log in
3. You'll see the split-pane screen: form on the left, AI Assistant on the right
4. Type into the chat, e.g.:
   > Today I met with Dr. Smith and discussed Product X efficacy. The sentiment was positive and I shared the brochures.
5. Watch the left form populate automatically — updated fields briefly highlight yellow

---

## 7. Project structure

```
hcp-crm/
├── backend/
│   └── app/
│       ├── core/       # DB connection, JWT/password utilities
│       ├── models/     # SQLAlchemy tables (users, hcps, interactions)
│       ├── schemas/    # Pydantic request/response contracts
│       ├── routers/    # auth, hcps, interactions (read-only), agent (chat)
│       └── agent/      # LangGraph agent + the 5 tools
└── frontend/
    └── src/
        ├── api/         # axios client with JWT auto-attached
        ├── store/       # Redux slices: auth, interaction, chat
        └── components/  # LoginPage, LogInteractionForm, AIAssistantPanel
```

## 8. Database schema (3 tables, kept intentionally simple)

| Table | Purpose |
|---|---|
| `users` | Field rep accounts |
| `hcps` | Healthcare professionals — separate table since one HCP has many interactions (used by `search_interaction_history`) |
| `interactions` | The core record. Every field is written **only** by the AI agent. Materials/samples/follow-ups are JSON columns rather than separate join tables, so every tool only touches one row — simpler to build and explain. |

## 9. How the agent works (for your video/interview explanation)

- The frontend sends each chat message to `POST /api/agent/chat` along with
  a `conversation_id`.
- The backend builds a LangGraph **ReAct agent** (`langgraph.prebuilt.create_react_agent`)
  with a Groq LLM bound to the 5 tools.
- The LLM — not any hand-written regex — reads the rep's message and
  decides which tool to call and what arguments to extract (HCP name,
  sentiment, topics, etc.), based on each tool's docstring.
- Conversation history and "which interaction is currently active" are
  tracked in memory per `conversation_id`, so `edit_interaction` knows
  which row to patch, and `suggest_followups`/`flag_compliance_risk`
  know which row to annotate.
- If a correction changes the sentiment, `edit_interaction` automatically
  regenerates the follow-up suggestions to match the new sentiment —
  so stale advice (e.g. "schedule a follow-up" after sentiment flips to
  negative) never lingers on screen.
- The backend returns the agent's natural-language reply **and** the
  full current interaction object, so the frontend can re-render the
  form and briefly highlight whatever changed.

## 10. Known limitations (worth mentioning honestly in your video)

- Conversation state is in-memory (a Python dict) — restarting the
  backend clears active conversations. A production version would use
  Redis or a DB table instead.
- `flag_compliance_risk` uses a small keyword list as a heuristic, not
  a full compliance rules engine.
- Materials/samples "Search/Add" from the mockup is represented as a
  simple list the AI populates from the chat, not a separate searchable
  catalog UI (out of scope for a 36-hour assessment).

## 11. Manual testing checklist

Once both servers are running, log in and paste these one at a time:

1. `Today I met with Dr. Smith and discussed Product X efficacy. The sentiment was positive and I shared the brochures.` → HCP/Topics/Sentiment/Materials populate
2. `Sorry, the name was actually Dr. John and the sentiment was negative` → only HCP name + sentiment change; Topics stays untouched; follow-ups auto-update to match negative sentiment
3. `What did we discuss with Dr. John before?` → assistant recalls the logged record
4. `Any follow-up suggestions?` → Follow-up Actions section populates
5. `I also gave Dr. John a cash gift and took him to an expensive dinner` → red Compliance Note appears
6. Try clicking directly into any left-panel field → nothing should happen (read-only, AI-only rule)

## 12. Deliverables checklist (from the assignment)

- [ ] Push this code to a GitHub repo, with this README
- [ ] Record a 10–15 min video: frontend walkthrough, live demo of all
  5 tools, code/structure explanation, your own summary of the task
- [ ] Submit both via the Google Form