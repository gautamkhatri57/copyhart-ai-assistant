# CopyHart AI Assistant

AI-powered chatbot developed for **CopyHart Services** using **Retrieval-Augmented Generation (RAG)**.

The chatbot understands user intent, maintains conversation context, retrieves relevant information from the CopyHart services knowledge base, and generates answers using Google Gemini.

## Features

* AI-powered chatbot
* Streamlit frontend
* FastAPI backend
* AI-based intent detection
* Conversation-aware follow-up questions
* RAG-based knowledge retrieval
* PDF knowledge base
* Semantic search
* Document reranking
* FAISS vector search
* Google Gemini response generation
* CopyHart services knowledge base
* Context-aware service clarification

## How It Works

```text
User
  ↓
Streamlit Chatbot
  ↓
FastAPI API
  ↓
AI Intent Analysis
  ↓
Service Detection / Clarification
  ↓
RAG Retrieval
  ↓
Document Reranking
  ↓
Google Gemini
  ↓
Answer
```

## Tech Stack

* Python
* Streamlit
* FastAPI
* FAISS
* Sentence Transformers
* Scikit-learn
* PyPDF
* Google Gemini
* NumPy

## Project Structure

```text
CopyHart Project1/
│
├── README.md
├── app.py
├── requirements.txt
│
├── data/
│   └── embeddings.npy
│
├── frontend/
│   └── streamlit_app.py
│
├── knowledge base/
│   └── services.pdf
│
└── rag/
    ├── embeddings.py
    ├── pdf_reader.py
    ├── reranker.py
    ├── retriever.py
    └── vector_store.py
```

## Backend

The FastAPI backend handles:

* User questions
* AI intent analysis
* Service identification
* Conversation context
* RAG retrieval
* Document reranking
* Gemini response generation

Run the backend with:

```bash
uvicorn app:app --reload
```

The backend runs locally at:

```text
http://127.0.0.1:8000
```

## Frontend

The chatbot interface is built using Streamlit.

Run the frontend with:

```bash
streamlit run frontend/streamlit_app.py
```

The Streamlit application will open in the browser.

## Knowledge Base

The chatbot uses:

```text
knowledge base/services.pdf
```

as its primary knowledge source.

The PDF content is processed into chunks, converted into embeddings, stored for semantic retrieval, and reranked before being provided to the AI model.

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Do **not** commit the `.env` file to GitHub.

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Project

### 1. Activate virtual environment

```bash
source .venv/bin/activate
```

### 2. Start FastAPI backend

```bash
uvicorn app:app --reload
```

### 3. Start Streamlit frontend

Open another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

## Current Architecture

The project uses a two-part architecture:

```text
Streamlit Frontend
        │
        │ HTTP POST /chat
        ▼
FastAPI Backend
        │
        ├── AI Intent Analysis
        │
        ├── RAG Retrieval
        │
        ├── Document Reranking
        │
        └── Google Gemini
                │
                ▼
             Answer
```

## Deployment

The Streamlit frontend can be deployed using **Streamlit Community Cloud**.

The FastAPI backend must also be hosted on an accessible server. The Streamlit frontend then connects to the deployed FastAPI backend using the `BACKEND_URL` environment variable.

## Security

* API keys are stored using environment variables.
* `.env` must not be committed to GitHub.
* `.venv` and Python cache files are excluded from version control.

## Project Status

**Current Status:** Development version completed and working locally.

The chatbot supports AI-based service clarification, RAG retrieval, document reranking, and context-aware responses.
