---
title: "Docker Commands Cheat Sheet"
description: "A complete Docker commands cheat sheet covering containers, images, volumes, networks, and Docker Compose — quick reference for containerized development."
category: cheatsheets
template_id: cheatsheet-v2
tags: [docker, containers, devops, cheatsheet, docker-compose]
related_posts: []
related_tools: []
published_date: "2026-04-25"
og_image: "/og/cheatsheets/docker-commands-cheatsheet.png"
downloadable: true
content_type: editorial
---

# Docker Commands Cheat Sheet

Docker's CLI gives you full control over containers, images, volumes, and networks from the terminal. This cheat sheet organizes the most-used commands by task so you can find what you need without digging through docs.

## Container Lifecycle Commands

These commands cover creating, starting, stopping, and removing containers.

| Command | Description |
|---------|-------------|
| `docker run <image>` | Create and start a container from an image |
| `docker run -d <image>` | Run container in detached (background) mode |
| `docker run -it <image> bash` | Start container with interactive terminal |
| `docker run --name <name> <image>` | Assign a name to the container |
| `docker run -p 8080:80 <image>` | Map host port 8080 to container port 80 |
| `docker run -v /host:/container <image>` | Mount a host directory as a volume |
| `docker start <container>` | Start a stopped container |
| `docker stop <container>` | Gracefully stop a running container |
| `docker restart <container>` | Stop and start a container |
| `docker rm <container>` | Remove a stopped container |
| `docker rm -f <container>` | Force remove a running container |

```bash
# Run nginx on port 8080, detached, with a custom name
docker run -d --name my-nginx -p 8080:80 nginx

# Start an interactive Ubuntu shell
docker run -it ubuntu:22.04 bash

# Remove all stopped containers at once
docker container prune
```

## Container Inspection & Logs

| Command | Description |
|---------|-------------|
| `docker ps` | List running containers |
| `docker ps -a` | List all containers (including stopped) |
| `docker logs <container>` | Show container log output |
| `docker logs -f <container>` | Follow (tail) container logs in real time |
| `docker inspect <container>` | Show detailed container configuration as JSON |
| `docker stats` | Live resource usage for all running containers |
| `docker top <container>` | Show running processes inside a container |
| `docker exec -it <container> bash` | Open a shell in a running container |
| `docker cp <container>:/path /host` | Copy files from container to host |

```bash
# Follow logs for a container named "api"
docker logs -f api

# Check CPU and memory usage live
docker stats --no-stream

# Inspect a container's network settings
docker inspect my-nginx | grep -A 20 '"NetworkSettings"'
```

## Image Commands

| Command | Description |
|---------|-------------|
| `docker images` | List all local images |
| `docker pull <image>` | Download an image from Docker Hub |
| `docker push <image>` | Upload an image to a registry |
| `docker build -t <name>:<tag> .` | Build image from Dockerfile in current directory |
| `docker rmi <image>` | Remove a local image |
| `docker tag <source> <target>` | Tag an image with a new name |
| `docker image prune` | Remove all unused (dangling) images |
| `docker history <image>` | Show image layer history |
| `docker save -o file.tar <image>` | Export image to a tar archive |
| `docker load -i file.tar` | Import image from tar archive |

```bash
# Build and tag an image from the current directory
docker build -t my-app:1.0 .

# Push to Docker Hub (requires login)
docker login
docker tag my-app:1.0 username/my-app:1.0
docker push username/my-app:1.0

# Remove all unused images (safe cleanup)
docker image prune -a
```

## Volume & Network Commands

Volumes and networks are essential for persistent storage and inter-container communication.

### Volume Commands

| Command | Description |
|---------|-------------|
| `docker volume create <name>` | Create a named volume |
| `docker volume ls` | List all volumes |
| `docker volume rm <name>` | Remove a volume |
| `docker volume inspect <name>` | Show volume details |
| `docker volume prune` | Remove all unused volumes |

### Network Commands

| Command | Description |
|---------|-------------|
| `docker network create <name>` | Create a user-defined bridge network |
| `docker network ls` | List all networks |
| `docker network rm <name>` | Remove a network |
| `docker network inspect <name>` | Show network details |
| `docker network connect <net> <container>` | Connect container to a network |
| `docker network disconnect <net> <container>` | Disconnect container from a network |

```bash
# Create a network and run two containers on it
docker network create app-net
docker run -d --name db --network app-net postgres:15
docker run -d --name api --network app-net my-api:latest

# The "api" container can reach "db" by hostname
```

## Docker Compose Commands

Docker Compose manages multi-container applications defined in `docker-compose.yml`.

| Command | Description |
|---------|-------------|
| `docker compose up` | Create and start all services |
| `docker compose up -d` | Start services in detached mode |
| `docker compose down` | Stop and remove containers + networks |
| `docker compose down -v` | Also remove volumes |
| `docker compose ps` | List compose service containers |
| `docker compose logs -f` | Follow logs for all services |
| `docker compose exec <svc> bash` | Open shell in a running service |
| `docker compose build` | Rebuild all service images |
| `docker compose pull` | Pull latest images for all services |
| `docker compose restart <svc>` | Restart a specific service |
| `docker compose config` | Validate and display the compose config |

```yaml
# Minimal docker-compose.yml example
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```bash
# Start the stack, rebuild if source changed
docker compose up -d --build

# Tail logs for just the web service
docker compose logs -f web
```

## System & Cleanup Commands

| Command | Description |
|---------|-------------|
| `docker system df` | Show disk usage by Docker objects |
| `docker system prune` | Remove all unused objects (safe) |
| `docker system prune -a` | Remove all unused objects including unused images |
| `docker info` | Display system-wide Docker information |
| `docker version` | Show Docker client and daemon version |
| `docker events` | Stream real-time events from the daemon |

```bash
# See how much disk Docker is using
docker system df

# Full cleanup: remove stopped containers, unused networks, dangling images
docker system prune

# Nuclear option: also removes all unused images
docker system prune -a --volumes
```

## Useful run Flags Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--detach` | `-d` | Run in background |
| `--interactive --tty` | `-it` | Interactive shell |
| `--publish` | `-p` | Port mapping `host:container` |
| `--volume` | `-v` | Bind mount or named volume |
| `--env` | `-e` | Set environment variable |
| `--env-file` | | Load env vars from file |
| `--network` | | Connect to a specific network |
| `--rm` | | Auto-remove container on exit |
| `--restart` | | Restart policy (`always`, `unless-stopped`) |
| `--memory` | `-m` | Memory limit (e.g. `512m`) |
| `--cpus` | | CPU limit (e.g. `1.5`) |

For a deeper look at container orchestration patterns, check the [DevNook guides hub](/guides/). If you work with version control alongside Docker, the [Git Commands Cheat Sheet](/cheatsheets/git-commands-cheatsheet) pairs well with this reference. Browse all quick-reference cards on the [cheatsheets hub](/cheatsheets/).

Docker commands become second nature with regular use. The table above covers the full lifecycle — from `docker run` to `docker system prune` — so keep it bookmarked for your daily containerized development workflow. For tools that complement your Docker setup, visit [DevNook tools](/tools/).
