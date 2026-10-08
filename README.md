# Bulk Certificate Generator

A backend service for generating certificates in bulk for event participants.

The system accepts a list of recipients, creates a bulk certificate generation job, processes certificates asynchronously using Redis workers, tracks individual certificate status, and provides APIs to monitor jobs and retrieve generated certificates.

## Features

- Create events
- Create bulk certificate generation jobs
- Validate recipient data
- Generate certificates asynchronously
- Redis-based queue processing
- Multiple worker support
- Job progress tracking
- Individual certificate success/failure tracking
- Failure isolation: one bad recipient does not stop other recipients
- Duplicate certificate prevention per event/user
- PDF certificate retrieval
- Automated API tests using pytest

## Architecture

```text
Client
   |
   v
FastAPI
   |
   +--------------------+
   |                    |
   v                    v
PostgreSQL             Redis
                         |
                  certificate_queue
                         |
              +----------+----------+
              |          |          |
              v          v          v
           Worker 1   Worker 2   Worker 3
              |
              v
      Certificate Generation
              |
              v
       Certificate Storage
```

Multiple workers consume the same Redis queue. Each worker processes an individual certificate independently.

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- ReportLab
- Pytest
- Docker
- GitHub Actions — future scope

## Project Structure

```text
bulk-certificate-generator/
├── app/
│   ├── certificate/
│   │   └── template.py
│   ├── config/
│   │   └── settings.py
│   ├── database/
│   │   ├── connection.py
│   │   ├── dependencies.py
│   │   └── redis.py
│   ├── models/
│   │   ├── base.py
│   │   ├── event.py
│   │   ├── user.py
│   │   ├── job.py
│   │   └── certificate.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── event_repository.py
│   │   ├── job_repository.py
│   │   └── certificate_repository.py
│   ├── routers/
│   │   ├── event.py
│   │   ├── certificate_job.py
│   │   ├── job.py
│   │   └── certificate.py
│   ├── schemas/
│   │   ├── event.py
│   │   └── certificate_job.py
│   ├── services/
│   │   ├── event_service.py
│   │   └── certificate_job_service.py
│   └── main.py
├── worker/
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_event.py
│   ├── test_certificate_job.py
│   ├── test_job.py
│   └── test_certificate.py
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Database Design

### Events

Stores event information:

```text
id
name
description
event_date
created_at
```

### Users

Stores certificate recipients:

```text
id
name
email
created_at
```

Email identifies an existing user.

### Jobs

A Job represents one bulk generation request:

```text
id
event_id
status
total_count
success_count
failed_count
created_at
completed_at
```

### Certificates

A Certificate represents one recipient's certificate:

```text
id
job_id
event_id
user_id
status
s3_key
error_message
created_at
completed_at
```

## Status Lifecycles

Certificate:

```text
pending
   |
   v
processing
   |
   +----> completed
   |
   +----> failed
```

Job:

```text
queued
   |
   v
processing
   |
   v
completed
```

A job reaches `completed` when all certificates have reached a final state. Individual certificate records show which recipients succeeded or failed.

## API Endpoints

### Create Event

```http
POST /events
```

Example:

```json
{
  "name": "Python Workshop",
  "description": "Backend Workshop",
  "event_date": "2026-10-20"
}
```

### Create Certificate Job

```http
POST /events/{event_id}/certificate-jobs
```

Example:

```json
{
  "recipients": [
    {
      "name": "Mukul",
      "email": "mukul@example.com"
    },
    {
      "name": "Rahul",
      "email": "rahul@example.com"
    }
  ]
}
```

The API creates the job and certificate records and queues pending certificate IDs in Redis.

### Get Job Status

```http
GET /jobs/{job_id}
```

Example:

```json
{
  "job_id": 1,
  "event_id": 1,
  "status": "processing",
  "total": 100,
  "successful": 75,
  "failed": 5,
  "pending": 20
}
```

### Get Job Certificates

```http
GET /jobs/{job_id}/certificates
```

Returns certificate status and failure information for the job.

### Retrieve Certificate

```http
GET /certificates/{certificate_id}
```

Returns the generated PDF when the certificate is completed successfully.

## Running Locally

### 1. Clone

```bash
git clone <your-repository-url>
cd bulk-certificate-generator
```

### 2. Virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

Copy `.env.example` to `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/certificate_db
REDIS_URL=redis://localhost:6379/0
```

Do not commit `.env`.

### 5. Start infrastructure

```bash
docker compose up -d
```

### 6. Start FastAPI

```bash
python -m uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

### 7. Start a worker

In another terminal:

```bash
python -m worker.main
```

Additional worker processes can be started in additional terminals. They all consume from the same Redis queue.

## Running Tests

Use a separate database for automated tests.

Create it once:

```sql
CREATE DATABASE certificate_test_db;
```

Run:

```bash
python -m pytest -v
```

Tests should never use the production database.

The test environment should point to `certificate_test_db` and should not use the normal development database.

## Testing Strategy

The test suite covers:

- Event creation
- Certificate job creation
- Recipient validation
- Invalid recipient handling
- Job status
- Certificate listing
- Certificate retrieval
- Failure isolation

Example failure isolation:

```text
Recipient A -> completed
Recipient B -> failed
Recipient C -> completed
```

Recipient B failing does not stop A or C.

