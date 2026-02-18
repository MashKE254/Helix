# Helix Architecture

## System Overview

Helix is a **Generative Teaching Infrastructure** that transforms curriculum documents into personalized, Socratic pedagogy. The system is built on a microservices architecture with a FastAPI backend and Next.js frontend.

## Core Components

### 1. RAG Engine (`backend/services/rag_engine.py`)

**Purpose**: Retrieves relevant curriculum documents using vector embeddings.

**Technology**:
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- Semantic search over curriculum documents

**Key Methods**:
- `retrieve_curriculum_context()`: Main retrieval function
- `retrieve_marking_scheme()`: Gets marking schemes for specific questions
- `retrieve_learning_objectives()`: Fetches learning objectives for chapters

**Data Flow**:
1. Student query → Embedding generation
2. Vector similarity search in ChromaDB
3. Filter by curriculum board, subject, topic
4. Return top-k relevant documents with metadata

### 2. Hierarchical Model Router (`backend/services/model_router.py`)

**Purpose**: Routes queries to appropriate AI models based on cognitive complexity.

**Model Selection**:
- **Haiku** (Fast): Simple queries, intent classification, dashboard updates
- **Sonnet** (Balanced): Standard explanations, practice problems, essay feedback
- **Opus** (Deep): Complex Socratic dialogue, debugging, exam prep
- **Verified** (Deterministic): Math proofs, chemical equations, code execution

**Routing Logic**:
```python
complexity < 0.3 → Haiku
complexity < 0.7 → Sonnet
complexity >= 0.7 → Opus
requires_verification → Verified
```

**Pedagogical Constraints**:
- Never gives direct answers
- Uses Socratic questioning
- Cites curriculum sources
- Detects misconceptions

### 3. Knowledge Graph System (`backend/services/knowledge_graph.py`)

**Purpose**: Maintains persistent knowledge graphs for each student.

**Structure**:
```json
{
  "concepts": {
    "photosynthesis": {
      "mastery": 0.75,
      "subject": "Biology",
      "attempts": 12,
      "last_updated": "2024-01-15T10:30:00Z"
    }
  },
  "misconceptions": [
    {
      "concept": "photosynthesis",
      "type": "confuses_reactants",
      "count": 3,
      "evidence": ["..."]
    }
  ],
  "prerequisite_gaps": [
    {
      "target_concept": "cellular_respiration",
      "missing_prerequisites": ["ATP", "mitochondria"]
    }
  ]
}
```

**Key Operations**:
- `update_concept_mastery()`: Updates mastery levels
- `detect_misconception()`: Records misconceptions
- `identify_prerequisite_gaps()`: Finds missing prerequisites
- `get_next_learning_path()`: Generates learning recommendations

### 4. Verification Layer (`backend/services/verification.py`)

**Purpose**: Provides deterministic verification for STEM content.

**Verification Types**:
1. **Mathematical**: SymPy for expression validation
2. **Chemical**: RDKit for equation balancing
3. **Code**: Judge0 for code execution
4. **Factual Grounding**: Checks against curriculum documents

**Safety Mechanisms**:
- Prevents hallucination by requiring curriculum citations
- Validates mathematical expressions before presenting to students
- Checks chemical equations for validity
- Executes code in sandboxed environment

## API Architecture

### Authentication (`backend/api/auth.py`)

- JWT-based authentication
- Role-based access control (Student, Parent, Teacher, Admin)
- Password hashing with bcrypt

### Student Endpoints (`backend/api/students.py`)

- `/intake`: Complete student intake interview
- `/state`: Get knowledge graph state
- `/weak-concepts`: Get concepts below mastery threshold
- `/learning-path`: Get recommended learning path

### Tutoring Endpoints (`backend/api/tutoring.py`)

- `/ask`: Ask question to AI tutor
- `/sessions`: Create/get learning sessions
- Implements Socratic dialogue flow

### Practice Endpoints (`backend/api/practice.py`)

- `/generate`: Generate practice problems
- `/submit`: Submit answers and get feedback
- Updates knowledge graph based on performance

### Parent Endpoints (`backend/api/parents.py`)

- `/dashboard`: View all children's learning states
- `/link-child`: Link child accounts

### Teacher Endpoints (`backend/api/teachers.py`)

