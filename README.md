# StackAI Vector Database - Take-Home Implementation

**Author**: Sergio Ayala  
**Company**: StackAI  

## 📋 Task Overview

### Objective
Develop a REST API that allows users to **index** and **query** documents within a custom Vector Database implementation, supporting:

- **CRUD operations** for Libraries, Documents, and Chunks
- **Custom vector indexing algorithms** (no external libraries like FAISS/Pinecone)
- **k-Nearest Neighbor search** with embedding-based similarity
- **Dockerized deployment** with production-ready configuration

### Key Definitions
- **Chunk**: Text piece with embedding and metadata (atomic searchable unit)
- **Document**: Collection of chunks with metadata
- **Library**: Collection of documents with indexing capabilities

## 🏗️ Technical Architecture

### Domain-Driven Design Structure
```
backend/app/
├── main.py                 # FastAPI application factory
├── api/v1/                 # RESTful API endpoints (v1)
│   ├── endpoints/          # Route handlers (presentation layer)
│   └── router.py          # API routing configuration
├── core/                   # Application configuration
├── schemas/                # Pydantic request/response models
├── services/               # Business logic layer (domain services)
├── repositories/           # Data access layer (infrastructure)
├── indexes/                # Custom vector indexing algorithms
└── db/                     # Database models and configuration
```

### SOLID Principles Implementation
- **Single Responsibility**: Each service handles one domain concern
- **Open/Closed**: Index algorithms are pluggable via strategy pattern
- **Liskov Substitution**: All indexes implement common `VectorIndexBase`
- **Interface Segregation**: Clean repository interfaces for data access
- **Dependency Inversion**: Services depend on abstractions, not implementations

## 🧮 Vector Indexing Algorithms

### Custom Implementation (No External Libraries)

#### 1. **HNSW (Hierarchical Navigable Small World)**
- **Time Complexity**: O(log n) search, O(n log n) build
- **Space Complexity**: O(n × M) where M is max connections
- **Use Case**: Best for high-dimensional vectors with frequent queries
- **Implementation**: Multi-layer graph structure with probabilistic connections

#### 2. **LSH (Locality Sensitive Hashing)**
- **Time Complexity**: O(1) average search, O(n) build
- **Space Complexity**: O(n × L) where L is number of hash tables
- **Use Case**: Approximate search with sub-linear query time
- **Implementation**: Random projection hashing with multiple tables

#### 3. **Brute Force Linear Search**
- **Time Complexity**: O(n) search, O(1) build
- **Space Complexity**: O(n)
- **Use Case**: Baseline for small datasets or exact results
- **Implementation**: Exhaustive cosine similarity computation

### Indexing Strategy
- **Algorithm Selection**: Choose between HNSW, LSH, or Brute Force via API parameter
- **Per-Library Indexing**: Each library maintains its own vector index
- **Real-time Indexing**: Chunks are indexed immediately upon creation
- **Thread-safe Operations**: Concurrent read/write access with proper synchronization

## 🗄️ Storage & Persistence

### Current Implementation
- **PostgreSQL Database**: NeonDB (cloud PostgreSQL) for persistent storage
- **In-Memory Vector Indexes**: Fast vector operations with thread-safe data structures
- **Async Operations**: Non-blocking I/O throughout the application
- **Real-time Indexing**: Embeddings generated and indexed on chunk creation

### Database Choice: PostgreSQL (NeonDB)
**Alternatives Considered**: JSON files, SQLite

**Decision Rationale**:
- **Concurrency**: PostgreSQL handles multiple concurrent writers, essential for production workloads
- **ACID Transactions**: Ensures data consistency during complex operations (library deletions, bulk imports)
- **Scalability**: Can handle millions of documents/chunks without performance degradation
- **Production Ready**: Battle-tested for high-traffic applications with proper connection pooling
- **Rich Data Types**: Native JSON support for metadata while maintaining relational benefits

### Vector Index Persistence (Future)
- **S3 Integration**: Store serialized vector indexes in AWS S3
- **Checkpoint System**: Periodic index snapshots for faster startup
- **Incremental Updates**: Delta-based index synchronization
- **Multi-node Consistency**: Distributed index management

## 🚀 Quick Start Guide

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd stackai/backend
```

### 2. Environment Configuration
Create `.env` file:
```bash
# Required: Database and API configuration
DATABASE_URL=postgresql+asyncpg://username:password@ep-example.neon.tech/dbname
COHERE_API_KEY=your_api_key

