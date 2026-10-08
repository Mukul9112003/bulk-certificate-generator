# Bulk Certificate Generator

A backend system for generating certificates in bulk from a predefined certificate template.

The system accepts a single certificate-generation request containing multiple recipients, creates a background job, processes certificates through a Redis queue, tracks individual certificate status, and provides APIs for monitoring job progress and retrieving generated certificates.

## Features

- Create events.
- Submit one bulk certificate-generation request for multiple recipients.
- Validate recipient name and email data using Pydantic.
- Create one certificate record per recipient.
- Process certificate generation asynchronously using Redis and a worker.
- Track certificate status:
  - `pending`
  - `processing`
  - `completed`
  - `failed`
- Track job progress:
  - total
  - successful
  - failed
  - pending
- Allow one certificate to fail without stopping other certificates in the same job.
- Generate PDF certificates using a single predefined template.
- Retrieve completed certificates through an API.
- PostgreSQL for persistent application data.
- Redis for background-job queuing.
- Designed to support multiple worker instances.
- Certificate files currently use local storage; the storage layer can later be moved to S3-compatible object storage/AWS S3.

## Architecture

```text
                    ┌──────────────────┐
                    │     Frontend     │
                    └────────┬─────────┘
                             │ HTTP
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    └──────┬─────┬─────┘
                           │     │
                           │     ▼
                           │  PostgreSQL
                           │
                           ▼
                         Redis
                           │
                    certificate_queue
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Worker 1      Worker 2      Worker 3
              │            │            │
              └────────────┼────────────┘
                           ▼
                    PDF Generation
                           │
                           ▼
                  Certificate Storage
                    (local currently)
```

### Why background processing?

Certificate generation can involve many recipients. Instead of making the client wait for every PDF to be generated inside the HTTP request, the API creates a job and places certificate work into Redis.

Workers process individual certificates independently.

This also means a failure for one recipient does not unnecessarily stop the remaining recipients.

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- ReportLab
- Pydantic
- Docker / Docker Compose
- pytest (for tests)

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── dependencies.py
│   │   └── redis.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── event.py
│   │   ├── user.py
│   │   ├── job.py
│   │   └── certificate.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── event_repository.py
│   │   ├── job_repository.py
│   │   └── certificate_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── event_service.py
│   │   └── certificate_job_service.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── event.py
│   │   ├── certificate_job.py
│   │   ├── job.py
│   │   └── certificate.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── event.py
│   │   └── certificate_job.py
│   │
│   ├── certificate/
│   │   ├── __init__.py
│   │   └── template.py
│   │
│   └── config/
│       ├── __init__.py
│       └── settings.py
│
├── worker/
│   ├── __init__.py
│   └── main.py
│
├── generated_certificates/
│
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Database Design

### `events`

Stores event information.

```text
id
name
description
event_date
created_at
```

### `users`

Stores recipients.

```text
id
name
email
created_at
```

The email is unique so the same recipient can be reused across different certificate jobs.

### `jobs`

Represents one bulk certificate-generation request.

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

A job can contain many certificates.

### `certificates`

Represents one certificate for one recipient.

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

The `s3_key` field is currently used to store the generated file path. It is reserved for the future move to object storage.

## Job and Certificate Lifecycle

### Certificate

```text
pending
   ↓
processing
   ↓
completed
```

or:

```text
pending
   ↓
processing
   ↓
failed
```

### Job

```text
queued
   ↓
processing
   ↓
completed
```

A completed job may contain both successful and failed certificates. The individual certificate records identify which certificates succeeded or failed.

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd bulk-certificate-generator
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/certificate_db
REDIS_URL=redis://localhost:6379/0
```

Do not commit `.env` to Git.

## Start PostgreSQL and Redis

Run:

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

Expected services:

```text
certificate-postgres
certificate-redis
```

## Run the FastAPI Application

From the project root:

```bash
python -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Run the Certificate Worker

In another terminal:

```bash
python -m worker.main
```

You should see:

```text
Certificate worker started
```

The worker waits for certificate IDs from the Redis queue.

## API Usage

### 1. Create an Event

```http
POST /events
```

Request:

```json
{
  "name": "Python Backend Workshop",
  "description": "FastAPI and backend development workshop",
  "event_date": "2026-10-10"
}
```

Example response:

```json
{
  "id": 1,
  "name": "Python Backend Workshop",
  "description": "FastAPI and backend development workshop",
  "event_date": "2026-10-10"
}
```

Use the actual returned event ID for subsequent requests.

### 2. Create a Bulk Certificate Job

```http
POST /events/{event_id}/certificate-jobs
```

Example:

```http
POST /events/1/certificate-jobs
```

Request:

