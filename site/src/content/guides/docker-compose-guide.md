---
title: "Docker Compose Orchestration: Recipes and Patterns"
description: "Master docker compose up, scaling, health checks, and orchestration recipes. A practical guide for running containerized services in development and beyond."
category: guides
subcategory: "DevOps & Infrastructure"
template_id: guide-v2
tags: [docker, docker-compose, devops, containers, orchestration]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-07-05"
og_image: "/og/guides/docker-compose-guide.png"
actual_word_count: 2513
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["Article", "FAQPage"],
    "headline": "Docker Compose Orchestration: Recipes and Patterns",
    "description": "Master docker compose up, scaling, health checks, and orchestration recipes. A practical guide for running containerized services in development and beyond.",
    "datePublished": "2026-07-05",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/guides/docker-compose-guide/",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between docker compose up and docker compose start?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "docker compose up creates and starts containers, pulling or building images as needed. docker compose start only starts containers that already exist in a stopped state. Use up to bring a stack online from zero, and start/stop to pause and resume without recreating containers."
        }
      },
      {
        "@type": "Question",
        "name": "How do I run a one-off command inside a Compose service?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Use docker compose run --rm service-name command. The --rm flag removes the container after the command exits. This is the standard approach for database migrations, seed scripts, and other one-time administrative tasks."
        }
      },
      {
        "@type": "Question",
        "name": "What happens to data when I run docker compose down?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "docker compose down stops and removes containers and networks but leaves named volumes in place by default. Your database data and persisted files survive across down/up cycles. Add --volumes to also remove named volumes and wipe persisted data."
        }
      },
      {
        "@type": "Question",
        "name": "How do I limit memory or CPU for a Compose service?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Use the deploy.resources key under the service definition. Set limits.cpus and limits.memory to cap usage. This prevents a single service from consuming all available resources on a shared development machine."
        }
      },
      {
        "@type": "Question",
        "name": "How do I check which version of Docker Compose is installed?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Run docker compose version. The modern Docker Compose is a CLI plugin for Docker, invoked as docker compose without a hyphen. The legacy standalone binary is docker-compose with a hyphen. The plugin version ships with Docker Desktop and is actively maintained."
        }
      }
    ]
  }
  </script>
---

Running a single Docker container is straightforward. Running five services that depend on each other — a web app, a database, a cache, a message queue, and a reverse proxy — is where `docker compose up` earns its place in every developer's toolkit. One command, one file, and your entire environment is live.

## How docker compose up Starts Your Services

`docker compose up` reads a `docker-compose.yml` file in the current directory and starts all defined services. The command works through a predictable sequence: it pulls or builds any missing images, creates the shared network, creates named volumes if they do not exist, then starts each container.

The most useful flags to know:

| Flag | What it does |
|------|-------------|
| `-d` / `--detach` | Run containers in the background, return the terminal immediately |
| `--build` | Force image rebuilds before starting |
| `--force-recreate` | Recreate containers even when configuration has not changed |
| `--remove-orphans` | Stop containers for services no longer defined in the compose file |
| `--no-deps` | Start a single service without also starting its dependencies |

Starting the stack without `-d` streams all service logs directly to your terminal. This is useful for initial debugging — you see everything immediately — but impractical for day-to-day work. In practice, `docker compose up -d` is what most teams use.

To restart a single service without touching the rest of the stack:

```bash
docker compose up -d --no-deps web
```

The `--no-deps` flag prevents Compose from also restarting `db` or other services `web` depends on. This is the fastest way to pick up a code change in one service while keeping everything else running.

## Writing a docker-compose.yml That Actually Works

The Compose file defines your services, their images or build contexts, port mappings, environment variables, volumes, and startup dependencies. A minimal working setup — a Node.js application connected to PostgreSQL:

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://dev:password@db:5432/myapp
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run `docker compose up -d` and both services start. The `app` service waits for the `db` container to be running before it starts. The named volume `postgres_data` persists database files between container restarts and across `docker compose down` and `up` cycles.

Two things to note here. First, `image: postgres:16` pins a specific major version rather than using `latest`. Pinning the image prevents silent breakage when a new release ships with API changes. Second, `build: .` tells Compose to build from the `Dockerfile` in the current directory. For more control, use `context` and `dockerfile` keys to point to a specific build path.

For a complete reference of Docker CLI commands that complement Compose, the [Docker commands cheat sheet](/cheatsheets/docker-commands-cheatsheet/) covers the essentials.

## Core Orchestration Recipes

### Three-Tier Stack: Web, Database, Cache

Most web applications need at minimum a web server, a relational database, and a cache layer. Here is a working three-tier setup with a Python application, PostgreSQL, and Redis:

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://app:secret@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

The `condition: service_healthy` on the `postgres` dependency is the critical difference from a basic `depends_on`. It instructs Compose to hold the `web` container in a waiting state until the health check on `postgres` actually passes — not just until the container starts. Redis uses `service_started` because it initialises quickly and no health check is defined for it.

### Network Isolation Between Services

