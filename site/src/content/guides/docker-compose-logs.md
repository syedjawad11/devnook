---
title: "Docker Compose Logs: How to View and Debug Container Output"
description: "View and debug container output with docker compose logs. Learn every flag, filter by service, follow live output, and troubleshoot container crashes."
category: guides
subcategory: "DevOps & Infrastructure"
template_id: blog-v5
tags: [docker, docker-compose, debugging, devops, containers]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-06-02"
og_image: "/og/guides/docker-compose-logs.png"
actual_word_count: 2779
schema_org: "<script type=\"application/ld+json\">\n{\"@context\":\"https://schema.org\",\"@type\":[\"BlogPosting\",\"FAQPage\"],\"headline\":\"Docker Compose Logs: How to View and Debug Container Output\",\"description\":\"View and debug container output with docker compose logs. Learn every flag, filter by service, follow live output, and troubleshoot container crashes.\",\"datePublished\":\"2026-06-02\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/guides/docker-compose-logs\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"How do I view logs for a specific service in Docker Compose?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Append the service name after the command: docker compose logs api. Add --follow to stream live output in real time, or --tail=N to limit output to the last N lines.\"}},{\"@type\":\"Question\",\"name\":\"Can I view logs from a stopped or crashed container with Docker Compose?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Yes. docker compose logs works on stopped and exited containers. Log output is preserved until you run docker compose down or docker compose rm.\"}},{\"@type\":\"Question\",\"name\":\"Why does docker compose logs not show output from my service?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"The most common reason is the service writes logs to a file instead of stdout and stderr. Docker only captures stdout and stderr. Configure your application to write logs there, or check if a non-default logging driver is configured.\"}}]}\n</script>"
---

When a containerized service crashes silently, fails to start, or loses a database connection, `docker compose logs` is the first command to reach for. Every container in a Compose stack writes to stdout and stderr — Docker captures that output automatically, and `docker compose logs` surfaces it with controls for filtering by service, following live output, and limiting how many lines you see.

This guide covers every practical flag and usage pattern: viewing logs for a single service, adding timestamps, following output in real time, and reading container output after a crash.

## What docker compose logs Actually Does

Docker attaches to each container's stdout and stderr streams at startup and routes that output through a logging driver. The default driver is `json-file`, which stores each log line as a JSON entry on the host filesystem — typically under `/var/lib/docker/containers/<container-id>/`.

When you run `docker compose logs`, Docker reads those stored entries and prints them to your terminal. Each line is prefixed with the service name and a replica number:

```
api-1      | [2026-06-01 09:42:13] INFO  Starting server on port 3000
db-1       | LOG:  database system is ready to accept connections
redis-1    | * Ready to accept connections tcp
```

The service name comes from your `docker-compose.yml`. The replica number increments when you scale a service (`api-1`, `api-2`, and so on). In terminals that support ANSI colors, each service name gets a distinct color — which makes multi-service output easier to scan at a glance.

The key difference from `docker logs <container-id>` is that `docker compose logs` works with service names — the logical names you define in your Compose file — rather than container IDs. It also understands your project's service graph, so you can reference multiple services together without looking up IDs first.

