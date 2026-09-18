# Security Architecture

## 1. Overview
The Security Architecture defines the threat model and defense mechanisms for the AI-Powered Placement Mentor. It strictly distinguishes between trusted system data, untrusted user inputs, untrusted web content, and non-deterministic LLM-generated output.

## 2. Threat Model and Mitigations

### 2.1 Identity and Access
- **Authentication:** All external APIs require valid JWT-based authentication via the API Gateway. Internal service communication requires internal mTLS or service-to-service tokens.
- **Authorization & RBAC:** Role-Based Access Control ensures students cannot access other students' data, and admins/crawlers have restricted domain boundaries.
- **Tenant Isolation:** Data is isolated logically by `user_id` at the database level. Direct cross-tenant access is prohibited.

### 2.2 Application Security
- **API Abuse & Rate Limiting:** Rate limiting (via Redis) is applied at the API Gateway to prevent volumetric attacks and resource exhaustion.
- **Data Poisoning & RAG Poisoning:** Scraped webpages are **never** treated as trusted instructions. Strict classification algorithms filter out low-relevance or malformed documents before they reach the MongoDB vector store. 

### 2.3 AI and LLM Security
- **Prompt Injection:** User inputs and retrieved RAG context are isolated from system instructions using structural delimiters and role-based messaging boundaries (e.g., separating system prompts from user messages).
- **Indirect Prompt Injection:** Web content injected via RAG is sanitized. LLMs are instructed to treat retrieved context strictly as data, not as executable commands.

### 2.4 Infrastructure and Execution Security
- **Code Execution Escape:** Untrusted code runs in Firecracker microVMs with strict limits and no network access (detailed in `10-execution-security.md`).
- **SSRF (Server-Side Request Forgery):** The Web Ingestion crawler strictly validates URLs, prohibits internal IP crawling, and enforces domain allowlists.
- **S3 Access:** S3 buckets containing raw documents and processing artifacts are private, accessible only via IAM roles assigned to specific backend services.
- **Database Exposure:** PostgreSQL, MongoDB, and Redis instances run in private subnets, completely inaccessible from the public internet.

### 2.5 Realtime Security
- **WebSocket/WebRTC Abuse:** Connections require initial token-based authentication. Messages are validated against expected schemas to prevent malformed payload attacks.

## 3. Data Trust Boundaries
- **Trusted:** Internal PostgreSQL databases, system prompts, API route configurations.
- **Untrusted (Validated):** User inputs (chat, form data). Must be sanitized and validated.
- **Untrusted (Isolated):** Submitted code. Must only execute in microVMs.
- **Untrusted (Quarantined):** Scraped web data. Must undergo normalization, classification, and separation from instructions.
- **Probabilistic:** LLM output. Cannot directly execute state-mutating database commands without deterministic service mediation.
