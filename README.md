# MedRAG — AI-Powered Document Intelligence

MedRAG is an AI-powered document analysis and question-answering application that combines Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), semantic search, and conversational memory to extract insights from uploaded documents and answer questions using relevant contextual information.

The project explores practical AI engineering concepts, including document processing, vector search, context retrieval, model orchestration, grounded responses, and persistent user sessions.

## Features

- **Document Analysis:** Upload PDF documents or use sample documents to generate structured, AI-powered insights.
- **RAG-Based Chat:** Ask questions about an uploaded document and receive context-aware answers using retrieved document content.
- **Semantic Search:** Generate embeddings and use FAISS for efficient similarity-based retrieval.
- **LLM Orchestration:** Route requests through a configurable multi-model cascade with fallback handling.
- **Conversational Context:** Maintain chat history and support follow-up questions within a document session.
- **User Authentication:** Supabase-powered authentication and session management.
- **Persistent Sessions:** Store chat sessions and related application data using Supabase.
- **Input Validation:** Validate uploaded files, enforce size and page limits, and handle invalid inputs.
- **Usage Controls:** Apply configurable daily analysis limits.
- **Resilient Error Handling:** Handle model failures, timeouts, and unavailable services with controlled fallback behavior.

## Tech Stack

| Category | Technologies |
|---|---|
| Language | Python |
| UI | Streamlit |
| LLMs | Groq API |
| Retrieval-Augmented Generation | RAG, FAISS |
| Embeddings | Hugging Face |
| Authentication and Storage | Supabase |
| Document Processing | PDF processing |
| Testing | Python `unittest` |
| Version Control | Git, GitHub |

## Architecture

```text
                 ┌──────────────────────┐
                 │     Streamlit UI     │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │ Authentication Layer │
                 │  Supabase Sessions   │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │  Document Processing │
                 └──────────┬───────────┘
                            │
                  ┌─────────▼─────────┐
                  │ Analysis Pipeline │
                  │ LLM Model Cascade │
                  └─────────┬─────────┘
                            │
                  ┌─────────▼─────────┐
                  │ Embedding + FAISS │
                  │ Context Retrieval │
                  └─────────┬─────────┘
                            │
                  ┌─────────▼─────────┐
                  │   RAG Chat Agent  │
                  └───────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.11 or a compatible version supported by the project's dependencies
- A Groq API key
- A Supabase project with the required database schema configured

### 1. Clone the repository

```bash
git clone https://github.com/piyushsharma1817/medRAG.git
cd medRAG
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure secrets

Create `.streamlit/secrets.toml` and configure the required credentials:

```toml
GROQ_API_KEY = "your_groq_api_key"
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_anon_or_publishable_key"
```

Use the exact setting names expected by the application. Never commit real API keys, database passwords, or other secrets to GitHub.

### 5. Configure the database

Run the SQL setup script in your Supabase SQL Editor:

```text
public/db/script.sql
```

Ensure that authentication, database permissions, and Row Level Security policies match the application's requirements.

### 6. Launch the application

```bash
python -m streamlit run src/main.py
```

Streamlit will display the local URL in your terminal.

## Testing

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

The tests cover core application behavior, analysis output quality, retrieval grounding, and isolation between document indexes.

## Project Structure

```text
medRAG/
├── public/
│   └── db/
│       ├── schema.png
│       └── script.sql
├── src/
│   ├── agents/
│   │   ├── analysis_agent.py
│   │   ├── chat_agent.py
│   │   └── model_manager.py
│   ├── auth/
│   │   ├── auth_service.py
│   │   └── session_manager.py
│   ├── components/
│   ├── config/
│   ├── services/
│   │   └── ai_service.py
│   └── main.py
├── tests/
├── .streamlit/
│   └── config.toml
├── requirements.txt
└── README.md
```

## Engineering Focus

MedRAG demonstrates practical implementation of:

- Retrieval-Augmented Generation pipelines
- Embedding-based semantic search
- Vector indexing and document-specific retrieval
- LLM fallback and error-handling strategies
- Stateful conversational applications
- Authentication and persistent session management
- Automated testing of retrieval quality and isolation

## Future Improvements

- Retrieval evaluation using precision, recall, and ranking metrics
- Reranking to improve context relevance
- Streaming responses and asynchronous processing
- Response latency and token-usage monitoring
- Improved observability and automated evaluation datasets

---

## Disclaimer

MedRAG is an informational tool, not a substitute for professional medical advice, diagnosis, or treatment. AI-generated interpretations may be inaccurate and should be reviewed by a qualified healthcare professional.

---

**MedRAG** — Exploring practical AI engineering through document intelligence, semantic retrieval, and LLM-powered applications.