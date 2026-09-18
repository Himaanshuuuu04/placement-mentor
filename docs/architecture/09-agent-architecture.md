# Agent Architecture

## 1. Overview
The Agent Architecture (PLANE B) orchestrates the AI-driven interactions of the mentor platform using LangGraph. It is responsible for reasoning, tutoring, evaluation, mock interviews, and system design mentoring.

## 2. LangGraph Architecture

The system utilizes a multi-agent orchestration pattern coordinated via LangGraph. Agents interact with the platform explicitly through tools and service APIs rather than direct database manipulation.

### 2.1 Nodes and Responsibilities

- **Router Node:** Analyzes the user's input intent and routes the state to the appropriate specialized agent (e.g., Coding, Interview, System Design).
- **Code Evaluator Node:** Analyzes code execution results (from Judge0), checks for algorithmic correctness, time/space complexity, and code quality, and generates evaluation feedback.
- **Interview Conductor Node:** Manages mock interviews, simulating interviewer personas (e.g., friendly, rigorous), asking follow-up questions based on real-time transcripts, and tracking interview progression.
- **System Design Mentor Node:** Guides users through system design questions, prompting for requirements, architecture, scaling, and bottleneck identification without immediately giving away the answer.
- **Knowledge Tracer Node:** Observes student interactions and evaluations to generate `MasteryUpdated` events, continuously refining the student's multidimensional mastery profile.
- **Question Generator Node:** Generates adaptive, company-specific questions tailored to the student's current mastery level and target role.
- **Feedback Generator Node:** Synthesizes evaluations and interview performance into actionable feedback.

### 2.2 Agent-to-Service Communication
Agents **must not** directly query or modify PostgreSQL. They interact with data via explicit tool boundaries (e.g., calling the Mastery API). 
- *Anti-pattern:* Agent → PostgreSQL
- *Correct pattern:* Agent → Mastery Service (API) → PostgreSQL

## 3. Agent State
LangGraph state contains only the context necessary for the current conversational and reasoning task. Authoritative business data remains in the respective microservices.

### 3.1 State Schema Categories
- **Session:** `session_id`, `turn_count`
- **User/Target:** `user_id`, `target_company`, `target_role`
- **Conversation:** Chat history (sliding window or summarized), `current_question`
- **Retrieval Context:** Context fetched from the Retrieval Service (RAG)
- **Evaluation:** Temporary execution results, rubric scores
- **Next Action:** Routing directives for LangGraph edges

### 3.2 State Separation
- **Short-term conversational state:** Ephemeral, held in the graph state.
- **Persistent agent checkpoint state:** Stored in PostgreSQL (via `PostgresSaver`) for LangGraph graph persistence, allowing long-running sessions to be paused and resumed.
- **Long-term user/mastery state:** Owned strictly by the Knowledge Tracing / Mastery Service, not the graph.

## 4. Probabilistic Logic Boundaries
- **AI Outputs:** Treated as probabilistic. AI handles generation, conversational tutoring, and subjective evaluation.
- **Deterministic Logic:** Code execution correctness, test case matching, rate limiting, and core mastery score aggregation are kept outside the LLM to ensure reliability and predictability.
