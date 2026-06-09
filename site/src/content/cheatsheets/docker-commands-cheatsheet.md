---
title: "Docker Commands Cheat Sheet"
description: "Complete docker commands cheatsheet covering docker run, Dockerfile, containers, images, volumes, networks, and Docker Compose for every stage of development."
category: cheatsheets
template_id: cheatsheet-v2
tags: [docker, containers, devops, cheatsheet, docker-compose]
related_posts: []
related_tools: []
published_date: "2026-06-09"
og_image: "/og/cheatsheets/docker-commands-cheatsheet.png"
downloadable: true
---

Docker's CLI gives you full control over containers, images, volumes, and networks from the terminal. This docker commands cheatsheet organizes the complete commands list by task — from your first `docker run` through multi-service Compose stacks and Dockerfile authoring — so you can find what you need without digging through docs.

## Quick-Start Docker Tutorial

New to Docker? These commands take you from zero to a running container in under two minutes.

| Step | Command | What It Does |
|------|---------|--------------|
| 1 | `docker version` | Confirm Docker is installed and the daemon is running |
| 2 | `docker pull nginx:latest` | Download the official NGINX image from Docker Hub |
| 3 | `docker run -d --name my-nginx -p 8080:80 nginx` | Start NGINX in the background, map port 8080 |
| 4 | `docker ps` | Confirm the container is running |
| 5 | `docker stop my-nginx` | Stop the container gracefully |
| 6 | `docker rm my-nginx` | Remove the stopped container |

```bash
docker pull nginx:latest
docker run -d --name my-nginx -p 8080:80 nginx
docker ps
docker stop my-nginx && docker rm my-nginx
```

That is the entire container lifecycle in six steps. Visit `http://localhost:8080` after step 3 — NGINX welcome page confirms it is running. The sections below cover every flag, variation, and related command.

## docker run Commands and Flags

`docker run` creates a new container from an image and starts it immediately. It is the single most-used entry in any docker commands list. Full syntax: `docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`.

| Flag | Short | What It Does |
|------|-------|--------------|
| `--detach` | `-d` | Run the container in the background |
| `--interactive --tty` | `-it` | Attach an interactive pseudo-TTY |
| `--name <name>` | | Assign a readable name to the container |
| `--publish <host>:<ctr>` | `-p` | Map host port to container port |
| `--publish-all` | `-P` | Map all EXPOSE'd ports to random host ports |
| `--volume <host>:<ctr>` | `-v` | Bind-mount a host path or named volume |
| `--mount` | | Explicit mount syntax (preferred in scripts) |
| `--env <KEY>=<val>` | `-e` | Set a single environment variable |
| `--env-file <file>` | | Load environment variables from a file |
| `--network <name>` | | Attach the container to a specific network |
| `--rm` | | Auto-remove the container on exit |
| `--restart <policy>` | | `no`, `always`, `unless-stopped`, `on-failure[:n]` |
| `--memory <limit>` | `-m` | Memory limit, e.g. `512m` or `2g` |
| `--cpus <n>` | | CPU quota, e.g. `1.5` for 1.5 cores |
| `--user <uid>` | `-u` | Run as a specific user or UID |
| `--workdir <path>` | `-w` | Set the working directory inside the container |
| `--entrypoint <cmd>` | | Override the image ENTRYPOINT |
| `--hostname <name>` | `-h` | Set the container hostname |
| `--add-host <host>:<ip>` | | Add a custom entry to /etc/hosts |
| `--read-only` | | Mount root filesystem as read-only |
| `--init` | | Use a minimal init process as PID 1 |

```bash
docker run --rm \
  -e NODE_ENV=production \
  --env-file .env.production \
  -v "$(pwd)/app":/usr/src/app \
  -w /usr/src/app \
  -p 3000:3000 \
  --memory 512m \
  --cpus 1 \
  node:20-alpine npm start
```

One-off Python script — container disappears on exit:

```bash
docker run --rm -it python:3.12-slim python
docker run --rm -v "$(pwd)":/work -w /work python:3.12-slim python migrate.py
```