# Optional: Override defaults
ENVIRONMENT=development
DEBUG=true
EMBEDDING_MODEL=embed-english-v3.0
EMBEDDING_DIMENSION=1024
DEFAULT_VECTOR_INDEX=hnsw
```

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

### 4. Verify Installation
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5. Create Sample Data
```bash
# Run the demo script to create a sample library
python demo_library_creation.py
```

This creates a "Machine Learning Fundamentals" library with:
- 3 documents (Supervised Learning, Neural Networks, Data Preprocessing)
- 36 total chunks with educational content
- Automatic embedding generation and indexing

## 🔌 API Endpoints

### Libraries
- `POST /api/v1/libraries/` - Create library
- `GET /api/v1/libraries/` - List all libraries
- `GET /api/v1/libraries/{id}` - Get library details
- `PUT /api/v1/libraries/{id}` - Update library
- `DELETE /api/v1/libraries/{id}` - Delete library
- `POST /api/v1/libraries/{id}/index` - Trigger re-indexing

### Documents
- `POST /api/v1/documents/` - Create document
- `GET /api/v1/documents/` - List documents (with library filter)
- `GET /api/v1/documents/{id}` - Get document by ID
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document

### Chunks
- `POST /api/v1/chunks/` - Create chunk (auto-generates embedding)
- `GET /api/v1/chunks/` - List chunks (with filters)
- `GET /api/v1/chunks/{id}` - Get chunk by ID
- `PUT /api/v1/chunks/{id}` - Update chunk
- `DELETE /api/v1/chunks/{id}` - Delete chunk
- `POST /api/v1/chunks/{id}/regenerate-embedding` - Regenerate embedding

### Vector Search
- `POST /api/v1/search/?algorithm={hnsw|lsh|brute_force}` - Semantic search with algorithm selection

### Example Search Request
```json
{
  "query": "What is supervised learning?",
  "library_id": "uuid-here",
  "k": 5
}
```

## 🧪 Testing & Quality

### Test Coverage
```bash
# Run comprehensive tests
cd backend/code_testing/
bash run_comprehensive_test.sh

# Individual test suites
python test_algorithms_unit.py      # Algorithm correctness
python test_api_workflow_auto.py    # API integration
python test_vector_search_complete.py  # Search functionality
```

### Quality Assurance
- **Static Typing**: Full type hints with mypy validation
- **Pydantic Validation**: Request/response schema enforcement
- **Error Handling**: Comprehensive exception management
- **Async/Await**: Non-blocking operations throughout
- **Code Quality**: Follows PEP 8 and FastAPI best practices

## 🛣️ Future Roadmap

### 1. RAG (Retrieval-Augmented Generation) Integration
**Goal**: Transform search results into contextual AI responses

**Implementation**:
- Extend search endpoints to include RAG capabilities
- Integrate with LLM providers (OpenAI, Anthropic, local models)
- Context window management for optimal prompt construction
- Citation tracking from source chunks

**Architecture**:
```python
class RAGService:
    async def generate_answer(self, query: str, search_results: List[SearchResult]) -> RAGResponse:
        # Combine search results into context
        # Generate LLM response with citations
        # Return structured answer with sources
```

### 2. Intelligent Auto-Indexing
**Goal**: Automatically select optimal indexing algorithms based on library characteristics

**Decision Factors**:
- **Library Size**: HNSW for >10k chunks, LSH for medium, Brute Force for small
- **Content Type**: Dense embeddings vs sparse features
- **Query Patterns**: Frequent queries favor HNSW, rare queries favor LSH
- **Update Frequency**: High-update libraries prefer incremental algorithms

**Implementation**:
```python
class IndexStrategySelector:
    def select_algorithm(self, library_stats: LibraryStats) -> IndexType:
        # ML-based algorithm selection
        # Performance profiling and adaptation
        # Cost-benefit analysis per use case
```

### 3. Document Processing Pipeline
**Goal**: End-to-end document ingestion with automatic chunking

**Features**:
- **File Type Support**: PDF, DOCX, TXT, HTML, Markdown
- **Intelligent Chunking**: Semantic boundary detection
- **Metadata Extraction**: Title, author, creation date, structure
- **Content Optimization**: OCR, text cleaning, encoding normalization

**Workflow**:
```
File Upload → Format Detection → Text Extraction → 
Semantic Chunking → Embedding Generation → Index Update
```

### 4. Alternative Embedding Models
Evaluate open-source models (SentenceTransformers, E5, BGE) and domain-specific embeddings for improved performance.

### 5. Production Enhancements

#### Persistence & Scaling
- **PostgreSQL Integration**: Metadata and relationships
- **Redis Caching**: Hot path optimization
- **S3 Storage**: Vector index persistence
- **Kubernetes Deployment**: Auto-scaling and load balancing

#### Monitoring & Observability
- **Metrics**: Query latency, index performance, accuracy
- **Tracing**: End-to-end request tracking
- **Alerting**: Performance degradation detection
- **Analytics**: Usage patterns and optimization opportunities
