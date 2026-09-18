# 02. Container Architecture

## 1. Introduction
The Container Architecture defines the high-level technical deployments that make up the AI-Powered Agentic Placement Mentor. The system follows a modular microservices approach grouped by bounded contexts, utilizing Next.js for the frontend, robust backend services, and specialized infrastructure containers for distinct workloads.

## 2. Container Diagram (C4 Level 2)

```mermaid
C4Container
    title Container Architecture

    Person(student, "CS Student", "Uses the platform")

    System_Boundary(frontend_boundary, "Client") {
        Container(frontend, "Web App (Next.js)", "React/Next.js", "Provides UI for learning, coding, and interviews")
    }

    System_Boundary(gateway_boundary, "Edge") {
        Container(api_gateway, "API Gateway / BFF", "Nginx/Node", "Handles authentication, rate limiting, and routing")
        Container(realtime_gateway, "Realtime Gateway", "Node.js/Socket.io/WebRTC", "Handles WebSockets and Audio signaling")
    }

    System_Boundary(services_boundary, "Microservices") {
        Container(learning_services, "Learning Services", "Python/Go/Node", "Manages users, mastery, questions, roadmaps")
        Container(ai_agents, "Agent Orchestrator", "Python/LangGraph", "Runs LLM agent workflows and tools")
        Container(knowledge_services, "Ingestion Pipeline", "Python", "Crawls, processes, and embeds documents")
    }

    System_Boundary(execution_boundary, "Execution") {
        Container(judge0, "Judge0 API", "Ruby/Go", "Manages code execution requests")
        Container(firecracker, "Firecracker microVMs", "Rust", "Provides secure isolation for code execution")
    }

    System_Boundary(data_boundary, "Persistence") {
        ContainerDb(postgres, "PostgreSQL", "PostgreSQL", "System of record for transactional application state")
        ContainerDb(mongodb, "MongoDB", "MongoDB Vector Search", "Stores documents, chunks, and embeddings for RAG")
        ContainerDb(redis, "Redis", "Redis", "BullMQ event queues, short-lived cache, distributed locks")
        ContainerDb(s3, "S3 Object Storage", "AWS S3 / MinIO", "Stores raw crawled HTML/Markdown and execution artifacts")
    }

    Rel(student, frontend, "Visits", "HTTPS")
    Rel(frontend, api_gateway, "API Requests", "HTTPS/REST")
    Rel(frontend, realtime_gateway, "Live Events/Audio", "WSS/WebRTC")
    
    Rel(api_gateway, learning_services, "Routes", "REST/gRPC")
    Rel(api_gateway, ai_agents, "Routes", "REST/gRPC")
    Rel(api_gateway, knowledge_services, "Routes", "REST/gRPC")
    
    Rel(learning_services, postgres, "Reads/Writes", "TCP")
    Rel(learning_services, redis, "Publishes events to", "TCP")
    Rel(learning_services, judge0, "Submits code to", "HTTP")
    
    Rel(ai_agents, postgres, "Reads/Writes Checkpoints", "TCP")
    Rel(ai_agents, mongodb, "Queries Vectors", "TCP")
    
    Rel(knowledge_services, mongodb, "Writes Embeddings", "TCP")
    Rel(knowledge_services, s3, "Stores Raw Docs", "HTTP")
    Rel(knowledge_services, redis, "Consumes/Produces Queue", "TCP")
    
    Rel(judge0, firecracker, "Spawns MicroVMs", "TCP/Socket")
```

## 3. Technology Stack Justification
- **Frontend (Next.js)**: Enables Server-Side Rendering (SSR) for fast initial loads, SEO, and robust integration with rich interactive components like code editors and WebRTC audio players.
- **Relational Database (PostgreSQL)**: Serves as the strict system of record for highly structured, transactional data (users, mastery, assessments). Supported by PostgresSaver for LangGraph persistence.
- **Vector Store (MongoDB)**: MongoDB Vector Search handles RAG document storage, vector similarity search, and rich metadata filtering natively in one location.
- **Cache & Message Broker (Redis)**: Facilitates short-lived state, rate limiting, and BullMQ queues for asynchronous jobs (crawling, evaluation, embeddings).
- **Object Storage (S3)**: Acts as the definitive repository for raw ingestion artifacts to preserve exact provenance, allowing data to be reprocessed or re-embedded without triggering new web crawls.
- **Orchestration (LangGraph)**: Provides native support for multi-agent cyclic graphs, state management, and persistent checkpoints essential for complex mentoring conversations.
- **Execution Engine (Judge0 + Firecracker)**: Ensures enterprise-grade security against malicious student code by isolating execution within hardened microVMs with strict resource ceilings.
