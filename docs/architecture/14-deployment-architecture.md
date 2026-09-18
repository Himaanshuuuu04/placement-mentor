# Deployment Architecture

## 1. Overview
The system is designed to run locally using Docker Compose for development, and on AWS for production. The deployment architecture leverages managed services where appropriate to minimize operational overhead while maintaining strict security boundaries.

## 2. Local Environment (Docker Compose)
For local development and testing, all dependencies are containerized:
- **Relational Data:** PostgreSQL
- **Vector Data:** MongoDB (or connected to MongoDB Atlas dev instance)
- **Queues/Cache:** Redis
- **Object Storage:** MinIO (S3-compatible)
- **Crawling:** Crawl4AI container
- **Execution:** Judge0 setup (simplified for local if Firecracker is too heavy)
- **Backend Services:** Node.js/Python services running in Docker

## 3. Production Environment (AWS)

### 3.1 Network Architecture (VPC)
- **Internet-Facing Components:** AWS CloudFront (CDN), Application Load Balancer (ALB).
- **Public Subnet:** ALB, NAT Gateways.
- **Private Worker Subnet (Egress-only):** ECS/EKS clusters hosting internal backend services, API Gateways, Agent Orchestrators, and Crawlers.
- **Private Database Subnet (Isolated):** Amazon RDS (PostgreSQL), ElastiCache (Redis). No outbound internet access.
- **Code-Execution Isolation Boundary:** Dedicated EC2 instances (bare metal or instances supporting nested virtualization) for Firecracker/Judge0 in a strictly isolated subnet with no outbound NAT Gateway routing.

### 3.2 Infrastructure Components
- **Compute:** ECS Fargate for stateless API and WebIngection services. Dedicated EC2 for the Code Execution Service to support Firecracker microVMs.
- **Storage:** Amazon S3 for raw/processed documents and artifacts.
- **Database:** Amazon RDS for PostgreSQL. MongoDB Atlas (VPC Peered) for Vector Search. Amazon ElastiCache for Redis/BullMQ.
- **CDN/Edge:** AWS CloudFront for caching Next.js frontend assets and static content.
- **Security:** TLS termination occurs at the ALB. AWS Security Groups enforce strict inbound/outbound rules (e.g., RDS only accepts connections from the Worker Subnet). Internal communication uses private DNS.

## 4. Cost Considerations & Optimization
- **Caching:** CloudFront caches static assets. Redis caches frequent, slow API responses and session states.
- **Asynchronous Processing:** Heavy tasks (crawling, chunking, embedding) run asynchronously via queues, allowing workers to scale down during off-peak hours.
- **Batching:** Document embeddings and mastery updates are batched where possible to reduce LLM and API costs.
- **Compute:** Serverless/Fargate scales to zero or minimal capacity during low traffic.
