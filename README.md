# Multi-Agent Accounting System

Sistem multi-agent pentru procesare automată de documente contabile — clasificare, propunere de contare și validare, construit ca proiect de disertație și MVP pentru un produs real.

## De ce acest proiect

Cabinetele de contabilitate mici/mijlocii din România pierd timp semnificativ pe introducerea manuală a documentelor și pe verificarea erorilor de contare. Acest sistem automatizează procesarea documentelor (facturi, bonuri fiscale, extrase bancare) printr-un pipeline de agenți specializați, cu verificare încrucișată automată — nu doar generare de contări, ci și detectarea erorilor înainte ca acestea să ajungă la contabil.

## Arhitectură

Sistemul folosește un **orchestrator** care coordonează agenți specializați, fiecare cu o responsabilitate clară:

```
Document (PDF/imagine)
        |
        v
+--------------------+
|  Agent 1:          |  Extrage si clasifica documentul
|  Classifier         |  (tip document, furnizor, sume, TVA)
+---------+----------+
          |
          v
   Document tranzactional?
     |              |
     v da            v nu
+--------------------+   status: classified_only
|  Agent 2:          |   (rapoarte, bilanturi etc.)
|  Accounting        |
|  Proposer          |<-------+
+---------+----------+        |
          |                    | feedback (retry)
          v                    |
+--------------------+         |
|  Agent 3:          |---------+
|  Validator          |  daca gaseste erori,
+---------+----------+  reincearca (max 2x)
          |
          v
   status: validated / needs_review
```

### Agenți

| Agent                   | Rol                                                                                             | Input                    | Output                                 |
| ----------------------- | ----------------------------------------------------------------------------------------------- | ------------------------ | -------------------------------------- |
| **Document Classifier** | Extrage date structurate din document (PDF/imagine, cu vision)                                  | Fișierul documentului    | Tip document, furnizor, CUI, sumă, TVA |
| **Accounting Proposer** | Propune înregistrarea contabilă (linii debit/credit)                                            | Date extrase + CUI firmă | Linii contabile propuse                |
| **Validator**           | Verifică balanța, coerența conturilor, plauzibilitatea TVA — fără LLM, doar reguli deterministe | Propunerea de contare    | Flag-uri de eroare, status             |

Orchestratorul rulează o **buclă de corecție**: dacă `Validator` găsește probleme, propunerea e retrimisă la `Accounting Proposer` cu feedback explicit despre ce trebuie corectat, până la 2 reîncercări.

## Stack tehnic

- **Backend**: Python, FastAPI
- **Bază de date**: PostgreSQL, SQLAlchemy (ORM), Alembic (migrații)
- **AI**: OpenAI API (`gpt-4o` / `gpt-4o-mini`) cu Structured Outputs (JSON Schema)
- **Infrastructură**: Docker Compose (PostgreSQL local)

## Structura proiectului

```
backend/
├── app/
│   ├── main.py                  # entry point FastAPI
│   ├── config.py                # configurare (variabile de mediu)
│   ├── orchestrator/            # orchestrare: state + graf de decizie
│   ├── agents/                  # agenti: classifier, proposer, validator
│   ├── ml/                      # modele ML (detectare anomalii - in lucru)
│   ├── llm/                     # client OpenAI, prompturi
│   ├── models/                  # modele SQLAlchemy (DB)
│   ├── schemas/                 # scheme Pydantic (request/response)
│   ├── api/                     # endpoint-uri FastAPI
│   └── db/                      # sesiune DB, migratii Alembic
├── requirements.txt
└── .env.example
```

## Setup local

### Cerințe

- Python 3.11+
- Docker Desktop

### Pași

**1. Clonează repo-ul și intră în `backend/`**

```bash
git clone <repo-url>
cd backend
```

**2. Creează mediul virtual și instalează dependențele**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

**3. Configurează variabilele de mediu**

Copiază `.env.example` în `.env` și completează valorile reale:

```bash
cp .env.example .env
```

Ai nevoie de o cheie API OpenAI (`OPENAI_API_KEY`).

**4. Pornește baza de date**

```bash
docker compose up -d
```

**5. Rulează migrațiile**

```bash
alembic upgrade head
```

**6. Pornește serverul**

```bash
uvicorn app.main:app --reload
```

API-ul e disponibil la `http://localhost:8000`, documentația interactivă la `http://localhost:8000/docs`.

## Endpoint-uri principale

| Metodă | Endpoint                           | Descriere                                                      |
| ------ | ---------------------------------- | -------------------------------------------------------------- |
| `GET`  | `/health`                          | Verificare status server                                       |
| `POST` | `/documents/upload`                | Încarcă un document (PDF/imagine)                              |
| `GET`  | `/documents/`                      | Listează documentele                                           |
| `POST` | `/documents/{id}/classify`         | Rulează pipeline-ul complet (clasificare → contare → validare) |
| `GET`  | `/review/pending`                  | Listează documentele care necesită verificare manuală          |
| `POST` | `/review/{transaction_id}/approve` | Aprobă o contare propusă                                       |
| `POST` | `/review/{transaction_id}/reject`  | Respinge o contare propusă                                     |

## Status curent / roadmap

- [x] Extragere și clasificare documente (PDF + imagini)
- [x] Propunere de contare cu direcție corectă (venit/cheltuială)
- [x] Validare automată (balanță, coerență conturi, TVA plauzibil)
- [x] Buclă de corecție între validator și proposer
- [x] Coadă de aprobare (backend)
- [ ] Frontend (React) peste coada de aprobare
- [ ] Agent de detectare anomalii (ML, scikit-learn)
- [ ] Validare CUI prin API ANAF
- [ ] Agent conversațional (chat peste datele procesate)

## Context academic

Acest proiect e dezvoltat ca parte a unei disertații despre sisteme multi-agent aplicate în contabilitate, cu accent pe:

- Orchestrare cu dependențe condiționate (nu toți agenții rulează pentru orice document)
- Verificare încrucișată automată între agenți, ca alternativă la validarea manuală completă
- Bucle de feedback/corecție între agenți, nu doar pipeline liniar
