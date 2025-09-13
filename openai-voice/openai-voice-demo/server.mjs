import 'dotenv/config';
import express from 'express';
import cors from 'cors';

const app = express();

// Allow the Vite dev server origin
app.use(
  cors({
    origin: ['http://localhost:5173', 'http://127.0.0.1:5173'],
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type'],
  }),
);

app.use(express.json());

const PORT = process.env.PORT || 8787;
// Prefer OPENAI_API_KEY but fall back to VITE_OPENAI_API_KEY if present (local-only convenience)
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || process.env.VITE_OPENAI_API_KEY;

if (!OPENAI_API_KEY) {
  console.warn(
    'Warning: No OPENAI_API_KEY found in environment. Set OPENAI_API_KEY in your shell (or add it to .env and load it before starting this server).',
  );
}

app.get('/healthz', (req, res) => {
  res.json({ ok: true });
});

// Mint an ephemeral client key for Realtime (ek_...) bound to the requested model
app.post('/api/ephemeral-token', async (req, res) => {
  try {
    const model =
      (req.body && typeof req.body.model === 'string' && req.body.model) ||
      'gpt-4o-realtime-preview-2024-12-17';

    if (!OPENAI_API_KEY) {
      return res.status(500).json({ error: 'OPENAI_API_KEY not set on server' });
    }

    const upstream = await fetch('https://api.openai.com/v1/realtime/client_secrets', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session: {
          type: 'realtime',
          model,
        },
      }),
    });

    const data = await upstream.json();

    if (!upstream.ok) {
      console.error('OpenAI /client_secrets error:', data);
      return res.status(upstream.status).json({ error: data });
    }

    // Return the full payload (client_secret.value will contain the ek_ token)
    res.json(data);
  } catch (err) {
    console.error('Ephemeral token server error:', err);
    res.status(500).json({ error: String(err) });
  }
});

app.listen(PORT, () => {
  console.log(`Ephemeral token server listening at http://localhost:${PORT}`);
});