By default, all services in a Compose file share a single automatically created network. Every service can reach every other service by its service name as the hostname — `postgres:5432`, `redis:6379`, and so on. For most development stacks, this is exactly what you want.

For more complex projects — say, a microservices setup where the frontend should reach the API gateway but not the database directly — you can define multiple named networks:

```yaml
services:
  frontend:
    image: nginx:alpine
    networks:
      - public

  api:
    build: ./api
    networks:
      - public
      - internal

  db:
    image: postgres:16
    networks:
      - internal

networks:
  public:
  internal:
```

The `frontend` service can reach `api` but has no route to `db`. The `api` service bridges both networks and acts as the gateway to the database tier. This mirrors your production network topology in local development, catching access control bugs before they reach a staging environment.

Docker's [Compose networking documentation](https://docs.docker.com/compose/networking/) covers DNS resolution, network drivers, and how Compose assigns container hostnames in detail.

### Web App with Background Workers

Compose handles background workers cleanly when they share the same codebase as the main application. A Django app with Celery workers:

```yaml
services:
  web:
    build: .
    command: gunicorn myapp.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - db

  worker:
    build: .
    command: celery -A myapp worker --loglevel=info --concurrency=2
    depends_on:
      - redis
      - db

  beat:
    build: .
    command: celery -A myapp beat --loglevel=info
    depends_on:
      - redis

  redis:
    image: redis:7-alpine

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=dev_password
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

All three application services — `web`, `worker`, and `beat` — reference `build: .` and share the same built image. Compose builds it once and starts three containers from it, each running a different command. When the application code changes, a single `docker compose up -d --build` propagates the new image to all three services.

## Health Checks and Service Readiness

`depends_on` controls startup order but only waits for a service to be *running*, not *ready*. A PostgreSQL container reports as running for several seconds before it accepts TCP connections. If your application tries to connect during that window, it fails with a connection refused error.

Health checks close this gap:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

The `start_period` key deserves attention. It sets a grace period during which health check failures do not count against the retry limit. For services that run schema migrations or data loading on first startup — which can take 10–20 seconds — this prevents premature "unhealthy" status marking before the service has had a chance to finish initialising.

Common health check commands by service type:

| Service | Health check command |
|---------|---------------------|
| PostgreSQL | `pg_isready -U user -d dbname` |
| MySQL / MariaDB | `mysqladmin ping -h localhost -u user --password=pass` |
| Redis | `redis-cli ping` |
| HTTP service | `curl -sf http://localhost:8080/health` |
| MongoDB | `mongosh --eval "db.adminCommand('ping')"` |
| RabbitMQ | `rabbitmq-diagnostics check_port_connectivity` |

Once a service declares a health check, downstream services can use `condition: service_healthy` in their `depends_on` block. This is the correct way to enforce readiness-based startup order in Compose.

For monitoring running containers and reading structured output after startup, the [Docker Compose Logs guide](/guides/docker-compose-logs/) covers `docker compose logs`, filtering by service name, and following log streams across a full stack.

## Scaling Services with docker compose up --scale

Compose supports horizontal scaling for stateless services using the `--scale` flag:

```bash
docker compose up -d --scale web=3
```

This starts three instances of the `web` service. Compose names them `project-web-1`, `project-web-2`, and `project-web-3` and attaches all three to the same internal network. Other services reach the pool using the `web` service name — Compose's internal DNS round-robins across all matching containers.

Port bindings require adjustment when scaling. Mapping three containers to the same host port causes an error. Either remove the `ports` binding from the scalable service, or use a port range:

```yaml
services:
  web:
    build: .
    ports:
      - "3000-3002:3000"   # maps to host ports 3000, 3001, 3002 respectively
```

The cleaner pattern is a reverse proxy in front of the scaled pool:

```yaml
services:
  proxy:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web

  web:
    build: .
    # No host port binding — traffic arrives only through the proxy
```

Nginx resolves the `web` upstream name to all running containers and load-balances requests across them. The proxy exposes only port 80 to the host.

The `--scale` flag works well for local load testing and CI environments where you want to reproduce multi-instance behaviour before deploying. For production-grade scaling with persistent storage, rolling deployments, and resource guarantees, Kubernetes handles requirements that Compose does not cover.

## Environment Variables and Override Files

### Using .env Files

Compose automatically reads a `.env` file in the same directory as `docker-compose.yml`. Variables defined there become available as substitutions throughout the Compose file:

```
POSTGRES_PASSWORD=dev_only_secret
APP_PORT=8000
NODE_ENV=development
```

```yaml
services:
  app:
    build: .
    ports:
      - "${APP_PORT}:8000"
    environment:
      - NODE_ENV=${NODE_ENV}

  db:
    image: postgres:16
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

The `.env` file belongs in `.gitignore`. Commit a `.env.example` file with placeholder values instead — this gives new team members a clear template without exposing credentials.

Compose supports default-value syntax for substitutions: `${VAR:-default}` uses `default` if `VAR` is unset or empty. This is useful for variables with sensible development defaults that still need explicit overrides in production. For example, `${APP_PORT:-8000}` runs on port 8000 unless the environment sets it otherwise. The stricter form `${VAR:?error message}` makes Compose exit immediately with an error when a required variable is not defined, catching missing configuration before a container starts.

### The env_file Option

When a service needs many environment variables, `env_file` is cleaner than a long `environment` block:

```yaml
services:
  app:
    build: .
    env_file:
      - .env
      - .env.local