## Asynchronous Processing

The API does not wait for every PDF to be generated.

```text
Client
  |
  v
Create Job
  |
  v
Create Certificate Records
  |
  v
Push Pending Certificate IDs to Redis
  |
  v
Return Job ID
```

Workers then:

```text
BLPOP Redis Queue
      |
      v
Get Certificate
      |
      v
Mark processing
      |
      v
Generate PDF
      |
      +----> completed
      |
      +----> failed
```

This keeps the API responsive during bulk generation.

## Multiple Workers

All workers consume the same Redis queue:

```text
                 Redis Queue
                     |
          +----------+----------+
          |          |          |
          v          v          v
       Worker 1   Worker 2   Worker 3
          |          |          |
          v          v          v
       Cert 1     Cert 2     Cert 3
```

Each worker waits for work using Redis `BLPOP`.

## Failure Isolation

Each certificate is processed independently.

For example:

```text
Certificate 1 -> completed
Certificate 2 -> completed
Certificate 3 -> failed
Certificate 4 -> completed
Certificate 5 -> completed
```

Final job state:

```text
total      = 5
successful = 4
failed     = 1
pending    = 0
```

The individual certificate stores the error message.

## Duplicate Certificate Handling

Users are identified by email.

Before creating a certificate, the service checks for an existing certificate using:

```text
event_id + user_id
```

If one already exists, the new certificate record is marked as failed with an appropriate error message instead of generating another certificate.

## Layered Architecture

```text
Router
   |
   v
Service
   |
   v
Repository
   |
   v
Database
```

### Router

Handles HTTP requests and responses.

### Service

Contains business rules such as:

- recipient validation
- user lookup/creation
- duplicate checks
- job creation
- queueing

### Repository

Handles database operations such as:

- create user
- find user by email
- create job
- update job
- create certificates
- retrieve certificates

## Design Decisions

### Why asynchronous processing?

Certificate generation is a bulk operation. Generating many PDFs inside the HTTP request would keep the request open unnecessarily.

The API therefore creates the job and queues work while workers generate certificates in the background.

### Why PostgreSQL?

The system has relational entities and foreign-key relationships:

```text
Event
  |
  +---- Job
          |
          +---- Certificate
                    |
                    +---- User
```

PostgreSQL provides persistence, transactions, foreign keys, and relational querying.

### Why Redis?

Redis provides a lightweight queue between the API and workers. It also allows multiple workers to consume pending certificate IDs concurrently.

### Why ReportLab?

ReportLab generates the certificate PDFs programmatically from the predefined certificate template.

### Why Job and Certificate are separate?

A Job represents the complete bulk request, while a Certificate represents one recipient.

```text
Job 10
├── Certificate 101
├── Certificate 102
├── Certificate 103
└── Certificate 104
```

This allows per-recipient status and failure tracking.

## Environment Separation

Development and automated tests use different databases:

```text
Development
    |
    v
certificate_db

Automated Tests
    |
    v
certificate_test_db
```

Production must never be used as the automated test database.

## CI/CD — Future Scope

CI/CD is not part of the current implementation.

A future GitHub Actions pipeline can automatically:

```text
Developer
   |
   v
git push / Pull Request
   |
   v
GitHub Actions
   |
   +--> Setup Python
   |
   +--> Install dependencies
   |
   +--> Start PostgreSQL
   |
   +--> Start Redis
   |
   +--> Run pytest
   |
   v
Tests pass?
   /       \
 No         Yes
 |           |
Stop      Continue
             |
             v
       Build Docker image
             |
             v
       Push to registry
             |
             v
       Deploy to AWS
```

The CI pipeline should prevent deployment when automated tests fail.

## Current Storage

Generated PDFs are currently stored locally.

The certificate record stores the generated file path in the `s3_key` field.

Amazon S3 can replace local storage later without changing the overall job-processing design.

## Security

- `.env` is excluded from Git.
- Database and Redis configuration comes from environment variables.
- Production credentials should be stored in a secrets manager.
- Authentication and authorization should be added before public deployment.
- Recipient input is validated before generation.

## Future Improvements

- Amazon S3 certificate storage
- Alembic migrations
- Authentication and authorization
- Retry mechanism
- Structured logging
- Monitoring and metrics
- Frontend dashboard
- Production deployment
- Rate limiting
- More robust worker lifecycle management

## End-to-End Flow

```text
1. Client creates event
          |
          v
2. Client submits recipients
          |
          v
3. API creates Job
          |
          v
4. Recipients are validated
          |
          v
5. Users are found/created
          |
          v
6. Certificate records are created
          |
          v
7. Pending certificate IDs go to Redis
          |
          v
8. API returns Job ID
          |
          v
9. Workers consume IDs
          |
          v
10. Worker generates PDF
          |
          v
11. Certificate becomes completed/failed
          |
          v
12. Job counters are updated
          |
          v
13. Client checks job status
          |
          v
14. Client retrieves completed certificate
```

## Project Status

Core backend functionality includes:

- Bulk job creation
- PostgreSQL persistence
- Redis asynchronous processing
- Multiple worker support
- Per-recipient failure isolation
- Job progress tracking
- Certificate retrieval
- Automated testing foundation

CI/CD, S3 storage, authentication, monitoring, and deployment automation are documented as future enhancements.
