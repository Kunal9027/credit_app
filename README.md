# Credit Approval System

A Django-based credit approval system that processes customer data and loan applications, calculates credit scores, and manages loan approvals.

## Features

- Customer registration with automatic credit limit calculation
- Loan eligibility check based on credit score
- Loan creation with validation
- View loan details
- View all loans for a customer
- Background data ingestion from Excel files

## Tech Stack

- Django 4+ with Django Rest Framework
- PostgreSQL database (Docker) / SQLite (local development)
- Celery for background tasks
- Redis as message broker
- Docker and Docker Compose for containerization

## Setup and Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized setup)
- Redis (for local development with Celery)

### Option 1: Running with Docker

1. Clone the repository
2. Place the Excel data files in the `data` directory:
   - `customer_data.xlsx`
   - `loan_data.xlsx`
3. Build and start the containers:

```bash
docker-compose up --build
```

4. The application will be available at http://localhost:8000

### Option 2: Local Development

1. Clone the repository
2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

3. Run the setup script:

```bash
python setup_local.py
```

4. Place the Excel data files in the `data` directory:
   - `customer_data.xlsx`
   - `loan_data.xlsx`

5. Start the development server:

```bash
python credit_project/manage.py runserver
```

6. The application will be available at http://localhost:8000

### Data Ingestion

#### With Docker

```bash
docker-compose exec web python credit_project/manage.py ingest_data
```

#### Local Development

```bash
python credit_project/manage.py ingest_data
```

## API Usage Examples

### Register a New Customer

```bash
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","age":30,"monthly_income":50000,"phone_number":"1234567890"}'
```

### Check Loan Eligibility

```bash
curl -X POST http://localhost:8000/check-eligibility/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"loan_amount":100000,"interest_rate":10.5,"tenure":12}'
```

### Create a Loan

```bash
curl -X POST http://localhost:8000/create-loan/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"loan_amount":100000,"interest_rate":10.5,"tenure":12}'
```

### View Loan Details

```bash
curl -X GET http://localhost:8000/view-loan/1/
```

### View Customer Loans

```bash
curl -X GET http://localhost:8000/view-loans/1/
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

- When using Docker, ensure all services are running: `docker-compose ps`
- For local development, the application will use SQLite by default

### Redis Connection Issues

For Celery to work properly in local development:

- **On Windows**: Download Redis from [Microsoft Archive Redis Releases](https://github.com/microsoftarchive/redis/releases) <mcreference link="https://github.com/microsoftarchive/redis/releases" index="0">0</mcreference>
  - Download the MSI installer (Redis-x64-3.0.504.msi is recommended)
  - Run the installer and follow the instructions
  - Redis will be installed as a Windows service that starts automatically

- **On Linux/Mac**: Install Redis using your package manager

- **Alternative for any OS**: Run Redis using Docker with our helper scripts:
  - Windows: Run `start_redis_docker.bat`
  - Linux/Mac: Run `./start_redis_docker.sh` (make it executable first with `chmod +x start_redis_docker.sh`)
  
  Or manually with:
  ```bash
  docker run -d -p 6379:6379 redis:7
  ```