# Docker and Docker Compose Setup

This project includes a Dockerized development environment for both:
- The ephemeral token backend server (Express) on port 8787
- The Vite web app on port 5173

It’s intended for local development and demos with hot-reload via bind mounts.

## Prerequisites
- Docker Desktop (or compatible Docker Engine)
- Docker Compose V2 (bundled with Docker Desktop)
- A valid OpenAI API key with Realtime access

## Files added
- `docker-compose.yml` — Orchestrates web + server containers
- `Dockerfile.server` — Ephemeral token server image
- `Dockerfile.web` — Vite dev server image
- `.dockerignore` — Build context hygiene

## Environment variables
Create a `.env` file in the project root (do not commit this):
```
# Required for the token server to mint ek_ client tokens
OPENAI_API_KEY=sk-your-key-here
```

You can also maintain a `.env.example` in the repo without secrets to document expected values.

## Services and Ports
- Web (Vite): http://localhost:5173
- Server (Ephemeral token server): http://localhost:8787
  - Health: GET `/healthz` → {"ok":true}
  - Token: POST `/api/ephemeral-token` → returns payload with `client_secret.value` (ek_)

## Start (recommended for dev)
From the project root:
```
docker compose up --build
```

- The server will be available at http://localhost:8787
- The web app will be available at http://localhost:5173
- Changes to the code on your host will reflect inside the containers because `docker-compose.yml` mounts the repo:
  - `.:/app` bind mount for both services
  - `node_modules` directories are container volumes to avoid permission issues

Tip: First build may take some time. Subsequent builds will be faster due to docker layer caching.

## Verify the token server
In a separate terminal:
```
curl -i http://localhost:8787/healthz
curl -i -X POST http://localhost:8787/api/ephemeral-token \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-4o-realtime-preview-2024-12-17"}'
```
You should see a 200 OK with a JSON containing `"value": "ek_..."`.

## Frontend behavior
The frontend (src/main.ts) is configured to:
- Fetch the ephemeral token from `http://localhost:8787/api/ephemeral-token`
- Connect to OpenAI Realtime using WebRTC with the received `ek_` token

In the browser:
1) Open http://localhost:5173
2) Click “Connect to Voice Agent”
3) Allow microphone when prompted

## Common issues
- 401/403 from OpenAI:
  - Ensure `OPENAI_API_KEY` has Realtime access (org/project scopes).
- “Using WebRTC requires ephemeral client key”:
  - Ensure the frontend is actually using the ek_ token returned by the server (check Network tab).
- Connection hangs:
  - Try Chrome without blockers; corporate proxies might interfere with WebRTC/STUN/TURN.
- CORS issues:
  - `server.mjs` allows http://localhost:5173 and http://127.0.0.1:5173 by default.

## Development vs. Production
This Compose setup targets development. For production:
- Host the token server behind HTTPS (reverse proxy, TLS termination)
- Lock down CORS and add authentication/authorization
- Ensure minimal TTL/scope for ephemeral secrets
- Serve the web app as a static build (e.g., Nginx) instead of Vite dev server
- Consider multi-stage Dockerfiles to produce small production images

## Useful commands
- Start:
  ```
  docker compose up --build
  ```
- Rebuild without cache:
  ```
  docker compose build --no-cache
  docker compose up
  ```
- Stop:
  ```
  docker compose down
  ```
- View logs:
  ```
  docker compose logs -f
  ```
- Shell into a service:
  ```
  docker compose exec web sh
  docker compose exec server sh
  ```

## Notes
- The `docker-compose.yml` uses `command: sh -c "npm ci && npm run ..."` to ensure dependencies are installed inside containers at startup. For faster iteration you can also pre-install in the Dockerfiles and rely less on bind-mounts.
- The Compose config sets `--host 0.0.0.0` for Vite so it is accessible from your host. If not needed, you can remove that flag.

This setup should let you run both services with a single command and test the full WebRTC + ephemeral token flow end-to-end.
