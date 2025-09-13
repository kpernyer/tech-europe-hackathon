#!/usr/bin/env node

/**
 * Demo Conversation Interpretation Script
 * Simulates a realistic CEO briefing conversation with interruptions and sentiment tracking
 */

// Using native fetch (Node.js 18+)

const BASE_URL = 'http://localhost:8787';

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(color, icon, message) {
  console.log(`${colors[color]}${icon} ${message}${colors.reset}`);
}

async function runConversationDemo() {
  log('cyan', '🏥', 'ORGANIZATIONAL TWIN CEO ASSISTANT - CONVERSATION DEMO');
  log('cyan', '━━━', '━'.repeat(60));
  
  try {
    // Initialize session
    log('blue', '🔄', 'Initializing conversation session...');
    const sessionResp = await fetch(`${BASE_URL}/api/conversation/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!sessionResp.ok) throw new Error('Failed to start session');
    const { sessionId } = await sessionResp.json();
    log('green', '✅', `Session started: ${sessionId.slice(-8)}`);
    
    console.log('\n' + colors.bright + '📋 SIMULATED CEO BRIEFING CONVERSATION' + colors.reset);
    console.log(colors.yellow + '━'.repeat(50) + colors.reset + '\n');
    
    // Conversation Flow Simulation
    await simulateConversationFlow(sessionId);
    
    // Final Analytics
    console.log('\n' + colors.bright + '📊 FINAL CONVERSATION ANALYTICS' + colors.reset);
    console.log(colors.yellow + '━'.repeat(40) + colors.reset);
    
    const analyticsResp = await fetch(`${BASE_URL}/api/analytics/summary/${sessionId}`);
    if (analyticsResp.ok) {
      const analytics = await analyticsResp.json();
      displayFinalAnalytics(analytics);
    }
    
    log('green', '🎉', 'Demo conversation completed successfully!');
    
  } catch (error) {
    log('red', '❌', `Demo failed: ${error.message}`);
    process.exit(1);
  }
}

async function simulateConversationFlow(sessionId) {
  const scenarios = [
    {
      time: 0,
      speaker: 'AI',
      message: 'Good morning! I have today\'s 5 priority items for your review. Let me walk you through them.',
      sentiment: null,
      event: { type: 'ai_response', data: { phase: 'greeting' } }
    },
    {
      time: 2000,
      speaker: 'AI', 
      message: 'First priority: Q4 Budget Approval Review - High urgency. Finance team needs final approval for $4.2M...',
      sentiment: null,
      event: { type: 'ai_response', data: { priority: 1, title: 'Q4 Budget Approval Review' } }
    },
    {
      time: 4000,
      speaker: 'CEO',
      message: 'Wait, hold on. $4.2M? That seems quite high. What exactly is this for?',
      sentiment: 'Tell me more about this $4.2M - that number concerns me',
      event: { type: 'interruption', data: { priority: 1, concern: 'budget amount' } }
    },
    {
      time: 6000,
      speaker: 'AI',
      message: 'Of course. The $4.2M covers cloud migration infrastructure and AI diagnostics integration...',
      sentiment: null,
      event: { type: 'ai_response', data: { elaboration: 'budget breakdown' } }
    },
    {
      time: 8000,
      speaker: 'CEO',
      message: 'Alright, that makes more sense. What are the risks if we delay this?',
      sentiment: 'Okay, I understand better now. What are the implications?',
      event: { type: 'follow_up_question', data: { topic: 'delay risks' } }
    },
    {
      time: 10000,
      speaker: 'AI',
      message: 'Delayed approval could push implementation to Q1 2026, missing our competitive advantage window.',
      sentiment: null,
      event: { type: 'ai_response', data: { risk_assessment: true } }
    },
    {
      time: 12000,
      speaker: 'CEO',
      message: 'Approved. Move to the next item.',
      sentiment: 'Approved, let\'s continue',
      event: { type: 'decision', data: { decision: 'approved', priority: 1 } }
    },
    {
      time: 14000,
      speaker: 'AI',
      message: 'Second priority: New Regulatory Compliance Requirements - High urgency. Japan\'s new Health Data Protection Act...',
      sentiment: null,
      event: { type: 'ai_response', data: { priority: 2, title: 'Regulatory Compliance' } }
    },
    {
      time: 16000,
      speaker: 'CEO',
      message: 'This is critical. We cannot afford non-compliance. What\'s the timeline?',
      sentiment: 'This is extremely important - we must handle this carefully',
      event: { type: 'high_priority_response', data: { emphasis: 'critical', concern: 'timeline' } }
    },
    {
      time: 18000,
      speaker: 'AI',
      message: 'Implementation required by December 2025. Non-compliance could result in ¥50M+ fines...',
      sentiment: null,
      event: { type: 'ai_response', data: { timeline: 'December 2025', risk: 'financial penalty' } }
    },
    {
      time: 20000,
      speaker: 'CEO',
      message: 'Get the Chief Compliance Officer on this immediately. Schedule a meeting today.',
      sentiment: 'This needs immediate action - very urgent',
      event: { type: 'urgent_action', data: { assignee: 'CCO', urgency: 'immediate' } }
    }
  ];
  
  for (const scenario of scenarios) {
    await sleep(scenario.time === 0 ? 0 : 2000);
    
    if (scenario.speaker === 'AI') {
      log('cyan', '🤖', `AI: ${scenario.message}`);
    } else {
      log('magenta', '👔', `CEO: ${scenario.message}`);
    }
    
    // Process event
    if (scenario.event) {
      await updateConversation(sessionId, scenario.event, null);
    }
    
    // Process sentiment
    if (scenario.sentiment) {
      const sentiment = await analyzeSentiment(scenario.sentiment);
      await updateConversation(sessionId, null, sentiment);
      
      // Display sentiment interpretation
      displaySentimentInterpretation(sentiment);
    }
    
    // Show real-time analytics periodically
    if ([4000, 12000, 20000].includes(scenario.time)) {
      await displayRealtimeAnalytics(sessionId);
    }
  }
}

async function updateConversation(sessionId, event, sentiment) {
  const payload = { sessionId };
  if (event) payload.event = event;
  if (sentiment) payload.sentiment = sentiment;
  
  await fetch(`${BASE_URL}/api/conversation/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

async function analyzeSentiment(text) {
  const resp = await fetch(`${BASE_URL}/api/sentiment/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  return resp.ok ? await resp.json() : null;
}

function displaySentimentInterpretation(sentiment) {
  if (!sentiment) return;
  
  const emotionIcon = {
    positive: '😊',
    negative: '😟', 
    stressed: '😰',
    neutral: '😐'
  }[sentiment.emotion] || '🤔';
  
  console.log(`   ${colors.yellow}💭 Sentiment: ${emotionIcon} ${sentiment.emotion} (${Math.round(sentiment.score * 100)}/100 confidence: ${Math.round(sentiment.confidence * 100)}%)${colors.reset}`);
  
  if (sentiment.indicators.length > 0) {
    console.log(`   ${colors.yellow}🎯 Indicators: ${sentiment.indicators.join(', ')}${colors.reset}`);
  }
}

async function displayRealtimeAnalytics(sessionId) {
  const resp = await fetch(`${BASE_URL}/api/analytics/summary/${sessionId}`);
  if (!resp.ok) return;
  
  const analytics = await resp.json();
  
  console.log(`\n   ${colors.bright}📊 Real-time Analytics:${colors.reset}`);
  console.log(`   ${colors.green}├─ Progress: ${analytics.backlogProgress.completed}/${analytics.backlogProgress.total} items (${analytics.backlogProgress.percentage}%)${colors.reset}`);
  console.log(`   ${colors.green}├─ Engagement: ${analytics.engagement.level}${colors.reset}`);
  console.log(`   ${colors.green}├─ Interruptions: ${analytics.engagement.interruptionCount}${colors.reset}`);
  console.log(`   ${colors.green}└─ Focus: ${analytics.engagement.focusArea}${colors.reset}\n`);
}

function displayFinalAnalytics(analytics) {
  const duration = `${Math.floor(analytics.duration / 60)}:${(analytics.duration % 60).toString().padStart(2, '0')}`;
  
  log('green', '📈', `Conversation Duration: ${duration}`);
  log('green', '📋', `Backlog Completion: ${analytics.backlogProgress.completed}/${analytics.backlogProgress.total} (${analytics.backlogProgress.percentage}%)`);
  log('green', '💭', `Final Sentiment: ${analytics.sentiment.current}`);
  log('green', '🎯', `Engagement Level: ${analytics.engagement.level}`);
  log('green', '✋', `Total Interruptions: ${analytics.engagement.interruptionCount}`);
  log('green', '🔍', `Final Focus: ${analytics.engagement.focusArea}`);
  
  if (analytics.sentiment.trend && analytics.sentiment.trend.length > 0) {
    const trend = analytics.sentiment.trend.map(score => 
      score > 0.2 ? '📈' : score < -0.2 ? '📉' : '➡️'
    ).join('');
    log('green', '📊', `Sentiment Trend: ${trend}`);
  }
  
  console.log('\n' + colors.bright + '🎯 CONVERSATION INSIGHTS:' + colors.reset);
  console.log(`${colors.cyan}• CEO showed immediate concern about budget amount (interruption)${colors.reset}`);
  console.log(`${colors.cyan}• Demonstrated strong risk awareness and urgency around compliance${colors.reset}`);
  console.log(`${colors.cyan}• Quick decision-making once context was provided${colors.reset}`);
  console.log(`${colors.cyan}• High engagement with immediate action requests${colors.reset}`);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run the conversation demo
runConversationDemo();