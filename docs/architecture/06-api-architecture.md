# 06. API Architecture

## 1. Design Principles
The API tier follows strict RESTful conventions, providing synchronous boundaries between the frontend clients and the backend microservices.

- **Standardization**: Uses standard HTTP verbs (GET, POST, PUT, PATCH, DELETE) and resource-oriented URLs.
- **Versioning**: All externally exposed APIs are prefixed with `/api/v1/`. Breaking changes mandate a schema bump (e.g., `/api/v2/`).
- **Data Format**: `application/json` is the sole data format for requests and responses.
- **Statelessness**: The API layer is completely stateless. User context is resolved entirely via tokens.

## 2. API Gateway & Cross-Cutting Concerns
- **Authentication**: JWT token validation occurs at the API Gateway. Backend services receive trusted headers detailing the `user_id`.
- **Authorization**: RBAC (Role-Based Access Control) claims embedded within the JWT dictate permissions (e.g., Student vs. Admin routes).
- **Rate Limiting**: IP and User-ID based rate limiting is managed via Redis at the edge to prevent API abuse, mitigate DDoS, and strictly control underlying LLM execution costs.
- **Idempotency**: All mutating operations (POST, PUT, PATCH) support an `Idempotency-Key` header, allowing safe retries on network failures.

## 3. Core API Contracts (OpenAPI 3.1 Style)

### Identity, Configuration & Taxonomy
- `GET /api/v1/users/me`: Retrieves current user profile.
- `PUT /api/v1/users/me/profile`: Updates target configurations.
- `GET /api/v1/companies`: Lists supported target companies.
- `GET /api/v1/roles`: Lists target roles.
- `GET /api/v1/topics`: Retrieves the competency taxonomy.

### Learning, Assessment & Mastery
- `GET /api/v1/questions`: Retrieves questions, supporting filtering by company, role, or topic.
- `POST /api/v1/assessments`: Initializes a new timed assessment.
- `POST /api/v1/submissions`: Submits code for a specific assessment question.
- `GET /api/v1/evaluations/{submission_id}`: Polls or retrieves evaluation feedback for a submission.
- `GET /api/v1/mastery/me`: Retrieves the student's multidimensional mastery radar (LKT/IRT state).
- `GET /api/v1/roadmaps/me`: Retrieves the deterministic learning schedule and priority topics.

### Interviews & Realtime
- `POST /api/v1/interviews`: Initializes a mock interview session. Returns a session ID and secure WebSocket/WebRTC connection tickets.
- `GET /api/v1/interviews`: Lists historical interview sessions.
- `GET /api/v1/interviews/{id}/history`: Retrieves full transcripts and turn data.

### Internal & Agent APIs (Protected)
- `POST /api/v1/retrieval/search`: Exposes semantic/hybrid search over the vector store (Used by LangGraph Agents).
- `POST /api/v1/ingestion/trigger`: Admin endpoint to manually trigger crawl workflows.

## 4. Standard Response Formats

**Success Response (2xx)**
All standard responses wrap data in a `data` envelope and provide pagination metadata where applicable.
```json
{
  "data": { ... },
  "meta": {
    "pagination": {
      "total": 150,
      "limit": 20,
      "offset": 0
    }
  }
}
```

**Error Response (4xx, 5xx)**
Errors are structured for programmatic parsing by the frontend.
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Invalid fields in request",
    "details": [
      { "field": "code_snippet", "issue": "cannot be empty" }
    ]
  },
  "request_id": "req-abcd-1234-xyz"
}
```
