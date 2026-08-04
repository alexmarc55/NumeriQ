# Multi-Agent Accounting System

A multi-agent system for automated accounting document processing — classification, accounting entry proposal, and validation, developed as both a dissertation project and an MVP for a real-world product.

## Why This Project

Small and medium-sized accounting firms in Romania spend significant time on manually entering documents and checking accounting entry errors. This system automates the processing of accounting documents (invoices, receipts, bank statements) through a pipeline of specialized agents with automated cross-validation — not just generating accounting entries, but also detecting errors before they reach the accountant.

## Architecture

The system uses an **orchestrator** that coordinates specialized agents, each with a clearly defined responsibility:

```
Document (PDF/image)
        |
        v
+--------------------+
|  Agent 1:          |  Extracts and classifies the document
|  Classifier         |  (document type, supplier, amounts, VAT)
+---------+----------+
          |
          v
   Transactional document?
     |              |
     v yes          v no
+--------------------+   status: classified_only
|  Agent 2:          |   (reports, balance sheets, etc.)
|  Accounting        |
|  Proposer          |<-------+
+---------+----------+        |
          |                    | feedback (retry)
          v                    |
+--------------------+         |
|  Agent 3:          |---------+
|  Validator          |  if errors are found,
+---------+----------+  retry (max 2 times)
          |
          v
   status: validated / needs_review
```

## Agents

| Agent                   | Role                                                                                                                 | Input                       | Output                                           |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------- | ------------------------------------------------ |
| **Document Classifier** | Extracts structured data from documents (PDF/images, using vision capabilities)                                      | Document file               | Document type, supplier, company ID, amount, VAT |
| **Accounting Proposer** | Proposes accounting entries (debit/credit lines)                                                                     | Extracted data + company ID | Proposed accounting lines                        |
| **Validator**           | Checks balance correctness, account consistency, and VAT plausibility — using deterministic rules only, without LLMs | Proposed accounting entry   | Error flags, validation status                   |

The orchestrator runs a **correction loop**: if the `Validator` detects issues, the proposal is sent back to the `Accounting Proposer` together with explicit feedback about what needs to be corrected, for up to 2 retry attempts.

## Technical Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL, SQLAlchemy (ORM), Alembic (migrations)
- **AI**: OpenAI API (`gpt-4o` / `gpt-4o-mini`) with Structured Outputs (JSON Schema)
- **Infrastructure**: Docker Compose (local PostgreSQL)

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # configuration (environment variables)
│   ├── orchestrator/            # orchestration: state + decision graph
│   ├── agents/                  # agents: classifier, proposer, validator
│   ├── ml/                      # ML models (anomaly detection - in progress)
│   ├── llm/                     # OpenAI client, prompts
│   ├── models/                  # SQLAlchemy database models
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── api/                     # FastAPI endpoints
│   └── db/                      # database session, Alembic migrations
├── requirements.txt
└── .env.example
```

## Local Setup

### Requirements

- Python 3.11+
- Docker Desktop

### Steps

**1. Clone the repository and navigate to `backend/`**

```bash
git clone <repo-url>
cd backend
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

**3. Configure environment variables**

Copy `.env.example` to `.env` and fill in the actual values:

```bash
cp .env.example .env
```

An OpenAI API key (`OPENAI_API_KEY`) is required.

**4. Start the database**

```bash
docker compose up -d
```

**5. Run database migrations**

```bash
alembic upgrade head
```

**6. Start the server**

```bash
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`.

## Main Endpoints

| Method | Endpoint                           | Description                                                           |
| ------ | ---------------------------------- | --------------------------------------------------------------------- |
| `GET`  | `/health`                          | Server health check                                                   |
| `POST` | `/documents/upload`                | Uploads a document (PDF/image)                                        |
| `GET`  | `/documents/`                      | Lists documents                                                       |
| `POST` | `/documents/{id}/classify`         | Runs the complete pipeline (classification → accounting → validation) |
| `GET`  | `/review/pending`                  | Lists documents requiring manual review                               |
| `POST` | `/review/{transaction_id}/approve` | Approves a proposed accounting entry                                  |
| `POST` | `/review/{transaction_id}/reject`  | Rejects a proposed accounting entry                                   |

## Current Status / Roadmap

- [x] Document extraction and classification (PDF + images)
- [x] Accounting entry proposal with correct direction (revenue/expense)
- [x] Automated validation (balance, account consistency, plausible VAT)
- [x] Correction loop between validator and proposer
- [x] Approval queue (backend)
- [ ] Frontend (React) on top of the approval queue
- [ ] ML anomaly detection agent (scikit-learn)
- [ ] Company ID validation through ANAF API
- [ ] Conversational agent (chat interface over processed data)

## Academic Context

This project is developed as part of a dissertation focused on multi-agent systems applied to accounting, with emphasis on:

- Conditional dependency-based orchestration (not all agents run for every document)
- Automated cross-validation between agents as an alternative to fully manual verification
- Feedback and correction loops between agents, rather than a simple linear pipeline
