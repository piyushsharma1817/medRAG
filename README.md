# MedRAG — Medical Intelligence & Retrieval Agent

MedRAG is a medical-report analysis and retrieval-augmented question-answering application designed to help users explore information in blood test reports. It combines LLM-powered analysis with document retrieval so users can ask follow-up questions grounded in their uploaded report.

The application is built with Streamlit, Python, LangChain, FAISS, Hugging Face embeddings, Groq, and Supabase.

> **Important:** MedRAG is an informational tool, not a substitute for professional medical advice, diagnosis, or treatment. AI-generated interpretations may be inaccurate and should be reviewed with a qualified healthcare professional.

## Features

### Medical report analysis
- Upload a PDF blood report or use the built-in sample report.
- Extract report text and validate uploaded files.
- Generate AI-assisted report analysis using Groq-hosted language models.
- Use a multi-model fallback mechanism for supported model failures.

### Retrieval-Augmented Generation (RAG)
- Create vector representations of report text using Hugging Face embeddings.
- Index document chunks with FAISS for semantic retrieval.
- Use retrieved report context to answer follow-up questions.
- Maintain conversational context for report-related questions.

### Authentication and session management
- Sign up and sign in using Supabase Auth.
- Store analysis sessions and chat history in Supabase.
- Revisit or delete previous sessions.
- Configure upload restrictions, daily analysis limits, and session timeouts.

### User interface
- Streamlit-based interface with a sidebar for session navigation.
- PDF upload and sample-report workflows.
- Report analysis and follow-up chat in one application.

## Tech Stack

| Component | Technology |
|---|---|
| Application UI | Streamlit |
| Language | Python |
| LLM inference | Groq API |
| RAG framework | LangChain |
| Embeddings | Hugging Face, `all-MiniLM-L6-v2` |
| Vector store | FAISS CPU |
| Authentication | Supabase Auth |
| Database | Supabase / PostgreSQL |
| PDF extraction | PDFPlumber |
| File validation | `filetype` |

## Architecture

1. **Document ingestion:** Accept a PDF report, validate the file, and extract its text.
2. **Analysis:** Pass report information to the analysis workflow to generate an interpretation.
3. **Indexing and retrieval:** Split report text into chunks, embed the chunks, and retrieve relevant context for a user query.
4. **Answer generation:** Provide the retrieved context to the language model to generate a follow-up response.
5. **Persistence:** Use Supabase to manage authentication, sessions, and stored conversation history.

## Getting Started

### Prerequisites

- Python 3.12 (the version used during local setup)
- A Supabase project
- A Groq API key

### 1. Clone the repository

```bash
git clone <YOUR_MEDRAG_REPOSITORY_URL>
cd medRAG
```

Replace the placeholder with the URL of your own repository.

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure AI provider (required for analysis and chat)

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-groq-api-key"
```

Guests can open the app and use sample/report workflows without Supabase credentials. A Groq API key is required to generate analysis and chat answers. Report text and prompts are sent to Groq. Hugging Face may download the embedding model at first use. Never commit this file or expose API keys in source code, screenshots, or public logs.

### Optional: saved accounts

To enable login, signup, and saved history, add `SUPABASE_URL` and `SUPABASE_KEY` to `.streamlit/secrets.toml`, then configure and review the policies in your own Supabase project. The supplied SQL schema does not enable or define row-level security policies. Do not deploy persistent history until suitable RLS policies are configured and verified. The application must use a publishable/anon key, never a service-role key.

### 5. Set up the database (optional)

Review `public/db/script.sql` and execute the schema manually in your own Supabase project's SQL Editor. Do not run it automatically from the application. Review and add safe RLS policies before enabling persistent user data.

With Supabase configured, the application uses it for authentication and persistent session and message data. Guest report content and chat are not written to Supabase.

### 6. Run MedRAG

```powershell
python -m streamlit run src/main.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Project Structure

```text
medRAG/
├── .streamlit/
│   └── config.toml
├── public/
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
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Development Roadmap

Planned improvements will be documented here as they are implemented and tested.

- [ ] Evaluate retrieval quality and answer faithfulness using a repeatable evaluation dataset.
- [ ] Add reranking to improve the relevance of retrieved report passages.
- [ ] Provide source-grounded answers with report-page references.
- [ ] Compare retrieval strategies and document their performance.
- [ ] Add tests for retrieval, answer grounding, and failure handling.

## Security and Privacy

- Keep API keys and database credentials in local secrets or deployment secret settings.
- Do not commit `.streamlit/secrets.toml`, environment files, or patient reports.
- Use synthetic or appropriately de-identified medical reports during development and testing.
- Review database access policies before deploying the application.
- Do not treat model-generated health information as a clinical diagnosis.

## Attribution and License

MedRAG is a personal adaptation and extension of [HIA (Health Insights Agent)](https://github.com/harshhh28/hia), originally created by Harsh Gajjar.

The original MIT license and copyright notice are retained in the `LICENSE` file. Original portions of the code remain subject to the applicable license terms. New features and modifications will be documented as they are developed.

## Project Status

Guest session data is held in Streamlit session state and disappears when that session ends; this is not a guarantee of secure deletion. In-memory guest usage limits are not abuse prevention controls. Scanned PDFs are not OCR processed. Do not upload reports unless you are comfortable sending their text to the configured AI provider.
