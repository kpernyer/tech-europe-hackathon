import './style.css'
import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime'
import { WebSocketAudioHandler } from './websocket-handler'

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div class="container">
    <div class="header">
      <h1>🏥 Organizational Twin CEO Assistant</h1>
      <p>WellnessRoberts Care - Healthcare Leadership Intelligence</p>
      <p>Real-time Voice AI with Organizational Context & Sentiment Analysis</p>
    </div>

    <div class="status-bar">
      <div class="status-card">
        <h4>🔌 Connection Status</h4>
        <div class="status-value" id="connection-status">Disconnected</div>
      </div>
      <div class="status-card">
        <h4>🎯 Transport Mode</h4>
        <div class="status-value" id="transport-mode">WebRTC</div>
      </div>
      <div class="status-card">
        <h4>🤖 AI Model</h4>
        <div class="status-value">GPT-4o Realtime</div>
      </div>
    </div>

    <div class="section compact collapsible-section">
      <div class="collapsible-header" onclick="toggleCollapse(this)">
        <h2>🎯 How to Use</h2>
        <span class="collapse-icon collapsed">▼</span>
      </div>
      <div class="collapsible-content collapsed">
        <div class="usage-steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>Connect</h3>
              <p>Click "Connect to Voice Agent" to load your organizational twin</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>Daily Briefing</h3>
              <p>Your assistant will present today's 5 priority items automatically</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>Interactive Discussion</h3>
              <p>Interrupt anytime to ask questions or dive deeper into any topic</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>🎙️ CEO Assistant Controls</h2>

      <div class="transport-selector">
        <h3>🔧 Connection Method</h3>
        <div class="transport-options">
          <label class="transport-option">
            <input type="radio" name="transport" value="webrtc" checked>
            <span class="transport-label">
              <strong>WebRTC</strong>
              <small>Direct P2P, ultra-low latency, built-in audio processing</small>
            </span>
          </label>
          <label class="transport-option">
            <input type="radio" name="transport" value="websocket">
            <span class="transport-label">
              <strong>WebSocket</strong>
              <small>Server-mediated, more reliable through firewalls</small>
            </span>
          </label>
        </div>
      </div>

      <div class="demo-controls">
        <button id="connect" class="btn btn-primary" type="button">
          🏥 Connect to Organizational Twin
        </button>
        <button id="disconnect" class="btn btn-danger" type="button" disabled>
          ❌ Disconnect
        </button>
      </div>
    </div>

    <div class="section compact">
      <h2>ℹ️ Demo Information</h2>
      <div class="warning">
        <p>🏥 <strong>Organizational Twin:</strong> This AI assistant has deep knowledge of WellnessRoberts Care's context, priorities, and culture.</p>
        <p>💼 <strong>Demo Features:</strong> Daily backlog presentation, interruption handling, sentiment analysis, and conversation state management.</p>
      </div>
    </div>

    <div class="section">
      <h2>📊 Session Status</h2>
      <div id="status" class="response-area">
        <p>Status: Disconnected</p>
        <p>Ready to connect to your organizational twin assistant.</p>
      </div>

      <div class="section">
        <h2>📈 Conversation Analytics</h2>
        <div class="analytics-grid">
          <div class="analytics-card">
            <h4>📊 Backlog Progress</h4>
            <div id="backlog-progress" class="status-value">Not Started</div>
          </div>
          <div class="analytics-card">
            <h4>⏱️ Conversation Time</h4>
            <div id="conversation-time" class="status-value">00:00</div>
          </div>
          <div class="analytics-card">
            <h4>🎯 Focus Area</h4>
            <div id="focus-area" class="status-value">Awaiting Connection</div>
          </div>
          <div class="analytics-card">
            <h4>📈 CEO Engagement</h4>
            <div id="engagement-level" class="status-value">Baseline</div>
          </div>
        </div>
      </div>
    </div>
  </div>
