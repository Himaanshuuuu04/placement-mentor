# Data Dictionary

## PostgreSQL Entities (System of Record)

### User & Identity Domain
| Entity | Description | Data Ownership |
| --- | --- | --- |
| `users` | Core user identity and credentials. | Identity / User Service |
| `user_profiles` | Extended user information (university, graduation year). | Identity / User Service |

### Organization Domain
| Entity | Description | Data Ownership |
| --- | --- | --- |
| `companies` | Target companies for placement (e.g., Google, Amazon). | Company & Role Service |
| `roles` | Specific roles within companies (e.g., SDE I, Frontend Engineer). | Company & Role Service |
| `topics` | Subject matter topics (e.g., Dynamic Programming, System Design). | Topic / Competency Service |
| `role_competencies` | Mapping of roles to required topics with weights. | Company & Role Service |

### Content & Assessment Domain
| Entity | Description | Data Ownership |
| --- | --- | --- |
| `questions` | Coding or theoretical questions. | Question Bank Service |
| `question_topics` | Mapping of questions to topics. | Question Bank Service |
| `question_companies` | Mapping of questions to companies for frequency tracking. | Question Bank Service |
| `assessments` | Groupings of questions for a specific test. | Assessment Service |

### Execution & Evaluation Domain
| Entity | Description | Data Ownership |
| --- | --- | --- |
| `submissions` | Student code submissions for questions. | Assessment Service |
| `execution_jobs` | Tracking of secure code execution tasks in Judge0/Firecracker. | Code Execution Service |
| `execution_results` | Outputs (stdout, stderr, limits) of an execution job. | Code Execution Service |
| `evaluations` | AI-generated feedback, complexity analysis, and scores. | Evaluation Service |

### Knowledge Tracing Domain
| Entity | Description | Data Ownership |
| --- | --- | --- |
| `student_mastery` | The current, aggregated knowledge state of a student per topic. | Knowledge Tracing / Mastery Service |
| `mastery_events` | Immutable log of knowledge signals updating the mastery state. | Knowledge Tracing / Mastery Service |

### Interview & Agent Domain
| Entity | Description | Data Ownership |
| --- | --- | --- |
| `interview_sessions` | High-level session data for a mock interview. | Interview Service |
| `interview_turns` | Sequential dialogue turns (student and agent) in an interview. | Interview Service |
| `interview_feedback` | Post-interview summary and scoring. | Interview Service |
| `learning_roadmaps` | Personalized preparation paths for students. | Roadmap / Personalization Service |

### Ingestion & Processing Domain
| Entity | Description | Data Ownership |
| --- | --- | --- |
| `knowledge_sources` | Root URLs or domains configured for scraping. | Crawl Service |
| `crawl_jobs` | Execution tracking for crawling runs. | Crawl Service |
| `discovered_urls` | URLs found during crawling to feed the queue. | Data Discovery Service |
| `documents` | High-level representation of scraped canonical documents. | Document Processing Service |
| `document_versions` | Versioned history of a document linked to raw S3 artifacts. | Document Processing Service |

## MongoDB Entities (Knowledge Store)

| Entity | Description | Data Ownership |
| --- | --- | --- |
| `knowledge_documents` | Document metadata, content hashes, and quality metrics used for RAG filtering. | Embedding / Indexing Service |
| `knowledge_chunks` | Chunked text and vector embeddings for semantic search. | Embedding / Indexing Service |

## S3 Object Storage Categories
- `raw/`: Unprocessed HTML/PDFs from the crawler.
- `processed/`: Markdown representations.
- `documents/`: Extracted JSON metadata.