- `/briefing`: Get morning class briefing
- `/students/{id}/state`: View individual student state

## Database Schema

### Core Tables

**users**: User accounts with authentication
**student_profiles**: Student-specific information
**parent_profiles**: Parent accounts with linked children
**teacher_profiles**: Teacher accounts with class information

**learning_sessions**: Individual learning sessions
**tutoring_interactions**: Chat history with AI tutor
**practice_problems**: Generated practice problems
**practice_attempts**: Student answers and feedback
**knowledge_graphs**: Persistent knowledge graphs
**curriculum_documents**: Curriculum documents and metadata

## Frontend Architecture

### Next.js App Router Structure

```
app/
├── page.tsx          # Landing page
├── login/            # Authentication
├── register/         # User registration
└── dashboard/        # Role-based dashboards
    ├── Student       # Student learning interface
    ├── Parent        # Parent monitoring dashboard
    └── Teacher       # Teacher co-pilot dashboard
```

### State Management

- React Query for server state
- Zustand for client state (optional)
- Local storage for authentication tokens

### API Client (`frontend/lib/api.ts`)

Centralized API client with:
- Automatic token injection
- Error handling
- TypeScript types

## Data Flow Examples

### Example 1: Student Asks Question

```
1. Student submits query via frontend
2. Frontend → POST /api/v1/tutoring/ask
3. Backend:
   a. Retrieve curriculum context (RAG)
   b. Classify query complexity
   c. Route to appropriate model
   d. Generate Socratic response
   e. Verify factual grounding
   f. Save interaction
   g. Update knowledge graph
4. Return response with citations
5. Frontend displays response + Socratic questions
```

### Example 2: Practice Problem Generation

```
1. Student requests practice problem
2. Backend:
   a. Get student's weak concepts from knowledge graph
   b. Retrieve relevant curriculum documents
   c. Generate problem using Sonnet model
   d. Align with curriculum standards
   e. Save problem record
3. Student submits answer
4. Backend:
   a. Retrieve marking scheme
   b. Generate feedback using AI
   c. Detect misconceptions
   d. Update knowledge graph mastery
   e. Record misconceptions
5. Return feedback and updated mastery
```

### Example 3: Parent Dashboard

```
1. Parent requests dashboard
2. Backend:
   a. Get all linked children
   b. For each child:
      - Get knowledge graph state
      - Calculate weak concepts
      - Get recent activity
      - Calculate time spent
3. Return aggregated dashboard
4. Frontend displays visualizations
```

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Role-based access control
3. **Data Isolation**: Students can only access their own data
4. **API Keys**: Stored in environment variables
5. **Input Validation**: Pydantic models for all inputs
6. **SQL Injection**: SQLAlchemy ORM prevents injection
7. **XSS**: React automatically escapes content

## Scalability

### Current Architecture
- Monolithic backend (can be split into microservices)
- Single database (can be sharded by region)
- In-memory Redis (can use Redis Cluster)

### Future Optimizations
1. **Caching**: Redis for frequently accessed curriculum docs
2. **CDN**: Static assets and embeddings
3. **Load Balancing**: Multiple backend instances
4. **Database Replication**: Read replicas for queries
5. **Vector DB Scaling**: ChromaDB → Pinecone for production
6. **Model Caching**: Cache common responses

## Monitoring & Observability

### Recommended Metrics
- API response times
- Model routing distribution
- Knowledge graph update frequency
- Practice problem generation rate
- Student engagement metrics

### Logging
- Structured logging with correlation IDs
- Error tracking (Sentry, etc.)
- Performance monitoring (APM)

## Deployment

### Development
- Docker Compose for local development
- Hot reload for both frontend and backend

### Production
- Kubernetes for orchestration
- PostgreSQL with managed service
- Redis with managed service
- Cloud storage for curriculum documents
- CDN for frontend assets

## Future Enhancements

1. **Multilingual Support**: Full transcreation (not just translation)
2. **Voice Interface**: Voice-first learning for accessibility
3. **Collaborative Learning**: Peer-to-peer study groups
4. **Adaptive Assessments**: Dynamic difficulty adjustment
5. **Teacher Tools**: Advanced analytics and intervention suggestions
6. **Mobile Apps**: Native iOS/Android applications
