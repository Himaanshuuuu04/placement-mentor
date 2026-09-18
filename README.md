# AI-Powered Agentic Placement Mentor

Welcome to the **AI-Powered Agentic Placement Mentor**, a sophisticated platform designed to help computer science students prepare for industry placements. The system leverages multi-agent AI orchestration, knowledge tracing, intelligent retrieval-augmented generation (RAG), and secure code execution to provide highly personalized, company-specific preparation and mock technical interviews.

## System Overview

The platform dynamically models a student's evolving knowledge state and adapts the preparation process accordingly. It is architected to seamlessly balance two major workloads:
1.  **Student interaction workloads:** Real-time conversational mentoring, mock interviews, and code evaluation.
2.  **Knowledge acquisition workloads:** Continuous ingestion, chunking, and embedding of technical and company-specific resources.

## High-Level Architecture Platforms

The architecture is divided into the following major logical planes:

*   **Student / Learning Platform:** Manages user profiles, assessments, learning roadmaps, question banks, and mastery tracking.
*   **AI / Agent Platform:** Orchestrates agents (e.g., Code Evaluator, System Design Mentor, Interview Conductor) using LangGraph for multi-step reasoning and interaction.
*   **Knowledge Acquisition Platform:** Handles asynchronous web crawling (Crawl4AI), document processing, chunking, and metadata extraction to populate the RAG vector store.
*   **Secure Execution Platform:** Safely executes and evaluates student code submissions using Judge0 heavily isolated within Firecracker microVMs.
*   **Realtime Platform:** Manages WebSocket connections for streaming tokens and live events, alongside WebRTC for real-time audio interview sessions.

## Core Technologies

*   **Frontend:** Next.js
*   **Agent Orchestration:** LangGraph
*   **Core Database:** PostgreSQL (Transactional State & Graph Checkpoints)
*   **Vector Database:** MongoDB Vector Search (Company-Specific RAG)
*   **Asynchronous Queues & Caching:** Redis + BullMQ
*   **Secure Code Execution:** Judge0 + Firecracker microVMs
*   **Object Storage:** AWS S3 (Raw Documents)
*   **Real-time Communication:** WebSockets & WebRTC

## Documentation

The architecture of this project is formally defined and frozen. For detailed insights into service boundaries, data schemas, event contracts, threat models, and sequence workflows, please refer to the documentation:

*   **[Architecture Freeze Declaration](docs/ARCHITECTURE_FREEZE.md)**
*   **[Full Documentation Directory](docs/)**

> **Note to Contributors:** Do not introduce arbitrary technology replacements or violate the isolation boundaries established in the architecture. Any systemic changes must be documented via an Architecture Decision Record (ADR).
