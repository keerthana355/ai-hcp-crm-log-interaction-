# AI-First HCP CRM — Log Interaction Module

An AI-driven "Log HCP Interaction" screen for pharmaceutical field reps.
The left panel displays interaction data; the right panel is an AI Assistant
that is the **only** way that data gets written — there is no manual form entry.

Built with: **React + Redux** (frontend), **FastAPI** (backend),
**LangGraph + Groq LLM** (agent), **MySQL** (database), **JWT** (auth).

---

## 1. What's included

- A LangGraph agent with **5 tools**:
  1. `log_interaction` — extracts a new interaction from natural language
  2. `edit_interaction` — patches only the fields being corrected, and
     regenerates follow-up suggestions automatically if sentiment changes
  3. `search_interaction_history` — recalls past interactions with an HCP
  4. `suggest_followups` — generates follow-up actions after logging
  5. `flag_compliance_risk` — flags potential compliance concerns
- A FastAPI backend: MySQL schema, JWT auth, REST endpoints
- A React + Redux frontend: split-pane layout with a read-only form (left)
  driven entirely by an AI chat (right). Fields the AI just updated briefly
  highlight, so it's clear the AI wrote them.

---

## 2. Prerequisites

- **Python 3.10, 3.11, or 3.12** (avoid 3.13+ — some packages like
  `pydantic-core` may lack prebuilt wheels on very new Python versions,
  forcing a Rust compile that often fails)
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

Create the database and a dedicated app user:

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
2. Choose **"Developer Default"** setup type (installs MySQL Server + Workbench)
3. Set a root password during setup — remember it
4. Open **MySQL Workbench** or the **Command Line Client**, connect with root
5. Run the same SQL as above to create the database and app user
6. Verify from Command Prompt (MySQL's `bin` folder needs to be on PATH —
   the installer usually handles this):
   ```cmd
   mysql -u hcp_app -p hcp_crm -e "SHOW TABLES;"
   ```

> If your password has special characters (`@`, `!`, etc.), URL-encode
> them in the connection string later (`@` → `%40`, `!` → `%21`).
> If MySQL rejects a password as too weak, use one with upper+lowercase,
> a number, and a special character — e.g. `HcpCrm@2026!Secure`.

---

## 4. Groq API key

1. Go to **https://console.groq.com** → sign up free
2. **API Keys** → **Create API Key** → copy it immediately
3. Paste it into `backend/.env` as `GROQ_API_KEY`

Models used:
- `openai/gpt-oss-20b` — primary model, drives all 5 tools
- `openai/gpt-oss-120b` — available as a fallback for heavier reasoning

> Groq deprecated `gemma2-9b-it` and `llama-3.3-70b-versatile` in 2025–2026.
> This project uses Groq's current recommended models instead.

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
# edit .env:
#   DATABASE_URL=mysql+pymysql://hcp_app:YourStrongPassword123@localhost:3306/hcp_crm
#   GROQ_API_KEY=gsk_your_real_key_here

uvicorn app.main:app --reload
```

### Windows

```cmd
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

copy .env.example .env
```

Edit `.env` and fill in:
```
DATABASE_URL=mysql+pymysql://hcp_app:YourStrongPassword123@localhost:3306/hcp_crm
GROQ_API_KEY=gsk_your_real_key_here
```

Then run:
```cmd
uvicorn app.main:app --reload
```

> If `py -3.12` isn't recognized, install it from
> **https://www.python.org/downloads/**, checking "Add python.exe to PATH."

### Verify

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```
Interactive API docs: **http://localhost:8000/docs**

Check tables were created:
```bash
mysql -u hcp_app -p hcp_crm -e "SHOW TABLES;"
# users, hcps, interactions
```

---

## 6. Frontend setup

In a new terminal (keep the backend running):

```bashVisit **http://localhost:5173**, register a rep account, log in, and you'll
see the split-pane screen — form on the left, AI Assistant on the right.

---

## 7. Test login

No seed accounts exist — register one via the app itself:

- Name: `Demo Rep`
- Email: `demo@hcp-crm.com`
- Password: `DemoPass@123`

Use these same credentials to log back in on future runs.

---
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173**, register a rep account, log in, and you'll
see the split-pane screen — form on the left, AI Assistant on the right.

---


## 7. Test login

No seed accounts exist — register one via the app itself:

- Name: `Demo Rep`
- Email: `demo@hcp-crm.com`
- Password: `DemoPass@123`

Use these same credentials to log back in on future runs.

---

## 8. Project structure

```
hcp-crm/
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py
│       ├── core/          # DB connection, JWT/password utilities
│       ├── models/        # SQLAlchemy tables (users, hcps, interactions)
│       ├── schemas/       # Pydantic request/response contracts
│       ├── routers/       # auth, hcps, interactions, agent (chat)
│       └── agent/         # LangGraph agent + the 5 tools
└── frontend/
    ├── package.json
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api/            # axios client with JWT auto-attached
        ├── store/          # Redux slices: auth, interaction, chat
        └── components/     # LoginPage, LogInteractionForm, AIAssistantPanel
```

---

## 9. Database schema

| Table | Purpose |
|---|---|
| `users` | Field rep accounts |
| `hcps` | Healthcare professionals — one HCP has many interactions (used by `search_interaction_history`) |
| `interactions` | The core record, written only by the AI agent. Materials/samples/follow-ups are JSON columns rather than separate tables, so every tool only touches one row |

---

## 10. How the agent works

- The frontend sends each chat message to `POST /api/agent/chat` with a `conversation_id`.
- The backend builds a LangGraph ReAct agent (`langgraph.prebuilt.create_react_agent`) with a Groq LLM bound to the 5 tools.
- The LLM reads the message and decides which tool to call and what arguments to extract (HCP name, sentiment, topics, etc.) based on each tool's docstring — there is no manual parsing.
- Conversation history and the "currently active" interaction are tracked in memory per `conversation_id`, so `edit_interaction` knows which row to patch, and `suggest_followups` / `flag_compliance_risk` know which row to annotate.
- If a correction changes the sentiment, `edit_interaction` regenerates follow-up suggestions to match — stale advice never lingers.
- The backend returns the agent's reply plus the full current interaction object, so the frontend can re-render the form and highlight what changed.

---

## 11. Testing

With both servers running, log in and try:

1. `Today I met with Dr. Smith and discussed Product X efficacy. The sentiment was positive and I shared the brochures.` → HCP, Topics, Sentiment, and Materials populate.
2. `Sorry, the name was actually Dr. John and the sentiment was negative` → only HCP name and sentiment change; Topics stays untouched; follow-ups update to match.
3. `What did we discuss with Dr. John before?` → assistant recalls the logged interaction.
4. `Any follow-up suggestions?` → Follow-up Actions populate.
5. `I also gave Dr. John a cash gift and took him to an expensive dinner` → a compliance note appears.
6. Clicking directly into any left-panel field does nothing — it's read-only, driven only by the AI.