# Currency Exchange

A currency exchange application built with FastAPI. The application retrieves official exchange rates from the National Bank of the Republic of Belarus (NBRB), stores them in PostgreSQL and allows users to create and manage exchange deals.

## Requirements

To run the application, you need:

- Docker
- Docker Compose (included in Docker Desktop)

No local Python or PostgreSQL installation is required.

## Configuration

Create a `.env` file in the project root directory:

```env
DEBUG=False

DB_HOST=posrgres_dev
DB_USER=postgres
DB_NAME=exchange_rates
DB_PASSWORD=postgres
DB_PORT=5432

NBRB_BASE_URL=https://api.nbrb.by

SCHEDULER_TIMEZONE=Europe/Minsk
SCHEDULER_HOUR=0
SCHEDULER_MINUTE=0

exchange_deal_expiration_minutes=1
overdue_deals_expiration_minutes=1
```

Adjust the variable names if your application settings use different names.

## Running the Application

Build and start the application:

```bash
docker compose up --build
```

Docker Compose will automatically:

1. Build the application Docker image.
2. Start the PostgreSQL container.
3. Wait until PostgreSQL is ready.
4. Apply database migrations using Alembic.
5. Start the FastAPI application.

Once started, the application will be available at:

- **Application:** [http://localhost:8000](http://localhost:8000)
- **API documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Main page:** [http://localhost:8000/exchange-deals](http://localhost:8000/exchange-deals)

## Database Migrations

Database migrations are applied automatically when the application container starts.

To apply new migrations, rebuild or restart the application:

```bash
docker compose up --build
```

## Stopping the Application

Stop containers:

```bash
docker compose down
```

PostgreSQL data is stored in a Docker volume and persists between restarts.

To remove containers and reset the database completely:

```bash
docker compose down -v
```

**Warning:** This command permanently deletes the PostgreSQL volume and all stored data.

## Running Tests

Tests run in a separate Docker environment using `docker-compose.test.yml`.

To build the test image and run the tests:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

The test environment starts its own PostgreSQL container and runs the test suite.

To remove the test containers and volumes after execution:

```bash
docker compose -f docker-compose.test.yml down -v
```