Full flag reference: [https://docs.docker.com/engine/reference/run/](https://docs.docker.com/engine/reference/run/)

## Container Lifecycle Commands

These commands manage the full lifecycle from creation to deletion.

| Command | What It Does |
|---------|--------------|
| `docker create <image>` | Create a container without starting it |
| `docker start <container>` | Start a stopped container |
| `docker stop <container>` | Send SIGTERM, wait, then SIGKILL |
| `docker stop -t 60 <container>` | Override the 10-second kill timeout |
| `docker kill <container>` | Send SIGKILL immediately |
| `docker kill -s SIGHUP <container>` | Send SIGHUP to reload config |
| `docker restart <container>` | Stop then start |
| `docker pause <container>` | Freeze all processes in the container |
| `docker unpause <container>` | Resume a paused container |
| `docker rm <container>` | Remove a stopped container |
| `docker rm -f <container>` | Force-remove a running container |
| `docker rename <old> <new>` | Rename a container |
| `docker update --memory 2g <container>` | Adjust resource limits without restarting |
| `docker wait <container>` | Block until exit, print exit code |
| `docker container prune` | Remove all stopped containers |

```bash
docker stop --time 60 my-app
docker rm my-app
docker container prune --force
docker wait my-batch-job
```

## Container Inspection and Logs

Monitor what is happening inside running containers without attaching to them directly.

| Command | What It Does |
|---------|--------------|
| `docker ps` | List running containers |
| `docker ps -a` | Include stopped containers |
| `docker ps -q` | Print only container IDs (pipe-friendly) |
| `docker logs <container>` | Print all log output |
| `docker logs -f <container>` | Stream logs in real time |
| `docker logs --tail 200 <container>` | Last 200 lines only |
| `docker logs --since 2h <container>` | Logs from the past 2 hours |
| `docker inspect <container>` | Full JSON configuration and state |
| `docker stats` | Live CPU, memory, and I/O for all running containers |
| `docker stats --no-stream` | One-shot resource snapshot |
| `docker top <container>` | Processes running inside the container |
| `docker exec -it <container> bash` | Open an interactive shell |
| `docker exec <container> <command>` | Run a command non-interactively |
| `docker cp <container>:/path /host/path` | Copy files from container to host |
| `docker cp /host/file <container>:/path` | Copy files from host to container |
| `docker diff <container>` | Show filesystem changes since start |
| `docker port <container>` | List all port mappings |

```bash
docker logs -f --timestamps api
docker exec my-db psql -U postgres -c "SELECT COUNT(*) FROM users;"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
docker inspect my-app --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
```

## Docker Image Commands

Images are read-only templates that containers run from. Every `docker build` produces a layered image stored locally.

| Command | What It Does |
|---------|--------------|
| `docker images` | List all local images |
| `docker images -a` | Include intermediate layer images |
| `docker images --filter dangling=true` | List only untagged images |
| `docker pull <image>:<tag>` | Download from Docker Hub or a private registry |
| `docker push <image>:<tag>` | Upload to a registry |
| `docker build -t <name>:<tag> .` | Build image from Dockerfile in current directory |
| `docker build -f <file> -t <name>:<tag> .` | Use a specific Dockerfile path |
| `docker build --no-cache -t <name>:<tag> .` | Rebuild every layer without cache |
| `docker build --target <stage> -t <name> .` | Build only up to a named stage |
| `docker rmi <image>` | Remove a local image |
| `docker rmi -f <image>` | Force-remove even if referenced by a container |
| `docker tag <source> <target>` | Create an additional tag or alias |
| `docker image prune` | Remove dangling (untagged) images |
| `docker image prune -a` | Remove all images not used by any container |
| `docker history <image>` | Layer-by-layer history and sizes |
| `docker save -o archive.tar <image>` | Export image to a tar archive |
| `docker load -i archive.tar` | Import image from a tar archive |
| `docker inspect <image>` | Full image metadata as JSON |

```bash
docker build -t my-api:3.0 .
docker tag my-api:3.0 username/my-api:3.0
docker tag my-api:3.0 username/my-api:latest
docker login
docker push username/my-api:3.0 && docker push username/my-api:latest
docker image prune -a --filter "until=72h" --force
```

## Dockerfile Instructions Reference

A Dockerfile is the script that defines how a docker image is built — each instruction creates a cached layer. Writing a well-structured dockerfile is the foundation of a lean, reproducible container image.

| Instruction | What It Does |
|-------------|--------------|
| `FROM <image>:<tag>` | Base image — every Dockerfile must start here |
| `FROM <image> AS <stage>` | Named stage for multi-stage builds |
| `WORKDIR <path>` | Set working directory; creates it if absent |
| `COPY <src> <dest>` | Copy files from build context into the image |
| `COPY --from=<stage> <src> <dst>` | Copy from a previous named build stage |
| `ADD <src> <dest>` | Like COPY, but also unpacks .tar archives and fetches URLs |
| `RUN <command>` | Execute a shell command and commit the result as a layer |
| `RUN ["exe", "arg"]` | Exec form — no shell expansion; preferred for clarity |
| `CMD ["exe", "arg"]` | Default command when running the container (overridable) |
| `ENTRYPOINT ["exe"]` | Fixed executable; CMD becomes its default arguments |
| `ENV <KEY>=<value>` | Set a persistent environment variable |
| `ARG <name>=<default>` | Build-time variable not baked into the final image |
| `EXPOSE <port>` | Document the port the application listens on |
| `VOLUME ["/data"]` | Declare a mount point for an external volume |
| `USER <user>` | Switch to a non-root user from this point forward |
| `HEALTHCHECK CMD <cmd>` | Define a container health probe |
| `LABEL <key>=<value>` | Attach metadata key-value pairs to the image |
| `SHELL ["exe", "flags"]` | Override the default shell for subsequent RUN instructions |
| `STOPSIGNAL <signal>` | Signal used to stop the container (default SIGTERM) |
| `ONBUILD <instruction>` | Trigger when this image is used as a base |

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
EXPOSE 3000
USER node
HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

The three-stage build discards all build tooling from the final image. Only compiled output and production `node_modules` are copied into the `runner` stage, keeping the image small and the attack surface minimal. Use `docker build --target deps .` to build only through the first stage.

## Volume and Network Commands

Volumes provide persistent storage independent of container lifecycles. Networks control how containers discover and communicate with each other.

### Volume Commands

| Command | What It Does |
|---------|--------------|
| `docker volume create <name>` | Create a named volume |
| `docker volume ls` | List all volumes |
| `docker volume ls --filter dangling=true` | Volumes not used by any container |
| `docker volume rm <name>` | Remove a volume (must be unused) |
| `docker volume inspect <name>` | Show mountpoint, driver, and labels |
| `docker volume prune` | Remove all unused volumes |

### Network Commands

| Command | What It Does |
|---------|--------------|
| `docker network create <name>` | Create a user-defined bridge network |
| `docker network create --driver overlay <name>` | Overlay network for Docker Swarm |
| `docker network create --subnet 172.20.0.0/16 <name>` | Custom subnet |
| `docker network ls` | List all networks |
| `docker network rm <name>` | Remove a network |
| `docker network inspect <name>` | Show subnet, gateway, and connected containers |
| `docker network connect <net> <container>` | Attach a running container to a network |
| `docker network disconnect <net> <container>` | Detach a container from a network |
| `docker network prune` | Remove all unused networks |

```bash
docker network create app-net
docker run -d --name db \
  --network app-net \
  -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16
docker run -d --name api \
  --network app-net \
  -e DATABASE_URL=postgres://postgres:secret@db/app \
  -p 8080:8080 \
  my-api:latest
```

Containers on the same network reach each other by container name — no IP addresses required. The `api` container resolves `db` automatically.

## Docker Compose Commands

Docker Compose manages multi-service stacks defined in `compose.yml` (or `docker-compose.yml`). Official reference: [https://docs.docker.com/compose/reference/](https://docs.docker.com/compose/reference/).

| Command | What It Does |
|---------|--------------|
| `docker compose up` | Create and start all services |
| `docker compose up -d` | Start in detached mode |
| `docker compose up --build` | Rebuild images before starting |
| `docker compose up --force-recreate` | Recreate containers even if config is unchanged |
| `docker compose down` | Stop and remove containers and networks |
| `docker compose down -v` | Also remove named volumes |
| `docker compose down --rmi all` | Also remove images built by Compose |
| `docker compose ps` | Status of all service containers |
| `docker compose logs -f` | Stream logs for all services |
| `docker compose logs -f <service>` | Stream logs for a single service |
| `docker compose exec <svc> bash` | Shell into a running service container |
| `docker compose run --rm <svc> <cmd>` | Run a one-off command in a fresh container |
| `docker compose build` | Rebuild all service images |
| `docker compose build --no-cache` | Rebuild without layer cache |
| `docker compose pull` | Pull latest images for all services |
| `docker compose push` | Push built images to their registries |
| `docker compose restart <svc>` | Restart a specific service |
| `docker compose stop` | Stop services without removing them |
| `docker compose start` | Start previously stopped services |
| `docker compose config` | Validate and print the resolved configuration |
| `docker compose top` | Processes running in each service container |
| `docker compose scale <svc>=<n>` | Scale a service to N replicas |

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://postgres:secret@db/myapp
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

```bash
docker compose up -d --build
docker compose run --rm web python manage.py migrate
docker compose logs -f web
docker compose scale worker=4
```

For deeper debugging of service output, the [Docker Compose Logs guide](/guides/docker-compose-logs/) covers filtering, timestamps, and per-service log redirection.

## System and Cleanup Commands

| Command | What It Does |
|---------|--------------|
| `docker system df` | Disk usage by images, containers, volumes, and build cache |
| `docker system df -v` | Verbose per-object breakdown |
| `docker system prune` | Remove stopped containers, unused networks, dangling images |
| `docker system prune -a` | Also remove all unused images |
| `docker system prune -a --volumes` | Full cleanup including unused volumes |
| `docker system prune --filter "until=48h"` | Only remove objects older than 48 hours |
| `docker info` | System-wide configuration, storage driver, runtime |
| `docker version` | Client and daemon version numbers |
| `docker events` | Real-time event stream from the Docker daemon |
| `docker events --filter type=container` | Filter to container events only |
| `docker builder prune` | Remove unused build cache |
| `docker builder prune -a` | Remove all build cache |

```bash
docker system df
docker container prune --force && docker image prune --force
docker builder prune --filter "until=24h" --force
docker system prune -a --volumes --force
```

Keep this docker cheatsheet alongside the [Linux Commands Cheat Sheet](/cheatsheets/linux-commands-cheatsheet/) and the [Git Commands Cheat Sheet](/cheatsheets/git-commands-cheatsheet/) — together they cover most daily terminal work. The [curl Command guide](/guides/curl-command-guide/) pairs well for testing container HTTP endpoints once services are running.
