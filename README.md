# AI-Powered SQL Agent

An enterprise-ready AI Agent that translates natural language business questions into safe, validated SQLite queries, executes them against a relational database, and returns conversational, human-readable answers alongside interactive result tables.

---

## 🌟 Key Features

1. **Natural Language to SQL**: Converts complex business queries into accurate SQLite syntax.
2. **Multi-Model LLM Support**: Native support for **Google Gemini** (`gemini-3.5-flash-lite`, `gemini-3.8-flash`) and **OpenAI** (`gpt-4o-mini`), with an intelligent offline fallback engine.
3. **Multi-Layer Security & Guardrails**:
   - **AST Parsing with `sqlglot`**: Enforces pure `SELECT` queries only.
   - **Forbidden Verbs Blocklist**: Rejects `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `TRUNCATE`, `PRAGMA`.
   - **Statement Chaining Prevention**: Blocks stacked queries and semicolon injection attacks.
   - **Read-Only SQLite Engine**: Connects via `file:database.db?mode=ro`, preventing database writes at the OS/engine level.
4. **Conversational Memory**: Context-aware follow-up reasoning (e.g. asking *"What are the top 10 customers?"* followed by *"Only those from Egypt"*).
5. **Interactive UI**: Clean Streamlit dashboard with 1-click test buttons for assignment questions, SQL code inspection, and tabular data visualization.
6. **FastAPI Backend**: Fully decoupled REST API for headless execution or external integrations.

---

## 📂 Project Architecture

```
ai_sql_agent/
│
├── app/
│   ├── main.py             # FastAPI REST endpoints
│   ├── agent.py            # Orchestrator pipeline
│   ├── database.py         # Read-only SQLite connection & schema inspector
│   ├── sql_generator.py    # LLM prompt engineering & query generation
│   ├── sql_validator.py    # Security validation & AST enforcement
│   └── conversation.py     # Multi-turn session memory
│
├── data/
│   ├── database.db         # SQLite database
│   └── seed_data.py        # Schema and synthetic data generator
│
├── frontend/
│   └── streamlit_app.py    # Interactive Streamlit dashboard
│
├── tests/
│   ├── test_queries.py     # SQLite benchmark queries
│   └── test_agent.py       # Full end-to-end automated test suite
│
├── .env                    # Environment variables (API keys)
├── .env.example            # Environment template
└── requirements.txt        # Python dependencies
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### 2. Setup Environment & Install Dependencies

```bash
# Clone or navigate to the directory
cd C:\Users\Ali\.gemini\antigravity\scratch\ai_sql_agent

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### 3. Initialize & Seed Database

```bash
python data/seed_data.py
```

### 4. Run Automated Tests

Run the full end-to-end test suite to verify all assignment questions, conversational memory, and security blocks:

```bash
python tests/test_agent.py
```

### 5. Launch the Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```

### 6. (Optional) Run FastAPI Backend Service

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be accessible at: `http://127.0.0.1:8000/docs`

---

## 🧪 Assignment Benchmark Questions

The database and agent have been verified against all 5 core assignment scenarios:

| # | Question | Verification Target | Status |
|---|----------|---------------------|--------|
| 1 | *What are the top 10 customers by revenue?* | Aggregates completed order totals per customer descending | ✅ Verified |
| 2 | *What was the revenue last month?* | Filters completed orders in the last 30 days | ✅ Verified |
| 3 | *Which country has the highest average order value?* | Calculates `AVG(total_amount)` grouped by country | ✅ Verified |
| 4 | *List customers without orders in the last 90 days* | Identifies inactive customers using `HAVING MAX(order_date) < date('now', '-90 days')` | ✅ Verified |
| 5 | *What is the percentage of cancelled orders?* | Computes cancellation ratio `(cancelled / total) * 100` | ✅ Verified |

### Edge Case Tests
1. **Conversational Follow-up**: Refines previous query (e.g. adding `AND country = 'Egypt'`).
2. **Malicious Injection Attack**: `DROP TABLE customers;` is rejected with security alert.
3. **Out-of-Scope Query**: Vague questions (e.g., weather inquiries) are caught and explained gracefully.

---

## 💡 Discussion & Demo Session Preparation (Bonus Topics)

For the post-assignment interview / demo session:

### 1. What is Climate Technology?
Climate Technology encompasses solutions aimed at mitigating greenhouse gas emissions (mitigation) or adapting to climate change effects (adaptation). Examples include clean energy IoT sensors, renewable grid optimization, carbon accounting, and precision agriculture.

### 2. What is Geospatial Data & GIS?
- **Geospatial Data**: Information that identifies the geographic location and characteristics of natural or constructed features on Earth (coordinates, satellite imagery, LiDAR scans).
- **GIS (Geographic Information System)**: A computer system for capturing, storing, checking, and displaying data related to positions on Earth’s surface.

### 3. How can AI and SQL Help Analyze Environmental Data?
- **Spatial SQL (e.g., PostGIS, SpatiaLite)**: Enables spatial joins (e.g. finding orders, weather alerts, or emissions within specific geographic polygons or radius).
- **AI Agents for Natural Language Analysis**: Allows non-technical policy makers or climate researchers to query complex spatio-temporal datasets using conversational questions (e.g. *"Which agricultural zones experienced soil moisture drop greater than 20% in the last quarter?"*).
