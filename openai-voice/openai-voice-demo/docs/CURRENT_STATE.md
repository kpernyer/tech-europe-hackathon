# OpenAI Voice Demo — Current State

Last updated: 2025-09-13

## Overview
- Stack: Vite + TypeScript frontend using `@openai/agents`/`@openai/agents-realtime` for a real-time voice agent.
- Transport: WebRTC in browser with ephemeral client tokens (ek_…) minted by a tiny local backend.
- Status: Local development flow established. Ephemeral token minting verified by CLI. Frontend fetches token and connects with WebRTC.

## Project Structure (key files)
- `index.html` — Vite entry, mounts `#app`.
- `src/main.ts` — Renders UI and handles agent connect/disconnect, token fetch, and session lifecycle.
- `server.mjs` — Express server to mint ephemeral tokens via OpenAI’s `/v1/realtime/client_secrets`.
- `package.json` — Dev and server scripts, dependencies.
- `.env` — Contains secrets (do not commit). Commit a `.env.example` without secrets instead.

## Scripts
- Start frontend:
  - `npm run dev`
  - URL: http://localhost:5173
- Start ephemeral token server:
  - `npm run server`
  - URL: http://localhost:8787
  - Endpoints:
    - `GET /healthz` → `{"ok": true}`
    - `POST /api/ephemeral-token` → returns `ek_…` token payload

## Dependencies (relevant)
- `"@openai/agents": "^0.1.2"`
- `express`, `cors`, `dotenv`
- `typescript ~5.8.3`, `vite ^7.1.2`
- `zod ^3.25.76`

## Backend (server.mjs)
- Loads environment via dotenv: `import 'dotenv/config'`.
- CORS allowed origins:
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`
- Port: `8787`
- Uses `OPENAI_API_KEY` (fallback to `VITE_OPENAI_API_KEY` if provided).
- Route:
  - `POST /api/ephemeral-token`:
    - Request body: `{ "model": "gpt-4o-realtime-preview-2024-12-17" }` (default if omitted).
    - Calls OpenAI: `https://api.openai.com/v1/realtime/client_secrets`.
    - Returns the full JSON (where `client_secret.value` contains the `ek_` token).
- Health:
  - `GET /healthz` → `{"ok":true}`.

### Validation (CLI)
- Health:
  - `curl -i http://localhost:8787/healthz` → `200 OK`.
- Token:
  - `curl -i -X POST http://localhost:8787/api/ephemeral-token -H 'Content-Type: application/json' -d '{"model":"gpt-4o-realtime-preview-2024-12-17"}'`
  - Returns `200 OK` with payload including `value: "ek_..."`.

## Frontend (src/main.ts)
- Transport: WebRTC (default in browser via `RealtimeSession`).
- Model: `"gpt-4o-realtime-preview-2024-12-17"` set when creating `RealtimeSession`.
- Connect flow:
  1) Fetch `ek_` token from `http://localhost:8787/api/ephemeral-token`.
  2) Call `session.connect({ apiKey: ek })`.
  3) Listen to `transport_event` for `connection_change` and `error` to update UI.
- Mic handling:
  - Do not stop mic tracks during connect.
  - Cleanup tracks on disconnect via `session.close()` and releasing any tracks if acquired.
- UI:
  - Displays connection status (Disconnected/Connecting/Connected/Error) and transport mode (WebRTC).
  - Note: A static “Demo Information” block still mentions WebSocket simplification; consider updating copy to reflect WebRTC + ephemeral token flow.

## How to Run Locally
1) Add `OPENAI_API_KEY` to your shell or `.env` (do not commit `.env`):
   - `.env`: `OPENAI_API_KEY=sk-...`
2) Start backend server:
   - `npm run server`
   - Verify:
     - `curl -i http://localhost:8787/healthz`
     - `curl -i -X POST http://localhost:8787/api/ephemeral-token -H 'Content-Type: application/json' -d '{"model":"gpt-4o-realtime-preview-2024-12-17"}'`
3) Start frontend:
   - `npm run dev`
   - Open `http://localhost:5173`
   - Click “Connect to Voice Agent” and allow microphone.

## Troubleshooting
- If frontend shows a fetch error:
  - Ensure server is listening on `8787` and endpoint paths are correct.
  - Validate token endpoint with `curl` as above.
- If you see “Using WebRTC requires ephemeral client key”:
  - Confirm the frontend is using an `ek_` token (`Network` tab shows token response; `ek_` should be passed to `connect()`).
- If `401/403` from OpenAI:
  - Ensure `OPENAI_API_KEY` has access to Realtime and is tied to the correct org/project.
- If “invalid/missing model”:
  - Update model string to a currently supported realtime variant or omit to let SDK default apply.
- If connection hangs:
  - Try Chrome without extensions (blockers may interfere with WebRTC/STUN/TURN).
  - Verify mic permissions for `localhost`.

## Security
- Revoke any keys previously committed. Keep secrets out of Git.
- Commit a sanitized `.env.example` and ensure `.env` is gitignored.

## Suggested Next Steps
- Update UI copy to reflect WebRTC + ephemeral tokens.
- Add user-facing logs/toasts for network/transport errors.
- Add an error boundary for React errors (if adopting a React stack).
- Productionize backend:
  - Host server behind HTTPS, add auth (session/JWT)
  - Lock CORS, ensure short TTL/scope for client secrets
  - Add rate limiting and observability/logging.

## Files Touched in this iteration
- `src/main.ts`
- `server.mjs`
- `package.json`
