# 01. System Context Architecture

## 1. Introduction
The "AI-Powered Agentic Placement Mentor" is an advanced learning platform designed to help computer science students prepare for technical interviews and placements. It provides personalized, company-specific preparation using multi-agent orchestration, robust knowledge tracing, secure code execution, and RAG over targeted interview materials.

## 2. High-Level Architecture Planes
The architecture is structured around five major logical planes:

### PLANE A — Student / Learning Platform
The core platform for user management, learning progress, and assessment.
- **Responsibilities**: User profiles, target company/role configuration, question banks, assessment workflows, student mastery modeling, personalized roadmaps, and interview history.
- **Primary Consumers**: Students via the Frontend application.

### PLANE B — AI / Agent Platform
The LangGraph-powered orchestration engine.
- **Responsibilities**: Agent routing, code evaluator agents, system design mentors, knowledge tracing analysis, question/feedback generation, and persistent agent states (checkpoints).
- **Constraints**: Agents interact with the system via explicitly defined APIs and tools. They do not access the database directly.

### PLANE C — Knowledge Acquisition Platform
The web ingestion and document processing pipeline.
- **Responsibilities**: URL discovery, crawl scheduling (Crawl4AI), document extraction, normalization, classification, deduplication, chunking, and embedding.
- **Data Products**: Populates the Vector Store (MongoDB) and Object Storage (S3).

### PLANE D — Secure Execution Platform
The isolated code evaluation environment.
- **Responsibilities**: Running untrusted student code submissions safely.
- **Technologies**: Judge0 inside Firecracker microVMs.
- **Constraints**: Enforces strict CPU, memory, time, network, and process limits to prevent abuse.

### PLANE E — Realtime Platform
The synchronous communication infrastructure.
- **Responsibilities**: Text streaming, session presence, live interview events (WebSockets), and real-time audio signaling (WebRTC).

## 3. Context Diagram (C4 Level 1)

```mermaid
C4Context
    title System Context for AI-Powered Agentic Placement Mentor

    Person(student, "CS Student", "A user preparing for technical interviews.")

    System_Boundary(mentor, "Placement Mentor System") {
        System(webapp, "Web Application", "Next.js frontend delivering the learning experience.")
        System(api_gateway, "API Gateway / BFF", "Routes requests to appropriate backend planes.")
        System(learning_platform, "Learning & Realtime Platform", "Manages user state, mastery, and live interview sessions.")
        System(ai_platform, "AI Agent Platform", "Orchestrates LLM agents for mentoring and evaluation.")
        System(knowledge_platform, "Knowledge Ingestion Platform", "Crawls and processes company/technical data.")
        System(execution_platform, "Secure Execution Platform", "Runs code submissions safely.")
    }

    System_Ext(llm_apis, "LLM Providers", "External APIs (e.g., OpenAI, Anthropic) for agent reasoning.")
    System_Ext(web_sources, "Public Web Sources", "Company blogs, technical documentation, interview experiences.")

    Rel(student, webapp, "Uses", "HTTPS/WSS/WebRTC")
    Rel(webapp, api_gateway, "Makes API calls to", "JSON/HTTPS")
    Rel(api_gateway, learning_platform, "Routes to")
    Rel(api_gateway, ai_platform, "Routes to")
    Rel(learning_platform, execution_platform, "Submits code to")
    Rel(ai_platform, llm_apis, "Queries for reasoning", "HTTPS")
    Rel(knowledge_platform, web_sources, "Crawls data from", "HTTPS")
```

## 4. Key External Interfaces
- **Students**: Interact with the system via web browsers and mobile clients.
- **LLM APIs**: Provide foundational intelligence, reasoning, and content generation capabilities.
- **Web Sources**: The unstructured data source (canonical web pages, blogs) for the RAG knowledge base.