The official [Docker Compose logs reference](https://docs.docker.com/reference/cli/docker/compose/logs/) lists the complete flag set.

## Viewing Logs for Specific Services

Without any arguments, `docker compose logs` dumps all output from all services since the containers started. In a stack with several services that have been running for hours, that output can span thousands of lines. Start with a specific service instead:

```bash
docker compose logs api
docker compose logs db
```

Append the service name exactly as it appears in your `docker-compose.yml`. To view multiple services at once, list them:

```bash
docker compose logs api db
```

This is useful when you suspect an interaction between services — for example, an API crash caused by a database that wasn't ready when the application attempted its first connection. Watching both services side by side reveals the timing of events across the startup sequence.

### Limiting Output with --tail

The `--tail` flag limits output to the last N lines per container:

```bash
docker compose logs --tail=50 api
```

Without `--tail`, you get every line since the container started. The `--tail` flag applies per container, not per service in aggregate. If you have three replicas of `api`, `--tail=50` gives you up to 50 lines from each replica, not 50 lines total across all three.

Combine service filtering with a tail limit for the most focused output:

```bash
docker compose logs --tail=100 api db
```

This is the typical starting point when you know which services are involved in a problem but want to avoid scrolling through hours of output.

### Ordering in Multi-Service Output

When you view multiple services simultaneously, log lines are interleaved in the order Docker delivers them. Lines from `api` and `db` may appear slightly out of sequence due to per-container buffering — Docker doesn't wait for a timestamp comparison before printing. If precise ordering matters for your debugging, add `--timestamps` to include Docker's recorded timestamp on each line, then sort the output offline.

## Following Live Output and Reading Timestamps

### The --follow Flag

The `--follow` flag (short form: `-f`) keeps `docker compose logs` running and streams new lines as containers produce them:

```bash
docker compose logs --follow api
```

Press `Ctrl+C` to stop following. The containers keep running — you're detaching from the log stream, not stopping the service.

To see only new output without any historical lines, combine `--follow` with `--tail=0`:

```bash
docker compose logs --follow --tail=0 api
```

`--tail=0` skips all stored output and shows only lines produced after the command runs. This is the cleanest setup when you've just restarted a service and want to watch it initialize without scrolling through output from previous runs.

Following is particularly useful during:

- **Service startup** — watch the initialization sequence in real time and see exactly where a service hangs or exits.
- **Request debugging** — tail the API log while sending test requests with curl or your HTTP client.
- **Database migration** — follow the database container while a migration runs to confirm it completes without errors.

### The --timestamps Flag

Docker records a timestamp for every log entry it captures. By default, `docker compose logs` omits these — it prints whatever the container wrote to stdout, verbatim. The `--timestamps` flag (short form: `-t`) adds Docker's recorded time:

```bash
docker compose logs --timestamps api
```

Output with timestamps:

```
api-1      | 2026-06-01T10:01:04.312476500Z [INFO] Server started on port 3000
db-1       | 2026-06-01T10:01:03.901234500Z LOG:  database system is ready to accept connections
```

Timestamps are in UTC, formatted as RFC 3339. In the example above, the database became ready at `10:01:03` and the API started at `10:01:04` — a healthy startup sequence. If those timestamps were reversed (API starts before the database is ready), you've just confirmed a race condition.

Timestamps are especially valuable when your application doesn't log its own times, or logs in a local timezone rather than UTC. Docker's `--timestamps` provides consistent UTC timing across all services without requiring any application changes.

## docker compose logs Flags Reference

| Flag | Short | What It Does |
|------|-------|--------------|
| `--follow` | `-f` | Stream new output continuously |
| `--tail=N` | | Show last N lines per container (default: all) |
| `--timestamps` | `-t` | Prepend Docker-recorded UTC timestamps |
| `--no-color` | | Disable ANSI color coding on service names |
| `--no-log-prefix` | | Omit the `service-N \|` prefix on each line |
| `--since=DURATION` | | Show logs since a relative time (`30m`, `2h`, `1h30m`) |
| `--since=TIMESTAMP` | | Show logs since an RFC 3339 timestamp |
| `--until=TIMESTAMP` | | Show logs up to a timestamp |
| `--index=N` | | Select output from a specific replica by its index |

The `--since` and `--until` flags accept both relative durations and absolute timestamps:

```bash
docker compose logs --since=30m api

docker compose logs --since="2026-06-01T10:00:00Z" --until="2026-06-01T10:10:00Z"
```

Duration units: `s` (seconds), `m` (minutes), `h` (hours). Combine them: `1h30m`. Timestamps use RFC 3339 format with a `Z` suffix for UTC.

The `--no-log-prefix` flag removes the `api-1 |` prefix on each line. This is necessary when piping to tools that parse log content — the prefix makes lines invalid for JSON parsers, log shippers, and structured log tools that expect one parseable record per line.

## Debugging Container Crashes and Startup Failures

Container crashes are one of the most common reasons to reach for `docker compose logs`. The challenge: by the time you notice a crash, the container may have already exited. Its terminal session is gone, but its log output isn't.

`docker compose logs` works on stopped and exited containers. Docker retains log output until you explicitly remove the containers with `docker compose down` or `docker compose rm`. After a crash, run:

```bash
docker compose logs api
```

Scroll to the last few lines — the output immediately before the exit almost always contains the error message or the exception that triggered it.

### Reading Exit Codes After a Crash

Check exit codes with:

```bash
docker compose ps --all
```

The `--all` flag includes stopped containers. The STATUS column shows output like `Exited (1) 5 minutes ago`. Common exit codes:

| Exit Code | Typical Cause |
|-----------|--------------|
| 0 | Clean exit — process finished normally |
| 1 | Generic error — caught exception, missing config, bad startup arg |
| 2 | Invalid usage — bad command-line argument |
| 137 | SIGKILL — usually the OOM (out-of-memory) killer |
| 143 | SIGTERM — container stopped gracefully |

Exit code 137 requires particular attention. If a service exits with 137 and the log output stops mid-sentence without an error message, the kernel's OOM killer terminated it. The container had no chance to log the reason. Check your Compose file for memory limits and look at the host's kernel messages for OOM events.

### Diagnosing Startup Race Conditions

The most common startup failure pattern in multi-container stacks: your application tries to connect to PostgreSQL or Redis before those services have finished initializing. The log sequence looks like this:

```
api-1      | Error: connect ECONNREFUSED 172.20.0.3:5432
api-1      | Process exited with code 1
db-1       | LOG:  database system is ready to accept connections
```

The database became ready *after* the application had already crashed. The `--timestamps` flag makes this timeline unmistakable — you'll see the exact milliseconds between each event.

The fix is a `healthcheck` on the database service combined with a `depends_on` condition set to `condition: service_healthy` in your application's service definition. The [Docker Compose startup ordering documentation](https://docs.docker.com/compose/how-tos/startup-order/) covers the configuration in detail.

`docker compose logs` is how you identify this problem. The configuration change comes after you've confirmed the timing.

## Piping, Searching, and Redirecting Output

Docker Compose doesn't include built-in log search — but `docker compose logs` writes to stdout, so standard Unix tools work directly.

### Searching with grep

Search for errors across all running services:

```bash
docker compose logs | grep -i "error"
```

Search within a specific service:

```bash
docker compose logs api | grep "connection refused"
```

Combine `--since` with `grep` to narrow the search to a time window:

```bash
docker compose logs --since=1h | grep "WARN"
```

Use `--no-log-prefix` when the `service-N |` prefix would interfere with your pattern or confuse the grep regex:

```bash
docker compose logs --no-log-prefix api | grep "request-id-abc123"
```

### Parsing JSON Logs

Many Node.js, Go, and Python applications log structured JSON — one JSON object per line. Pipe with `--no-log-prefix` to `jq` for filtering:

```bash
docker compose logs --no-log-prefix api | jq 'select(.level == "error")'
```

Without `--no-log-prefix`, every line starts with `api-1 |`, making it invalid JSON. `jq` will fail to parse every line and print errors for each one.

### Saving Logs to a File

For offline analysis or sharing with teammates, redirect output to a file:

```bash
docker compose logs --timestamps > compose-debug.log 2>&1
```

This captures all services with Docker's UTC timestamps. For searching and filtering long log files, see the [Linux Commands Cheat Sheet](/cheatsheets/linux-commands-cheatsheet) for `grep`, `awk`, and `sed` patterns suited to log analysis work.

### CI/CD Log Capture

In CI/CD pipelines, capturing logs after a failed test run is standard practice. A typical GitHub Actions configuration:

```yaml
- name: Start services
  run: docker compose up --detach

- name: Run integration tests
  run: docker compose run --rm test-runner

- name: Capture logs on failure
  if: failure()
  run: docker compose logs --timestamps > /tmp/compose-logs.txt

- name: Upload log artifact
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: compose-logs
    path: /tmp/compose-logs.txt
```

The `if: failure()` condition ensures log capture only runs when a prior step has failed. The logs appear as a downloadable artifact in the Actions UI — no need to re-run the job to catch the failure live.

After tests complete — pass or fail — run `docker compose down` to tear down all containers and networks. A failed run that leaves containers running will interfere with the next run on the same host, especially if services bind to fixed ports.

For a broader reference on configuring workflows, triggers, and runners, see the [GitHub Actions Guide](/blog/github-actions-guide-status-checkout-runners).

## Log Drivers and Production Configuration

In development, the default `json-file` logging driver works well. In production, you'll usually route logs to a centralized system — Elasticsearch, CloudWatch, Splunk, or a similar platform. The logging driver choice directly affects whether `docker compose logs` works.

Docker supports several logging drivers:

| Driver | Storage | docker compose logs works? |
|--------|---------|---------------------------|
| `json-file` | Local disk | Yes (default) |
| `local` | Local disk, optimized binary | Yes |
| `syslog` | System journal | No |
| `journald` | systemd journal | No |
| `awslogs` | AWS CloudWatch Logs | No |
| `splunk` | Splunk HEC | No |
| `fluentd` | Fluentd / Fluent Bit | No |

When you configure any driver other than `json-file` or `local`, `docker compose logs` stops working — Docker forwards logs externally and cannot read them back. The [Docker logging drivers documentation](https://docs.docker.com/config/containers/logging/configure/) explains this limitation and the available configuration options.

To keep `docker compose logs` functional while also shipping logs to an external system, use the `json-file` driver locally and run a log-shipping sidecar (Fluent Bit is the common choice for Docker environments). Configure `max-size` and `max-file` options to prevent disk exhaustion from high-throughput services:

```yaml
services:
  api:
    image: my-api:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

This keeps the last three rotated log files of 10 MB each — 30 MB maximum per container. Without rotation, a high-throughput service can fill available disk space within hours. The `max-size` and `max-file` options are only available on `json-file` and `local` drivers.

When you're debugging API services alongside their logs, the [curl command guide](/guides/curl-command-guide) covers sending test HTTP requests, inspecting response headers, and measuring connection timing — a useful companion to `docker compose logs --follow` when tracing a request through your stack.

For a broader reference on Docker container management — `docker ps`, `docker exec`, `docker inspect`, and image commands — see the [Docker Commands Cheat Sheet](/cheatsheets/docker-commands-cheatsheet).

## Frequently Asked Questions

### How do I view logs for a specific service in Docker Compose?

Append the service name after the command: `docker compose logs api`. Replace `api` with the service name from your `docker-compose.yml`. To follow live output, add `--follow`: `docker compose logs --follow api`. To limit output to recent lines, add `--tail=N`: `docker compose logs --tail=50 api`. Multiple services can be specified together: `docker compose logs api db redis`.

### Can I view logs from a stopped or crashed container?

Yes. `docker compose logs` works on stopped and exited containers — Docker retains log output until you explicitly remove the containers with `docker compose down` or `docker compose rm`. After a crash, run `docker compose logs <service>` to read the output that preceded the exit. The last few lines before the crash almost always contain the error message.

### Why does docker compose logs show no output from my service?

The most common cause: the service writes logs to a file inside the container rather than to stdout or stderr. Docker only captures stdout and stderr. Configure your application to write logs to those streams — for most frameworks this is a single configuration change. A second cause: you've configured a logging driver other than `json-file` or `local`, which forwards logs to an external system and makes them unavailable through `docker compose logs`.

### How do I search Docker Compose logs for a specific string?

Pipe the output to `grep`: `docker compose logs api | grep "connection refused"`. For case-insensitive search: `docker compose logs | grep -i "error"`. When the service prefix (`api-1 |`) interferes with your pattern, use `--no-log-prefix`: `docker compose logs --no-log-prefix api | grep "ERROR"`. Combine with `--since` to limit the search to a time window: `docker compose logs --since=30m | grep "WARN"`.

### What does --tail=0 do in docker compose logs?

`--tail=0` skips all stored log history and shows only lines produced after the command runs. Combined with `--follow`, it gives you a clean live stream from the moment you run the command — nothing from previous container runs, nothing from earlier in the current session. This is the standard setup for watching a freshly restarted service initialize without noise from prior output.

## Conclusion

`docker compose logs` handles the most important debugging work in a Compose-based workflow: reading output from running services, inspecting stopped containers after a crash, and correlating events across multiple services. The `--follow`, `--tail`, `--timestamps`, `--since`, and `--no-log-prefix` flags cover most scenarios without any additional tooling. For production deployments, configure `max-size` and `max-file` on the `json-file` driver to keep disk usage bounded, and use `--no-log-prefix` when piping docker compose logs output to structured parsers or log shippers. When something goes wrong, `docker compose logs` is always available — even after the container has stopped.
