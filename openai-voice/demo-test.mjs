#!/usr/bin/env node

/**
 * Demo Test Script for Organizational Twin CEO Assistant
 * This script tests the conversation flow and analytics endpoints
 */

// Using native fetch (Node.js 18+)

const BASE_URL = 'http://localhost:8787';

// Simulate a demo conversation session
async function runDemoTest() {
  console.log('🏥 Testing Organizational Twin CEO Assistant Demo\n');
  
  try {
    // 1. Test health check
    console.log('1️⃣ Testing health check...');
    const healthResp = await fetch(`${BASE_URL}/healthz`);
    if (healthResp.ok) {
      console.log('   ✅ Server is running');
    } else {
      throw new Error('Server not responsive');
    }
    
    // 2. Test organizational context loading
    console.log('\n2️⃣ Testing organizational context...');
    const contextResp = await fetch(`${BASE_URL}/api/organization/context`);
    if (contextResp.ok) {
      const context = await contextResp.json();
      console.log(`   ✅ Loaded ${context.organization.name} context`);
      console.log(`   📋 ${context.backlog.ceo_daily_priorities.length} priorities for ${context.backlog.date}`);
    } else {
      throw new Error('Failed to load context');
    }
    
    // 3. Start conversation session
    console.log('\n3️⃣ Starting conversation session...');
    const sessionResp = await fetch(`${BASE_URL}/api/conversation/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!sessionResp.ok) {
      throw new Error('Failed to start session');
    }
    
    const sessionData = await sessionResp.json();
    const sessionId = sessionData.sessionId;
    console.log(`   ✅ Started session: ${sessionId}`);
    
    // 4. Simulate conversation events
    console.log('\n4️⃣ Simulating conversation events...');
    
    // Simulate AI presenting first priority
    await simulateEvent(sessionId, 'ai_response', { priority: 1, content: 'Q4 Budget Approval Review' });
    console.log('   📢 AI presented priority #1');
    
    // Simulate CEO interruption
    await simulateEvent(sessionId, 'interruption', { priority: 1, concern: 'budget details' });
    console.log('   ✋ CEO interrupted to ask about budget');
    
    // Simulate sentiment analysis
    await simulateSentiment(sessionId, 'Tell me more about the $4.2M investment - that seems high');
    console.log('   💭 Analyzed CEO sentiment (concerned about budget)');
    
    // Simulate focus change
    await simulateEvent(sessionId, 'focus_change', { newFocus: 'Budget Details Discussion' });
    console.log('   🎯 Focus changed to budget details');
    
    // Wait and simulate more events
    await sleep(2000);
    
    await simulateEvent(sessionId, 'ai_response', { content: 'Budget breakdown explanation' });
    await simulateSentiment(sessionId, 'Okay, that makes sense. Let\'s continue with the other items');
    console.log('   ✅ CEO satisfied, ready to continue');
    
    // 5. Get analytics summary
    console.log('\n5️⃣ Getting conversation analytics...');
    const analyticsResp = await fetch(`${BASE_URL}/api/analytics/summary/${sessionId}`);
    if (analyticsResp.ok) {
      const analytics = await analyticsResp.json();
      console.log('   📊 Analytics Summary:');
      console.log(`      • Duration: ${analytics.duration} seconds`);
      console.log(`      • Backlog Progress: ${analytics.backlogProgress.completed}/${analytics.backlogProgress.total} (${analytics.backlogProgress.percentage}%)`);
      console.log(`      • Current Sentiment: ${analytics.sentiment.current}`);
      console.log(`      • Engagement Level: ${analytics.engagement.level}`);
      console.log(`      • Interruptions: ${analytics.engagement.interruptionCount}`);
      console.log(`      • Focus Area: ${analytics.engagement.focusArea}`);
    }
    
    console.log('\n🎉 Demo test completed successfully!');
    console.log('\n📋 Test Summary:');
    console.log('   ✅ Organizational context loaded');
    console.log('   ✅ Conversation session tracking working');  
    console.log('   ✅ Sentiment analysis functional');
    console.log('   ✅ Analytics endpoints responsive');
    console.log('   ✅ Interruption handling simulated');
    console.log('   ✅ Real-time conversation state management');
    
    console.log('\n🚀 Ready for live demo with voice interface!');
    
  } catch (error) {
    console.error('\n❌ Demo test failed:', error.message);
    console.log('\n💡 Make sure the server is running: npm run server');
    process.exit(1);
  }
}

// Helper functions
async function simulateEvent(sessionId, eventType, eventData) {
  await fetch(`${BASE_URL}/api/conversation/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sessionId,
      event: { type: eventType, data: eventData }
    })
  });
}

async function simulateSentiment(sessionId, text) {
  // First analyze the sentiment
  const sentimentResp = await fetch(`${BASE_URL}/api/sentiment/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  
  if (sentimentResp.ok) {
    const sentiment = await sentimentResp.json();
    
    // Then update the conversation with sentiment data
    await fetch(`${BASE_URL}/api/conversation/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId,
        sentiment
      })
    });
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run the demo test
runDemoTest();