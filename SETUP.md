# Helix Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose (optional)

## Quick Start with Docker

```bash
# Clone and navigate to project
cd Helix

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env and add your API keys:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY (optional, for embeddings)
# - WOLFRAM_APP_ID (optional)
# - JUDGE0_API_KEY (optional)

# Start all services
docker-compose up -d

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000
```

## Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env and add your API keys

# Set up database
# Make sure PostgreSQL is running
createdb helix  # Or create via pgAdmin

# Run migrations (if using Alembic)
# alembic upgrade head

# Start server
uvicorn backend.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

## Initial Configuration

### 1. Add Curriculum Documents

The system needs curriculum documents to function. You can add them via the API:

```bash
curl -X POST http://localhost:8000/api/v1/curriculum/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "board": "IGCSE",
    "subject": "Biology",
    "document_type": "syllabus",
    "title": "IGCSE Biology Syllabus 2023",
    "content": "...",
    "metadata": {"year": 2023, "chapter": 1}
  }'
```

### 2. Create Your First User

1. Register at http://localhost:3000/register
2. Complete student intake (if student)
3. Start learning!

## API Keys Required

- **Anthropic API Key**: Required for AI model routing (Claude Haiku/Sonnet/Opus)
- **OpenAI API Key**: Optional, for better embeddings (defaults to sentence-transformers)
- **Wolfram App ID**: Optional, for mathematical verification
- **Judge0 API Key**: Optional, for code execution verification

## Architecture Overview

### Backend Structure

```
backend/
├── api/              # API endpoints
│   ├── auth.py       # Authentication
│   ├── students.py   # Student endpoints
│   ├── parents.py    # Parent dashboard
│   ├── teachers.py   # Teacher dashboard
│   ├── curriculum.py # Curriculum management
│   ├── tutoring.py   # Socratic tutoring
│   └── practice.py   # Practice problems
├── core/             # Core configuration
│   ├── config.py     # Settings
│   ├── database.py   # Database setup
│   └── redis_client.py
├── models/           # Database models
│   ├── user.py       # User models
│   └── learning.py   # Learning models
└── services/         # Business logic
    ├── rag_engine.py      # RAG for curriculum
    ├── model_router.py    # AI model routing
    ├── knowledge_graph.py # Knowledge graphs
    └── verification.py    # Verification layer
```

### Frontend Structure

```
frontend/
├── app/              # Next.js app directory
│   ├── page.tsx      # Landing page
│   ├── login/        # Login page
│   ├── register/     # Registration
│   └── dashboard/    # User dashboard
└── lib/
    └── api.ts        # API client
```

## Key Features

1. **RAG Engine**: Retrieves curriculum documents using vector embeddings
2. **Model Router**: Routes queries to appropriate AI models (Haiku/Sonnet/Opus)
3. **Knowledge Graph**: Tracks student mastery and misconceptions
4. **Verification Layer**: Validates math, chemistry, and code
5. **Socratic Teaching**: Guides learning through questions

## Development

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Production Deployment

1. Set `DEBUG=False` in backend/.env
2. Use strong `SECRET_KEY`
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use production database
6. Configure Redis persistence
7. Set up monitoring and logging

## Support

For issues or questions, please refer to the main README.md