```json
{
  "recipients": [
    {
      "name": "Rahul Sharma",
      "email": "rahul.sharma@example.com"
    },
    {
      "name": "Amit Kumar",
      "email": "amit.kumar@example.com"
    },
    {
      "name": "Priya Singh",
      "email": "priya.singh@example.com"
    }
  ]
}
```

Example response:

```json
{
  "job_id": 1,
  "event_id": 1,
  "status": "queued",
  "total": 3
}
```

The API returns immediately while the workers process the certificates in the background.

### 3. Check Job Progress

```http
GET /jobs/{job_id}
```

Example:

```http
GET /jobs/1
```

Example response while processing:

```json
{
  "job_id": 1,
  "event_id": 1,
  "status": "processing",
  "total": 3,
  "successful": 1,
  "failed": 0,
  "pending": 2
}
```

Example completed response:

```json
{
  "job_id": 1,
  "event_id": 1,
  "status": "completed",
  "total": 3,
  "successful": 2,
  "failed": 1,
  "pending": 0
}
```

### 4. Retrieve a Certificate

```http
GET /certificates/{certificate_id}
```

Example:

```http
GET /certificates/1
```

If the certificate is completed, the API returns the generated PDF.

If the certificate is still processing, the API returns a `409` response.

If the certificate does not exist, the API returns `404`.

## Validation and Failure Handling

Recipient data is validated before processing.

For example:

```json
{
  "recipients": []
}
```

is rejected.

Invalid email addresses are also rejected.

During background processing, certificates are handled independently.

For example:

```text
5 certificates

Worker processing:

Certificate 1 → completed
Certificate 2 → completed
Certificate 3 → failed
Certificate 4 → completed
Certificate 5 → completed
```

The job can still finish with:

```text
total = 5
successful = 4
failed = 1
```

The failure is stored in the individual certificate's `error_message`.

## Multiple Workers

The system is designed around a shared Redis queue.

Multiple worker processes can consume from:

```text
certificate_queue
```

For example:

```text
Redis
  │
  ├── Worker 1
  ├── Worker 2
  └── Worker 3
```

A worker takes one certificate ID from the queue and processes it.

This allows certificate generation to scale horizontally by running additional worker instances instead of creating one container per certificate.

## Certificate Storage

The current implementation generates PDFs in:

```text
generated_certificates/
```

The database stores the generated file path in `certificates.s3_key`.

This naming is intentional for future object-storage support.

### Future S3 migration

The planned architecture is:

```text
Worker
   ↓
Generate PDF
   ↓
Object Storage
   ↓
S3
```

The application can later replace local file storage with AWS S3 or another S3-compatible object-storage service without changing the core job-processing model.

## Testing

Run:

```bash
pytest
```

Tests should cover:

- Creating a generation job.
- Input validation.
- Certificate generation.
- Job status/progress.
- Individual certificate failure.
- Certificate retrieval.

## Design Decisions

### Why FastAPI?

FastAPI provides a simple API layer with automatic validation and interactive Swagger documentation.

### Why PostgreSQL?

PostgreSQL is used as the relational database for persistent event, user, job, and certificate information.

### Why Redis?

Redis provides a simple queue for background certificate-processing work.

### Why background workers?

Bulk certificate generation should not block the HTTP request while potentially generating many PDFs.

### Why multiple workers?

Multiple workers can consume the same Redis queue concurrently, allowing the system to process many certificates more efficiently.

### Why one certificate record per recipient?

Each certificate needs its own lifecycle and failure state. This allows one recipient's failure to be recorded without stopping the other recipients.

### Why local storage initially?

The assignment can be completed and demonstrated without depending on a cloud storage service. The storage design leaves room for a later migration to S3.

## Future Improvements

Possible improvements include:

- S3/object-storage integration.
- Certificate list endpoint for frontend selection.
- Frontend dashboard for job progress.
- Download buttons for completed certificates.
- Retry support for failed certificates.
- More reliable queue acknowledgement/recovery.
- Database transactions/unit-of-work for stronger consistency.
- Atomic job counter updates for concurrent workers.
- Authentication and authorization.
- Dockerized FastAPI and worker services.
- Automated CI/CD with GitHub Actions.

## Assignment Alignment

The implementation addresses the core assignment requirements:

- Accept certificate generation requests.
- Validate recipient data.
- Generate certificates using a predefined template.
- Track generation status.
- Track job progress/results.
- Retrieve generated certificates.
- Support bulk generation.
- Allow individual certificate failures without stopping the entire job.
- Provide tests.
- Document setup, execution, API usage, and design decisions.

## Important Note

The system is intentionally structured so that the backend, worker processing, storage, and frontend can evolve independently.

The current implementation focuses on completing the core backend workflow first. Frontend, multiple worker deployment, and S3 storage can be added without changing the fundamental bulk-job model.
