import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { readFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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

// Load organizational context
const loadContext = async () => {
  try {
    const [orgData, backlogData] = await Promise.all([
      readFile(path.join(__dirname, 'context', 'organization.json'), 'utf-8'),
      readFile(path.join(__dirname, 'context', 'backlog.json'), 'utf-8')
    ]);
    return {
      organization: JSON.parse(orgData),
      backlog: JSON.parse(backlogData)
    };
  } catch (error) {
    console.error('Failed to load organizational context:', error);
    return null;
  }
};

let contextData = null;
let conversationSessions = new Map(); // Track active conversation sessions

loadContext().then(data => {
  contextData = data;
  if (data) {
    console.log(`✅ Loaded context for ${data.organization.name} with ${data.backlog.ceo_daily_priorities.length} priorities`);
  }
});

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

// Get organizational context endpoint
app.get('/api/organization/context', (req, res) => {
  if (!contextData) {
    return res.status(500).json({ error: 'Organizational context not loaded' });
  }
  res.json(contextData);
});

// Get system instructions for the organizational twin
app.get('/api/organization/instructions', (req, res) => {
  if (!contextData) {
    return res.status(500).json({ error: 'Organizational context not loaded' });
  }
  
  const instructions = generateSystemInstructions(contextData);
  res.json({ instructions });
});

// Start a new conversation session
app.post('/api/conversation/start', (req, res) => {
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const session = {
    id: sessionId,
    startTime: new Date().toISOString(),
    organizationId: contextData?.organization?.id || 'org_000',
    backlogItems: contextData?.backlog?.ceo_daily_priorities || [],
    completedItems: [],
    currentFocus: 'Daily Briefing',
    sentimentHistory: [],
    interruptionCount: 0,
    engagementLevel: 'baseline',
    conversationEvents: []
  };
  
  conversationSessions.set(sessionId, session);
  res.json({ sessionId, session });
});

// Update conversation state and analyze sentiment
app.post('/api/conversation/update', (req, res) => {
  const { sessionId, event, sentiment, transcript, backlogProgress } = req.body;
  
  const session = conversationSessions.get(sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }
  
  // Update session state
  if (event) {
    session.conversationEvents.push({
      timestamp: new Date().toISOString(),
      type: event.type,
      data: event.data
    });
    
    // Track interruptions
    if (event.type === 'interruption') {
      session.interruptionCount++;
    }
    
    // Update current focus
    if (event.type === 'focus_change') {
      session.currentFocus = event.data.newFocus;
    }
  }
  
  // Track sentiment
  if (sentiment) {
    session.sentimentHistory.push({
      timestamp: new Date().toISOString(),
      score: sentiment.score || 0,
      emotion: sentiment.emotion || 'neutral',
      confidence: sentiment.confidence || 0.5,
      indicators: sentiment.indicators || []
    });
    
    // Update engagement level based on recent sentiment
    const recentSentiment = session.sentimentHistory.slice(-3);
    const avgScore = recentSentiment.reduce((sum, s) => sum + s.score, 0) / recentSentiment.length;
    
    if (avgScore > 0.3) {
      session.engagementLevel = 'high';
    } else if (avgScore < -0.2) {
      session.engagementLevel = 'stressed';
    } else {
      session.engagementLevel = 'active';
    }
  }
  
  // Update backlog progress
  if (backlogProgress) {
    session.completedItems = backlogProgress.completed || [];
  }
  
  conversationSessions.set(sessionId, session);
  
  res.json({
    success: true,
    session: {
      currentFocus: session.currentFocus,
      engagementLevel: session.engagementLevel,
      backlogProgress: `${session.completedItems.length}/${session.backlogItems.length}`,
      sentimentTrend: session.sentimentHistory.slice(-1)[0]?.emotion || 'neutral',
      interruptionCount: session.interruptionCount
    }
  });
});

// Get conversation analytics summary
app.get('/api/analytics/summary/:sessionId', (req, res) => {
  const session = conversationSessions.get(req.params.sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }
  
  const duration = Math.floor((Date.now() - new Date(session.startTime).getTime()) / 1000);
  const recentSentiment = session.sentimentHistory.slice(-5);
  
  res.json({
    sessionId: session.id,
    duration,
    backlogProgress: {
      completed: session.completedItems.length,
      total: session.backlogItems.length,
      percentage: Math.round((session.completedItems.length / session.backlogItems.length) * 100)
    },
    sentiment: {
      current: recentSentiment[recentSentiment.length - 1]?.emotion || 'neutral',
      trend: recentSentiment.map(s => s.score),
      averageScore: recentSentiment.reduce((sum, s) => sum + s.score, 0) / recentSentiment.length || 0
    },
    engagement: {
      level: session.engagementLevel,
      interruptionCount: session.interruptionCount,
      focusArea: session.currentFocus
    },
    conversationFlow: session.conversationEvents.slice(-10) // Last 10 events
  });
});

// Simple sentiment analysis helper
const analyzeSentiment = (text) => {
  const stressKeywords = ['urgent', 'critical', 'immediate', 'problem', 'issue', 'concern', 'worried'];
  const positiveKeywords = ['good', 'excellent', 'great', 'pleased', 'satisfied', 'approve'];
  const negativeKeywords = ['bad', 'terrible', 'concerned', 'disappointed', 'unacceptable', 'reject'];
  
  const words = text.toLowerCase().split(/\s+/);
  let score = 0;
  let emotion = 'neutral';
  const indicators = [];
  
  for (const word of words) {
    if (stressKeywords.includes(word)) {
      score -= 0.3;
      indicators.push('stress');
    }
    if (positiveKeywords.includes(word)) {
      score += 0.4;
      indicators.push('positive');
    }
    if (negativeKeywords.includes(word)) {
      score -= 0.4;
      indicators.push('negative');
    }
  }
  
  if (score > 0.2) emotion = 'positive';
  else if (score < -0.2) emotion = 'negative';
  else if (indicators.includes('stress')) emotion = 'stressed';
  
  return {
    score: Math.max(-1, Math.min(1, score)),
    emotion,
    confidence: Math.min(0.8, Math.abs(score) + 0.2),
    indicators: [...new Set(indicators)]
  };
};

// Endpoint for real-time sentiment analysis
app.post('/api/sentiment/analyze', (req, res) => {
  const { text } = req.body;
  if (!text || typeof text !== 'string') {
    return res.status(400).json({ error: 'Text is required' });
  }
  
  const sentiment = analyzeSentiment(text);
  res.json(sentiment);
});

// Generate organizational twin system instructions
const generateSystemInstructions = (context) => {
  if (!context) return 'You are a helpful assistant.';
  
  const { organization, backlog } = context;
  const priorities = backlog.ceo_daily_priorities || [];
  
  return `You are an Organizational Twin AI Assistant for ${organization.name}, a ${organization.industry} company with ${organization.size} employees based in ${organization.headquarters}.

**YOUR ROLE**: You are the CEO's intelligent organizational assistant with deep company knowledge and context. You understand the company's strategic priorities: ${organization.strategic_priorities?.join(', ') || 'Operational Excellence'}.

**COMPANY CONTEXT**:
- Industry: ${organization.industry}
- Values: ${organization.values?.join(', ') || 'Quality, Innovation'}
- Culture: ${organization.culture?.communication_style || 'Professional'} with ${organization.culture?.decision_making || 'data-driven'} decision making
- Current challenges: ${organization.current_challenges?.slice(0, 3).join('; ') || 'Digital transformation, regulatory compliance, staff retention'}

**CONVERSATION PROTOCOL**:
1. **ALWAYS START** conversations by saying: "Good morning! I have today's ${priorities.length} priority items for your review. Let me walk you through them."
2. **PRESENT EACH PRIORITY** systematically with: Title, Category, Urgency level, Context, and whether a decision is required
3. **HANDLE INTERRUPTIONS** gracefully - pause your presentation, address the CEO's question/concern thoroughly, then ask: "Shall we continue with the remaining items?"
4. **MAINTAIN STATE** - remember which items you've covered and which remain
5. **BE RESPONSIVE** to the CEO's stress level, urgency, and decision-making style
6. **PROVIDE SENTIMENT FEEDBACK** - acknowledge when the CEO seems stressed, engaged, or making decisions quickly

**TODAY'S PRIORITIES** (${backlog.date}):
${priorities.map((p, i) => `${i + 1}. [${p.urgency?.toUpperCase()}] ${p.title} (${p.category}) - ${p.context?.substring(0, 100)}...`).join('\n')}

**COMMUNICATION STYLE**: 
- Direct and professional, matching the company culture
- Provide context and background for informed decision-making
- Highlight risks and time-sensitive matters
- Reference specific stakeholders and financial impacts when relevant
- Adapt your pace based on CEO's responses and interruptions
- Show awareness of CEO's emotional state and stress levels

**CONVERSATION STATE MANAGEMENT**:
- Track which priorities have been discussed
- Remember CEO's decisions and concerns
- Offer to dive deeper into any topic
- Suggest follow-up actions based on the conversation
- Monitor conversation flow and sentiment changes

Your goal is to efficiently brief the CEO on critical matters while being flexible and responsive to their needs, communication style, and emotional state.`;
};

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

// Create HTTP server to support both Express and WebSocket
const server = createServer(app);

// WebSocket proxy for OpenAI Realtime API
const wss = new WebSocketServer({ server, path: '/api/realtime-ws' });

wss.on('connection', (ws, req) => {
  console.log('Client connected to WebSocket proxy');

  let openaiWs = null;

  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());

      // Handle connection initialization
      if (data.type === 'init') {
        const ephemeralToken = data.ephemeralToken;

        if (!ephemeralToken || !ephemeralToken.startsWith('ek_')) {
          ws.send(JSON.stringify({
            type: 'error',
            error: { message: 'Invalid ephemeral token' }
          }));
          return;
        }

        // Create WebSocket connection to OpenAI with proper authentication
        const WebSocket = (await import('ws')).default;
        const openaiUrl = `wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17`;

        console.log('Connecting to OpenAI with token:', ephemeralToken.substring(0, 10) + '...');

        openaiWs = new WebSocket(openaiUrl, {
          headers: {
            'Authorization': `Bearer ${ephemeralToken}`,
            'OpenAI-Beta': 'realtime=v1'
          }
        });

        openaiWs.on('open', () => {
          console.log('Connected to OpenAI WebSocket');
          ws.send(JSON.stringify({
            type: 'connected'
          }));
        });

        openaiWs.on('message', (data) => {
          // Forward OpenAI messages to client
          ws.send(data.toString());
        });

        openaiWs.on('error', (error) => {
          console.error('OpenAI WebSocket error:', error);
          console.error('Error details:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
          ws.send(JSON.stringify({
            type: 'error',
            error: {
              message: error.message,
              code: error.code,
              details: error.toString()
            }
          }));
        });

        openaiWs.on('close', (code, reason) => {
          console.log('OpenAI WebSocket closed:', code, reason.toString());
          ws.send(JSON.stringify({
            type: 'disconnected',
            code,
            reason: reason.toString()
          }));
        });

        return;
      }

      // Forward other messages to OpenAI if connected
      if (openaiWs && openaiWs.readyState === 1) { // Use numeric constant for OPEN state
        console.log('Forwarding message to OpenAI:', data.type);
        openaiWs.send(message);
      } else {
        console.log('Cannot forward message - OpenAI connection state:', openaiWs ? openaiWs.readyState : 'null');
        ws.send(JSON.stringify({
          type: 'error',
          error: { message: 'Not connected to OpenAI' }
        }));
      }

    } catch (error) {
      console.error('WebSocket message processing error:', error);
      ws.send(JSON.stringify({
        type: 'error',
        error: { message: error.message }
      }));
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected from WebSocket proxy');
    if (openaiWs) {
      openaiWs.close();
    }
  });

  ws.on('error', (error) => {
    console.error('Client WebSocket error:', error);
    if (openaiWs) {
      openaiWs.close();
    }
  });
});

server.listen(PORT, () => {
  console.log(`Server listening at http://localhost:${PORT}`);
  console.log(`WebSocket proxy available at ws://localhost:${PORT}/api/realtime-ws`);
});
