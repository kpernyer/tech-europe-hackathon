import './style.css'
import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime'

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div class="container">
    <div class="header">
      <h1>🎙️ OpenAI Voice Demo at Hackathon {Tech: Europe}</h1>
      <p>September 13-14th 2025, Kenneth Pernyer</p>
      <p>Real-time Voice AI Agent with WebSocket Transport</p>
    </div>

    <div class="status-bar">
      <div class="status-card">
        <h4>🔌 Connection Status</h4>
        <div class="status-value" id="connection-status">Disconnected</div>
      </div>
      <div class="status-card">
        <h4>🎯 Transport Mode</h4>
        <div class="status-value">WebRTC</div>
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
              <p>Click "Connect to Voice Agent" to establish WebSocket connection</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>Allow Microphone</h3>
              <p>Grant microphone permissions when prompted by your browser</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>Start Talking</h3>
              <p>Speak naturally with the AI assistant - it will respond in real-time</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>🎙️ Voice Agent Controls</h2>
      <div class="demo-controls">
        <button id="connect" class="btn btn-primary" type="button">
          🔗 Connect to Voice Agent
        </button>
        <button id="disconnect" class="btn btn-danger" type="button" disabled>
          ❌ Disconnect
        </button>
      </div>
    </div>

    <div class="section compact">
      <h2>ℹ️ Demo Information</h2>
      <div class="warning">
        <p>⚠️ <strong>Development Setup:</strong> This demo uses WebSocket transport with direct API key for simplicity.</p>
        <p>For production WebRTC implementation, a backend service should generate ephemeral client keys.</p>
      </div>
    </div>

    <div class="section">
      <h2>📊 Session Status</h2>
      <div id="status" class="response-area">
        <p>Status: Disconnected</p>
        <p>Ready to connect to OpenAI's realtime voice model.</p>
      </div>
    </div>
  </div>
`

class VoiceAgentDemo {
  private session: RealtimeSession | null = null
  private micStream: MediaStream | null = null
  private connectBtn: HTMLButtonElement
  private disconnectBtn: HTMLButtonElement
  private statusDiv: HTMLDivElement
  private connectionStatusDiv: HTMLDivElement

  constructor() {
    this.connectBtn = document.querySelector<HTMLButtonElement>('#connect')!
    this.disconnectBtn = document.querySelector<HTMLButtonElement>('#disconnect')!
    this.statusDiv = document.querySelector<HTMLDivElement>('#status')!
    this.connectionStatusDiv = document.querySelector<HTMLDivElement>('#connection-status')!

    this.setupEventListeners()
  }

  private setupEventListeners() {
    this.connectBtn.addEventListener('click', () => this.connect())
    this.disconnectBtn.addEventListener('click', () => this.disconnect())
  }

  private updateStatus(message: string) {
    this.statusDiv.innerHTML = `<p>Status: ${message}</p>\n<p>🕒 ${new Date().toLocaleTimeString()}</p>`
  }

  private updateConnectionStatus(status: 'connected' | 'connecting' | 'disconnected' | 'error', message: string) {
    this.connectionStatusDiv.className = `status-value ${status}`
    this.connectionStatusDiv.textContent = message
  }

  private async connect() {
    try {
      this.updateStatus('🔄 Creating voice agent...')
      this.updateConnectionStatus('connecting', 'Connecting...')
      this.connectBtn.disabled = true

      console.log('Creating agent and session...')

      const agent = new RealtimeAgent({
        name: 'Assistant',
        instructions: 'You are a helpful voice assistant for the Hackathon Tech Europe demo. Speak naturally and conversationally.',
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
      this.updateStatus('🎉 Connected successfully!\n\n✨ You can now speak naturally with the AI assistant.\n💬 It will respond in real-time using OpenAI\'s voice model.')
      this.updateConnectionStatus('connected', 'Connected')
      this.connectBtn.disabled = true
      this.disconnectBtn.disabled = false

      // Add event listeners after successful connection
      this.session.on('error', (error) => {
        console.error('Session error:', error)
        this.updateStatus(`❌ Session error: ${error}`)
        this.updateConnectionStatus('error', 'Error')
      })

    } catch (error) {
      console.error('Connection failed:', error)
      const errorMessage = error instanceof Error ? error.message : String(error)
      this.updateStatus(`❌ Connection failed: ${errorMessage}\n\n💡 This might be due to:\n• Browser extension conflicts\n• Network connectivity issues\n• API key problems`)
      this.updateConnectionStatus('error', 'Failed')
      this.connectBtn.disabled = false
    }
  }

  private disconnect() {
    if (this.session) {
      this.session.close()
      this.session = null
    }

    if (this.micStream) {
      this.micStream.getTracks().forEach(track => track.stop())
      this.micStream = null
    }

    this.updateStatus('🔌 Disconnected from voice agent\n\nReady to reconnect when needed.')
    this.updateConnectionStatus('disconnected', 'Disconnected')
    this.connectBtn.disabled = false
    this.disconnectBtn.disabled = true
  }
}

new VoiceAgentDemo()

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