`

class VoiceAgentDemo {
  private session: RealtimeSession | null = null
  private webSocketHandler: WebSocketAudioHandler | null = null
  private currentTransport: 'webrtc' | 'websocket' = 'webrtc'
  private micStream: MediaStream | null = null
  private connectBtn: HTMLButtonElement
  private disconnectBtn: HTMLButtonElement
  private statusDiv: HTMLDivElement
  private connectionStatusDiv: HTMLDivElement
  private transportModeDiv: HTMLDivElement
  private conversationStartTime: number | null = null
  private conversationTimerInterval: number | null = null
  private conversationSessionId: string | null = null
  private lastTranscript: string = ''
  private sentimentUpdateInterval: number | null = null

  constructor() {
    this.connectBtn = document.querySelector<HTMLButtonElement>('#connect')!
    this.disconnectBtn = document.querySelector<HTMLButtonElement>('#disconnect')!
    this.statusDiv = document.querySelector<HTMLDivElement>('#status')!
    this.connectionStatusDiv = document.querySelector<HTMLDivElement>('#connection-status')!
    this.transportModeDiv = document.querySelector<HTMLDivElement>('#transport-mode')!

    this.setupEventListeners()
  }

  private setupEventListeners() {
    this.connectBtn.addEventListener('click', () => this.connect())
    this.disconnectBtn.addEventListener('click', () => this.disconnect())

    // Listen for transport method changes
    const transportRadios = document.querySelectorAll<HTMLInputElement>('input[name="transport"]')
    transportRadios.forEach(radio => {
      radio.addEventListener('change', (e) => {
        if ((e.target as HTMLInputElement).checked) {
          this.currentTransport = (e.target as HTMLInputElement).value as 'webrtc' | 'websocket'
          this.transportModeDiv.textContent = this.currentTransport === 'webrtc' ? 'WebRTC' : 'WebSocket'
          console.log('Transport method changed to:', this.currentTransport)
        }
      })
    })
  }

  private updateStatus(message: string) {
    this.statusDiv.innerHTML = `<p>Status: ${message}</p>\n<p>🕒 ${new Date().toLocaleTimeString()}</p>`
  }

  private updateConnectionStatus(status: 'connected' | 'connecting' | 'disconnected' | 'error', message: string) {
    this.connectionStatusDiv.className = `status-value ${status}`
    this.connectionStatusDiv.textContent = message
  }

  private updateAnalytics(elementId: string, value: string) {
    const element = document.getElementById(elementId)
    if (element) {
      element.textContent = value
    }
  }

  private startConversationTimer() {
    this.conversationStartTime = Date.now()
    this.conversationTimerInterval = window.setInterval(() => {
      if (this.conversationStartTime) {
        const elapsed = Math.floor((Date.now() - this.conversationStartTime) / 1000)
        const minutes = Math.floor(elapsed / 60)
        const seconds = elapsed % 60
        this.updateAnalytics('conversation-time', `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`)
      }
    }, 1000)
  }

  private stopConversationTimer() {
    if (this.conversationTimerInterval) {
      clearInterval(this.conversationTimerInterval)
      this.conversationTimerInterval = null
    }
    this.conversationStartTime = null
  }
  
  private async startConversationSession() {
    try {
      const response = await fetch('http://localhost:8787/api/conversation/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        const data = await response.json()
        this.conversationSessionId = data.sessionId
        console.log('Started conversation session:', this.conversationSessionId)
      }
    } catch (error) {
      console.error('Failed to start conversation session:', error)
    }
  }
  
  private async trackConversationEvent(eventType: string, eventData: any) {
    if (!this.conversationSessionId) return
    
    try {
      await fetch('http://localhost:8787/api/conversation/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: this.conversationSessionId,
          event: {
            type: eventType,
            data: eventData
          }
        })
      })
    } catch (error) {
      console.error('Failed to track conversation event:', error)
    }
  }
  
  private startSentimentMonitoring() {
    this.sentimentUpdateInterval = window.setInterval(async () => {
      await this.analyzeSentimentAndUpdateUI()
    }, 5000) // Analyze sentiment every 5 seconds
  }
  
  private stopSentimentMonitoring() {
    if (this.sentimentUpdateInterval) {
      clearInterval(this.sentimentUpdateInterval)
      this.sentimentUpdateInterval = null
    }
  }
  
  private async analyzeSentimentAndUpdateUI() {
    if (!this.conversationSessionId) return
    
    try {
      // Get conversation analytics
      const analyticsResp = await fetch(`http://localhost:8787/api/analytics/summary/${this.conversationSessionId}`)
      if (analyticsResp.ok) {
        const analytics = await analyticsResp.json()
        
        // Update UI with analytics
        this.updateAnalytics('backlog-progress', `${analytics.backlogProgress.completed}/${analytics.backlogProgress.total} items (${analytics.backlogProgress.percentage}%)`)
        this.updateAnalytics('focus-area', analytics.engagement.focusArea)
        this.updateAnalytics('engagement-level', this.formatEngagementLevel(analytics.engagement.level))
        
        // Update conversation state if needed
        if (analytics.sentiment.current !== 'neutral') {
          console.log('Sentiment detected:', analytics.sentiment.current)
        }
      }
    } catch (error) {
      console.error('Failed to analyze sentiment:', error)
    }
  }
  
  private formatEngagementLevel(level: string): string {
    switch (level) {
      case 'high': return '🔥 Highly Engaged'
      case 'active': return '✅ Actively Engaged'
      case 'stressed': return '⚡ Stressed/Urgent'
      case 'baseline': return '📊 Baseline'
      default: return level
    }
  }

  private async connect() {
    try {
      this.updateStatus('🔄 Creating voice agent...')
      this.updateConnectionStatus('connecting', 'Connecting...')
      this.connectBtn.disabled = true

      console.log(`Creating agent and session using ${this.currentTransport}...`)

      if (this.currentTransport === 'websocket') {
        await this.connectViaWebSocket()
      } else {
        await this.connectViaWebRTC()
      }

    } catch (error) {
      console.error('Connection failed:', error)
      const errorMessage = error instanceof Error ? error.message : String(error)
      this.updateStatus(`❌ Connection failed: ${errorMessage}\n\n💡 This might be due to:\n• Browser extension conflicts\n• Network connectivity issues\n• API key problems`)
      this.updateConnectionStatus('error', 'Failed')
      this.connectBtn.disabled = false
    }
  }

  private async connectViaWebRTC() {
    console.log('Creating agent and session...')

    // Load organizational context and instructions
    const [contextResp, instructionsResp] = await Promise.all([
      fetch('http://localhost:8787/api/organization/context'),
      fetch('http://localhost:8787/api/organization/instructions')
    ])

    if (!contextResp.ok || !instructionsResp.ok) {
      throw new Error('Failed to load organizational context or instructions')
    }

    const contextData = await contextResp.json()
    const instructionsData = await instructionsResp.json()

    this.updateStatus(`🏥 Loaded context for ${contextData.organization.name}...`)

    const agent = new RealtimeAgent({
      name: 'Organizational Twin',
      instructions: instructionsData.instructions,
    })

    this.session = new RealtimeSession(agent, {
      model: 'gpt-4o-realtime-preview-2024-12-17',
    })

    // Forward transport connection changes and errors to UI
    this.session.on('transport_event', (event: any) => {
      console.log('transport_event:', event)
      if (event.type === 'connection_change') {
        const status = event.status as 'connecting' | 'connected' | 'disconnected' | undefined
        if (status) {
          this.updateConnectionStatus(
            status === 'connected' ? 'connected' : status === 'connecting' ? 'connecting' : 'disconnected',
            status.charAt(0).toUpperCase() + status.slice(1)
          )
        }
      } else if (event.type === 'error') {
        const msg =
          typeof event?.error === 'string'
            ? event.error
            : event?.error?.message || JSON.stringify(event)
        console.error('Transport error event:', event)
        this.updateStatus(`❌ Transport error: ${msg}`)
        this.updateConnectionStatus('error', 'Error')
        this.connectBtn.disabled = false
        this.disconnectBtn.disabled = true
      }
    })

    this.updateStatus('🎤 Preparing to connect (browser may prompt for microphone)...')

    this.updateStatus('🔗 Fetching ephemeral client token...')
    // Request an ek_ token from the local server
    const tokenResp = await fetch('http://localhost:8787/api/ephemeral-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'gpt-4o-realtime-preview-2024-12-17' })
    })
    const tokenData = await tokenResp.json()
    if (!tokenResp.ok) {
      throw new Error('Ephemeral token error: ' + JSON.stringify(tokenData))
    }
    const ek =
      tokenData?.client_secret?.value ??
      tokenData?.client_secret ??
      tokenData?.value
    if (!ek || typeof ek !== 'string' || !ek.startsWith('ek_')) {
      throw new Error('Invalid ephemeral token response')
    }

    this.updateStatus('🔗 Connecting to OpenAI Realtime API (WebRTC)...')

    // Simple connection with timeout
    const connectPromise = this.session.connect({
      apiKey: ek
    })

    // Add a timeout to avoid hanging
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Connection timeout after 30 seconds')), 30000)
    })

    await Promise.race([connectPromise, timeoutPromise])

    console.log('Connection successful!')
    this.updateStatus('🎉 Connected to your organizational twin!\n\n🏥 Your assistant will now present today\'s priority items.\n💬 You can interrupt anytime to ask questions or dive deeper.')

    // Update analytics
    this.updateAnalytics('backlog-progress', 'Starting Presentation')
    this.updateAnalytics('focus-area', 'Daily Briefing')
    this.updateAnalytics('engagement-level', 'Active')
    this.startConversationTimer()
    this.updateConnectionStatus('connected', 'Connected')
    this.connectBtn.disabled = true
    this.disconnectBtn.disabled = false

    // Start conversation session tracking
    await this.startConversationSession()

    // Add event listeners after successful connection
    this.session.on('error', (error) => {
      console.error('Session error:', error)
      this.updateStatus(`❌ Session error: ${error}`)
      this.updateConnectionStatus('error', 'Error')
    })

    // Track conversation events for sentiment analysis
    this.session.on('response', (response) => {
      console.log('AI Response:', response)
      this.trackConversationEvent('ai_response', { response })
    })

    this.session.on('input_audio_buffer_committed', (event) => {
      console.log('Audio input committed:', event)
      this.trackConversationEvent('user_speech', { duration: event.duration || 0 })
    })

    // Start periodic sentiment analysis
    this.startSentimentMonitoring()
  }

  private async connectViaWebSocket() {
    // Load organizational context and instructions
    const [contextResp, instructionsResp] = await Promise.all([
      fetch('http://localhost:8787/api/organization/context'),
      fetch('http://localhost:8787/api/organization/instructions')
    ])

    if (!contextResp.ok || !instructionsResp.ok) {
      throw new Error('Failed to load organizational context or instructions')
    }

    const contextData = await contextResp.json()
    const instructionsData = await instructionsResp.json()

    this.updateStatus(`🏥 Loaded context for ${contextData.organization.name}...`)

    this.updateStatus('🔗 Fetching ephemeral client token...')

    // Request an ek_ token from the local server
    const tokenResp = await fetch('http://localhost:8787/api/ephemeral-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'gpt-4o-realtime-preview-2024-12-17' })
    })
    const tokenData = await tokenResp.json()
    if (!tokenResp.ok) {
      throw new Error('Ephemeral token error: ' + JSON.stringify(tokenData))
    }
    const ek =
      tokenData?.client_secret?.value ??
      tokenData?.client_secret ??
      tokenData?.value
    if (!ek || typeof ek !== 'string' || !ek.startsWith('ek_')) {
      throw new Error('Invalid ephemeral token response')
    }

    this.updateStatus('🔗 Connecting to OpenAI Realtime API (WebSocket)...')

    // Create WebSocket handler
    this.webSocketHandler = new WebSocketAudioHandler(
      ek,
      (status, message) => {
        this.updateConnectionStatus(status, message)
      },
      (text, isUser) => {
        console.log(`${isUser ? 'User' : 'AI'}:`, text)
        // Handle transcript display if needed
      },
      (audioData) => {
        // Handle audio playback if needed
        console.log('Received audio data:', audioData.length, 'bytes')
      }
    )

    await this.webSocketHandler.connect()

    console.log('WebSocket connection successful!')
    this.updateStatus('🎉 Connected to your organizational twin via WebSocket!\n\n🏥 Your assistant will now present today\'s priority items.\n💬 You can interrupt anytime to ask questions or dive deeper.')

    // Update analytics
    this.updateAnalytics('backlog-progress', 'Starting Presentation')
    this.updateAnalytics('focus-area', 'Daily Briefing')
    this.updateAnalytics('engagement-level', 'Active')
    this.startConversationTimer()
    this.updateConnectionStatus('connected', 'Connected')
    this.connectBtn.disabled = true
    this.disconnectBtn.disabled = false

    // Start conversation session tracking
    await this.startConversationSession()

    // Start periodic sentiment analysis
    this.startSentimentMonitoring()
  }

  private disconnect() {
    // Disconnect WebRTC session
    if (this.session) {
      this.session.close()
      this.session = null
    }

    // Disconnect WebSocket handler
    if (this.webSocketHandler) {
      this.webSocketHandler.disconnect()
      this.webSocketHandler = null
    }

    if (this.micStream) {
      this.micStream.getTracks().forEach(track => track.stop())
      this.micStream = null
    }

    this.updateStatus('🔌 Disconnected from organizational twin\n\nReady to reconnect when needed.')
    this.updateConnectionStatus('disconnected', 'Disconnected')
    this.connectBtn.disabled = false
    this.disconnectBtn.disabled = true

    // Reset analytics
    this.updateAnalytics('backlog-progress', 'Not Started')
    this.updateAnalytics('conversation-time', '00:00')
    this.updateAnalytics('focus-area', 'Awaiting Connection')
    this.updateAnalytics('engagement-level', 'Baseline')
    this.stopConversationTimer()
    this.stopSentimentMonitoring()
    this.conversationSessionId = null
  }
}

const voiceDemo = new VoiceAgentDemo()

// Export demo instance for global access
;(window as any).voiceDemo = voiceDemo

// Collapsible functionality
function toggleCollapse(header: HTMLElement) {
  const content = header.nextElementSibling as HTMLElement
  const icon = header.querySelector('.collapse-icon') as HTMLElement

  if (content.classList.contains('collapsed')) {
    content.classList.remove('collapsed')
    icon.classList.remove('collapsed')
    content.style.maxHeight = content.scrollHeight + 'px'
  } else {
    content.classList.add('collapsed')
    icon.classList.add('collapsed')
    content.style.maxHeight = '0px'
  }
}

// Make toggleCollapse available globally
;(window as any).toggleCollapse = toggleCollapse
