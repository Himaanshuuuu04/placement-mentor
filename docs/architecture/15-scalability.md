# Scalability Architecture

## 1. Overview
The platform achieves scalability through a modular microservices architecture, asynchronous event-driven workflows, and state externalization. Components are designed to scale independently based on their specific workload profiles.

## 2. Independently Scalable Components

### 2.1 Asynchronous Workers (Queue-Based Scaling)
These components are decoupled from synchronous API requests and scale horizontally based on queue depth (Redis/BullMQ):
- **Crawl Workers:** Scaled based on the `crawl-fetch` queue size to handle mass ingestion.
- **Embedding Workers:** Scaled based on `document-embed` to manage high-throughput LLM API/local model interactions.
- **Evaluation Workers:** Scaled based on `evaluation` queues to process student submissions asynchronously.

### 2.2 Synchronous Components (Horizontal Scaling)
- **API Gateway & Stateless Services:** Horizontally scalable behind the load balancer based on CPU/Memory utilization.
- **Realtime Gateway (WebSockets):** Horizontally scalable using Redis Pub/Sub as the backplane for message routing across instances.
- **LangGraph Workers:** Scaled horizontally to handle concurrent active interview and mentoring sessions.

### 2.3 Compute-Intensive Components
- **Code Execution Workers (Judge0/Firecracker):** Scaled out across dedicated instances based on submission volume. Given the hard limits per execution (e.g., 256MB RAM per microVM), horizontal scaling of host EC2 instances is strictly predictable.

## 3. Database Scaling
- **PostgreSQL:** Scaled vertically (compute/memory) initially. Partitioning is *only* considered for high-growth append-only tables (like `execution_results` or `mastery_events`) if data growth mathematically necessitates it.
- **MongoDB:** Scales horizontally via sharding if the vector index exceeds single-node memory capacities.
- **Redis:** Used for ephemeral state; scaled via clustering or larger instance types.

## 4. Bottlenecks and Limitations
The system does not claim "infinite scalability". Realistic bottlenecks include:
- **LLM Rate Limits:** External provider quotas limit the speed of real-time Agent responses and batch embedding generation.
- **PostgreSQL Write Throughput:** High volumes of `MasteryUpdated` events or `InterviewTurn` logs could stress write capacity, requiring batching strategies.
- **Crawler Egress:** Crawling large sites is bottle-necked by target domain rate limits (politeness policies) and outbound network bandwidth.
