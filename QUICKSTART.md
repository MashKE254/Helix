# Helix Quick Start Guide

Get Helix running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check Node.js version (need 18+)
node --version

# Check if Docker is installed (optional)
docker --version
```

## Option 1: Docker (Recommended)

```bash
# 1. Clone/navigate to project
cd Helix

# 2. Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Edit backend/.env - ADD YOUR API KEYS:
#    ANTHROPIC_API_KEY=your-key-here
#    (Others are optional)

# 4. Start everything
docker-compose up

# 5. Open browser
#    Frontend: http://localhost:3000
#    Backend API: http://localhost:8000
#    API Docs: http://localhost:8000/docs
```

## Option 2: Manual Setup

### Step 1: Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# Start PostgreSQL and Redis (or use Docker)
# Then start backend:
uvicorn backend.main:app --reload
```

### Step 2: Frontend

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start frontend
npm run dev
```

## First Steps

1. **Register an Account**
   - Go to http://localhost:3000/register
   - Choose role: Student, Parent, or Teacher
   - Complete registration

2. **Complete Student Intake** (if student)
   - Log in and go to dashboard
   - Fill out intake form with:
     - Curriculum board (e.g., "IGCSE", "KCSE", "CBSE")
     - Subjects you're studying
     - Learning style preferences

3. **Start Learning!**
   - Ask questions in the tutoring interface
   - Generate practice problems
   - Track your progress

## Adding Curriculum Documents

The system needs curriculum documents to function. Add them via API:

```bash
# Get your auth token first (login via frontend or API)
TOKEN="your-jwt-token"

# Add a curriculum document
curl -X POST http://localhost:8000/api/v1/curriculum/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "board": "IGCSE",
    "subject": "Biology",
    "document_type": "syllabus",
    "title": "IGCSE Biology Syllabus 2023",
    "content": "Full syllabus content here...",
    "metadata": {"year": 2023}
  }'
```

Or use the API docs at http://localhost:8000/docs

## Testing the System

### Test Student Flow

1. Register as student
2. Complete intake
3. Ask a question: "What is photosynthesis?"
4. Generate a practice problem
5. Submit an answer
6. View your knowledge graph state

### Test Parent Flow

1. Register as parent
2. Register children as students
3. Link children to parent account
4. View parent dashboard

### Test Teacher Flow

1. Register as teacher
2. View class briefing (when students are linked)
3. Monitor student progress

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Check Redis is running: `redis-cli ping`
- Check API keys in `.env`

### Frontend won't connect
- Check `NEXT_PUBLIC_API_URL` in frontend/.env
- Check backend is running on port 8000
- Check CORS settings in backend

### No curriculum results
- Add curriculum documents via API
- Check ChromaDB is initialized
- Verify embeddings are being generated

### Database errors
- Run migrations: `alembic upgrade head`
- Check database connection string
- Verify PostgreSQL is accessible

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Read [SETUP.md](./SETUP.md) for detailed setup
- Read [README.md](./README.md) for overview

## Getting Help

- Check API documentation at http://localhost:8000/docs
- Review error logs in terminal
- Check database connection
- Verify all environment variables are set

Happy learning with Helix! 🚀
