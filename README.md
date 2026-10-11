# MedRAG — Medical Intelligence & Retrieval Agent

MedRAG is a medical report analysis and retrieval-augmented question-answering application designed to help users explore information in blood test reports. It combines LLM-powered analysis with document retrieval so users can ask follow-up questions grounded in their uploaded reports.

Built with Streamlit, Python, LangChain, FAISS, Hugging Face embeddings, Groq, and Supabase.

> **Disclaimer:** MedRAG is an informational tool, not a substitute for professional medical advice, diagnosis, or treatment. AI-generated interpretations may be inaccurate and should be reviewed by a qualified healthcare professional.

## Features

### Medical Report Analysis
- Upload a PDF blood report or use the built-in sample report.
- Extract report text and validate uploaded files.
- Generate AI-assisted report analysis using Groq-hosted language models.
- Use a multi-model fallback mechanism for supported model failures.

### Retrieval-Augmented Generation (RAG)
- Generate vector embeddings from report text using Hugging Face.
- Index document chunks with FAISS for semantic retrieval.
- Use retrieved report context to answer follow-up questions.
- Maintain conversational context for report-related questions.

### Authentication & Session Management
- Sign up and sign in using Supabase Auth.
- Store analysis sessions and chat history in Supabase.
- Revisit or delete previous sessions.
- Configure upload restrictions, daily analysis limits, and session timeouts.

### User Interface
- Streamlit-based interface with sidebar session navigation.
- PDF upload and sample-report workflows.
- Report analysis and follow-up chat in one application.

## Tech Stack

| Component | Technology |
|---|---|
| Application UI | Streamlit |
| Programming Language | Python |
| LLM Inference | Groq API |
| RAG Framework | LangChain |
| Embedding Model | Hugging Face — `all-MiniLM-L6-v2` |
| Vector Store | FAISS CPU |
| Authentication | Supabase Auth |
| Database | Supabase / PostgreSQL |
| PDF Extraction | PDFPlumber |
| File Validation | `filetype` |

## Architecture

1. **Document ingestion:** Validate an uploaded PDF and extract its text.
2. **Analysis:** Process report information through the analysis workflow to generate an AI-assisted interpretation.
3. **Indexing and retrieval:** Split report text into chunks, generate embeddings, and retrieve relevant context for each query.
4. **Answer generation:** Provide retrieved context to the language model to generate report-related responses.
5. **Persistence:** Use Supabase for authentication, sessions, and stored conversation history when configured.

## Getting Started

### Prerequisites

- Python 3.12
- A Groq API key for analysis and chat
- A Supabase project for optional authentication and persistent history

### 1. Clone the Repository

```bash
git clone https://github.com/piyushsharma1817/medRAG.git
cd medRAG
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure Groq

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-groq-api-key"
```

A Groq API key is required to generate analysis and chat responses. Report text and prompts are sent to Groq. Hugging Face may download the embedding model during first use.

Never commit this file or expose API keys in source code, screenshots, or public logs.

### 5. Optional: Configure Supabase

To enable authentication and saved history, add the following to `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-publishable-or-anon-key"
```

Use only an appropriate publishable/anon key, never a service-role key in the client-facing application.

Review `public/db/script.sql` and execute the schema manually in your Supabase project's SQL Editor if needed. The supplied SQL schema does not establish row-level security policies. Configure and verify suitable RLS policies before enabling persistent user data. Do not execute schema changes automatically from the application.

Guest report content and chat are not written to Supabase, according to the current application design.

### 6. Run the Application

```powershell
python -m streamlit run src/main.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Project Structure

```text
medRAG/
├── .devcontainer/
├── .streamlit/
│   └── config.toml
├── public/
│   ├── HIA_demo.gif
│   └── db/
│       ├── script.sql
│       └── schema.png
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
│   ├── utils/
│   └── main.py
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

## Testing

Run the test suite:

```powershell
python -m unittest discover -s tests -v
```

The current test suite covers analysis prompt constraints, model fallback behavior, retrieval grounding, report-index isolation, and related failure cases.

## Development Roadmap

- [ ] Evaluate retrieval quality and answer faithfulness using a repeatable evaluation dataset.
- [ ] Add reranking to improve the relevance of retrieved report passages.
- [ ] Provide source-grounded answers with report-page references.
- [ ] Compare retrieval strategies and document their performance.
- [ ] Expand tests for retrieval, answer grounding, and failure handling.

## Security & Privacy

- Keep API keys and database credentials in local secrets or deployment secret settings.
- Never commit `.streamlit/secrets.toml`, environment files, or patient reports.
- Use synthetic or appropriately de-identified medical reports during development and testing.
- Review database access policies before deploying the application.
- Do not treat model-generated health information as a clinical diagnosis.
- Avoid uploading reports containing sensitive information unless you understand how their text is processed by the configured AI provider.

## Attribution

MedRAG is a personal adaptation and extension of [HIA (Health Insights Agent)](https://github.com/harshhh28/hia).

The project builds upon the original work and incorporates additional functionality and modifications. Original portions remain subject to their applicable license terms. A suitable license and any required original copyright notices should be retained in the repository.

## Project Status & Limitations

- Guest session data is held in Streamlit session state and disappears when that session ends; this does not guarantee secure deletion.
- In-memory guest usage limits are not robust abuse-prevention controls.
- Scanned PDFs are not OCR-processed.
- Uploaded report text and prompts may be sent to the configured AI provider.
- AI-generated results can be incomplete or inaccurate and should not be used as a standalone basis for medical decisions.