```

Multiple files apply in order — later entries override earlier ones. `.env.local` is a common convention for developer-specific overrides. Both files feed into the container's environment at startup.

### Override Files for Multiple Environments

Compose merges multiple files when you pass them with `-f`:

```bash
docker compose up -d

docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d

docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

`docker-compose.override.yml` is handled specially: Compose merges it with `docker-compose.yml` automatically when the file exists in the same directory, with no `-f` flags required. This makes it the right place for development-only additions — volume mounts for live code reloading, debug ports, or relaxed memory limits — that should never reach production.

```yaml
services:
  app:
    volumes:
      - .:/app                         ports:
      - "9229:9229"                    environment:
      - DEBUG=true
```

When reviewing how configuration differs between environments before a deployment, a [diff viewer](/tools/diff-viewer/) makes it easy to confirm that the production override only changes what you intend.

## Validating and Inspecting Your Compose Stack

Before running `docker compose up`, validate the merged configuration with all substitutions applied:

```bash
docker compose config
```

This prints the fully resolved Compose file — variable substitutions applied, override files merged, defaults filled in. A YAML syntax error or an undefined variable shows up here rather than as a cryptic runtime failure. Running this before every production deploy is a low-cost safety habit.

Useful companion commands:

```bash
docker compose config --services   # list all service names
docker compose config --volumes    # list named volumes in the stack
docker compose ps                  # show running containers and port bindings
docker compose top                 # show processes running inside each container
```

In CI pipelines, `docker compose config --quiet` exits with a non-zero status on any error but produces no output on success — a clean lint step. The [GitHub Actions guide](/blog/github-actions-guide-status-checkout-runners/) shows how to wire validation steps alongside checkout actions and test runners in an automated pipeline.

## Frequently Asked Questions

### What is the difference between docker compose up and docker compose start?

`docker compose up` creates and starts containers, pulling or building images if needed. `docker compose start` only starts containers that already exist in a stopped state — it will not create them if they are absent. Use `docker compose up` to bring a stack online from zero. Use `start` and `stop` to pause and resume a stack you have already created, without recreating or reconfiguring any containers.

### How do I run a one-off command inside a Compose service?

Use `docker compose run` rather than `docker compose up`:

```bash
docker compose run --rm app python manage.py migrate
docker compose run --rm app rake db:seed
```

The `--rm` flag removes the container when the command exits, keeping your container list clean. The new container starts with all configured environment variables, attaches to the same named volumes, and connects to the same networks as the running stack. This is the standard pattern for database migrations, seed scripts, and administrative tasks that need the full application environment but should not run as a long-lived service.

### What happens to data when I run docker compose down?

`docker compose down` stops and removes containers and networks, but leaves named volumes in place by default. Your database data, uploaded files, and other persisted state survive across `down`/`up` cycles. To also remove named volumes and wipe all persisted data, add the `--volumes` flag:

```bash
docker compose down --volumes
```

Use `docker compose down --volumes` when you want a fully clean state — typically before testing a fresh install flow or between unrelated test runs. Avoid it as a routine teardown command, or you will lose your local development data every time.

### How do I limit memory or CPU for a Compose service?

Use the `deploy.resources` key under the service definition:

```yaml
services:
  app:
    build: .
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          memory: 256M
```

The `limits` keys cap the maximum resources the container can use. The `reservations` keys define a minimum guaranteed allocation. This prevents a single service from consuming all available memory on a development machine, which matters when running several projects simultaneously.

### How do I check which version of Docker Compose is installed?

```bash
docker compose version
```

The modern Docker Compose is a CLI plugin for Docker, invoked as `docker compose` (two words, no hyphen). It ships with Docker Desktop and is the actively maintained version. The legacy standalone binary is `docker-compose` with a hyphen — it still works but receives no new features. If `docker compose version` fails, check whether the plugin is enabled in Docker Desktop settings under the CLI tools section.

## Conclusion

`docker compose up` is the control point for your entire local development environment. The patterns here — health-checked dependencies with `condition: service_healthy`, named networks for service isolation, environment-specific override files, and horizontal scaling with `--scale` — cover the orchestration problems that come up repeatedly in real projects.

Two places to go next: the [Docker Compose Logs guide](/guides/docker-compose-logs/) for managing structured log output across multi-container stacks, and the [Bash cheat sheet](/cheatsheets/bash-commands-cheatsheet/) for the shell scripting patterns that complement Compose in CI workflows. The [official Docker Compose documentation](https://docs.docker.com/compose/) is the authoritative reference for any compose file key not covered here, and the [Compose file specification](https://docs.docker.com/compose/compose-file/) documents every field with full examples.
