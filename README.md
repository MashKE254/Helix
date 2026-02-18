# Helix - Generative Teaching Infrastructure

**Helix** is a real-time, adaptive AI engine that transforms any curriculum document, textbook, or skill requirement into personalized, Socratic pedagogy.

## Architecture Overview

### Core Components

1. **RAG Engine**: Vectorized embeddings of official syllabi, past papers, and curriculum standards
2. **Hierarchical Model Router**: Routes queries through different AI models based on complexity
3. **Safety & Verification Layer**: Factual grounding, pedagogical safety, hallucination prevention
4. **Dynamic State Management**: Persistent knowledge graphs for each student

### Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React/TypeScript)
- **Database**: PostgreSQL + Redis
- **Vector DB**: ChromaDB/Pinecone for embeddings
- **AI Models**: Anthropic Claude (Haiku/Sonnet/Opus) + Verified systems
- **Verification**: Wolfram Alpha, RDKit, Judge0

## Project Structure

```
Helix/
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── shared/           # Shared types and utilities
├── docs/             # Documentation
└── docker-compose.yml # Development environment
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Installation

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Running

```bash
# Start all services
docker-compose up

# Or run separately
# Backend: uvicorn backend.main:app --reload
# Frontend: npm run dev
```

## License

Proprietary
