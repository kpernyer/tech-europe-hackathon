/**
 * WebSocket-based audio streaming handler for OpenAI's Realtime API
 * Alternative to WebRTC implementation
 */

interface AudioChunk {
  audio: string; // base64 encoded audio
  transcript?: string;
}

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export class WebSocketAudioHandler {
  private ws: WebSocket | null = null
  private mediaRecorder: MediaRecorder | null = null
  private audioContext: AudioContext | null = null
  private audioChunks: Blob[] = []
  private isRecording = false
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private isConnectedToOpenAI = false
  private audioQueue: string[] = []
  private isPlayingAudio = false

  constructor(
    private apiKey: string,
    private onStatusChange: (status: 'connecting' | 'connected' | 'disconnected' | 'error', message: string) => void,
    private onTranscript: (text: string, isUser: boolean) => void,
    private onAudio: (audioData: string) => void
  ) {}

  async connect(): Promise<void> {
    try {
      this.onStatusChange('connecting', 'Connecting to WebSocket...')

      // Get user media first
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 24000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })

      // Initialize audio context
      this.audioContext = new AudioContext({ sampleRate: 24000 })

      // Connect to local WebSocket proxy instead of directly to OpenAI
      const wsUrl = `ws://localhost:8787/api/realtime-ws`
      this.ws = new WebSocket(wsUrl)

      // Set up WebSocket event handlers
      this.setupWebSocketHandlers()

      // Set up media recorder for audio streaming
      this.setupMediaRecorder(stream)

      // Wait for connection
      await this.waitForConnection()

      this.onStatusChange('connected', 'Connected via WebSocket')
      this.reconnectAttempts = 0

    } catch (error) {
      console.error('WebSocket connection failed:', error)
      this.onStatusChange('error', `Connection failed: ${error}`)
      throw error
    }
  }

  private setupWebSocketHandlers(): void {
    if (!this.ws) return

    this.ws.onopen = () => {
      console.log('WebSocket connected to proxy')
      // Send initialization message with ephemeral token
      this.ws!.send(JSON.stringify({
        type: 'init',
        ephemeralToken: this.apiKey
      }))
    }

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        this.handleWebSocketMessage(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      this.onStatusChange('disconnected', 'Connection closed')

      if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.attemptReconnect()
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.onStatusChange('error', 'WebSocket error')
    }
  }

  private async attemptReconnect(): Promise<void> {
    this.reconnectAttempts++
    this.onStatusChange('connecting', `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    await new Promise(resolve => setTimeout(resolve, this.reconnectDelay * this.reconnectAttempts))

    try {
      await this.connect()
    } catch (error) {
      console.error('Reconnection failed:', error)
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.onStatusChange('error', 'Max reconnection attempts reached')
      }
    }
  }

  private sendSessionUpdate(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.log('Cannot send session update - WebSocket not ready')
      return
    }

    if (!this.isConnectedToOpenAI) {
      console.log('Cannot send session update - not connected to OpenAI yet')
      return
    }

    console.log('Sending session update to OpenAI')

    const sessionConfig = {
      type: 'session.update',
      session: {
        modalities: ['text', 'audio'],
        instructions: 'You are a helpful AI assistant. Respond naturally and conversationally.',
        voice: 'alloy',
        input_audio_format: 'pcm16',
        output_audio_format: 'pcm16',
        input_audio_transcription: {
          model: 'whisper-1'
        },
        turn_detection: {
          type: 'server_vad',
          threshold: 0.5,
          prefix_padding_ms: 300,
          silence_duration_ms: 200
        },
        tools: [],
        tool_choice: 'auto',
        temperature: 0.8,
        max_response_output_tokens: 4096
      }
    }

    this.ws.send(JSON.stringify(sessionConfig))
  }

  private handleWebSocketMessage(message: WebSocketMessage): void {
    // Handle proxy-specific messages
    if (message.type === 'connected') {
      console.log('Proxy connected to OpenAI')
      this.isConnectedToOpenAI = true
      this.onStatusChange('connected', 'Connected via WebSocket')
      this.sendSessionUpdate()
      return
    }

    if (message.type === 'disconnected') {
      console.log('Proxy disconnected from OpenAI')
      this.isConnectedToOpenAI = false
      this.onStatusChange('disconnected', 'Connection closed')
      return
    }

    // Handle standard OpenAI messages
    switch (message.type) {
      case 'session.created':
        console.log('Session created:', message)
        break

      case 'session.updated':
        console.log('Session updated:', message)
        break

      case 'input_audio_buffer.committed':
        console.log('Audio buffer committed')
        break

      case 'input_audio_buffer.speech_started':
        console.log('Speech started')
        break

      case 'input_audio_buffer.speech_stopped':
        console.log('Speech stopped')
        break

      case 'conversation.item.input_audio_transcription.completed':
        if (message.transcript) {
          this.onTranscript(message.transcript, true)
        }
        break

      case 'response.audio_transcript.delta':
        if (message.delta) {
          this.onTranscript(message.delta, false)
        }
        break

      case 'response.audio.delta':
        if (message.delta) {
          console.log('Received audio delta:', message.delta.length, 'characters')
          this.onAudio(message.delta)
          this.playAudioDelta(message.delta)
        }
        break

      case 'response.done':
        console.log('Response completed')
        break

      case 'error':
        console.error('Server error:', message)
        console.error('Error details:', JSON.stringify(message.error, null, 2))
        this.onStatusChange('error', `Server error: ${message.error?.message || 'Unknown error'}`)
        break

      default:
        console.log('Unhandled message type:', message.type)
    }
  }

  private setupMediaRecorder(stream: MediaStream): void {
    try {
      // Try different audio formats for compatibility with OpenAI
      let options = {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 24000
      }

      // Fallback options in order of preference
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options.mimeType = 'audio/webm'
      }

      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: 'audio/mp4' } as any
      }

      console.log('Using audio format:', options.mimeType)

      this.mediaRecorder = new MediaRecorder(stream, options)

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          console.log('Audio chunk received:', event.data.size, 'bytes')
          this.audioChunks.push(event.data)
          this.processAudioChunk(event.data)
        }
      }

      this.mediaRecorder.onstop = () => {
        console.log('Recording stopped')
        this.isRecording = false
      }

      this.mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event)
      }

      // Start recording in small chunks for real-time streaming
      this.startRecording()

    } catch (error) {
      console.error('Failed to setup media recorder:', error)
      throw error
    }
  }

  private startRecording(): void {
    if (this.mediaRecorder && !this.isRecording) {
      this.mediaRecorder.start(100) // Record in 100ms chunks
      this.isRecording = true
    }
  }

  private async processAudioChunk(chunk: Blob): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.isConnectedToOpenAI) {
      console.log('Cannot process audio - WebSocket not ready or not connected to OpenAI')
      return
    }

    try {
      // For WebSocket, we need to convert audio to PCM16 format
      // This is more complex than the WebRTC version which handles this automatically
      const buffer = await chunk.arrayBuffer()

      // Try to decode the audio and convert to PCM16
      const pcmData = await this.convertToPCM16(buffer)

      if (pcmData) {
        const base64Audio = btoa(String.fromCharCode(...new Uint8Array(pcmData)))
        console.log('Sending PCM16 audio chunk to OpenAI:', base64Audio.length, 'characters')

        // Send audio data to OpenAI
        const audioMessage = {
          type: 'input_audio_buffer.append',
          audio: base64Audio
        }

        this.ws.send(JSON.stringify(audioMessage))
      }

    } catch (error) {
      console.error('Failed to process audio chunk:', error)
    }
  }

  private async convertToPCM16(audioBuffer: ArrayBuffer): Promise<ArrayBuffer | null> {
    if (!this.audioContext) return null

    try {
      // Decode the audio data
      const decodedData = await this.audioContext.decodeAudioData(audioBuffer.slice())

      // Convert to mono if stereo
      const channelData = decodedData.getChannelData(0)

      // Convert float32 samples to int16 PCM
      const pcm16 = new Int16Array(channelData.length)
      for (let i = 0; i < channelData.length; i++) {
        // Convert float (-1 to 1) to int16 (-32768 to 32767)
        pcm16[i] = Math.max(-32768, Math.min(32767, channelData[i] * 32768))
      }

      return pcm16.buffer

    } catch (error) {
      console.error('Failed to convert audio to PCM16:', error)
      return null
    }
  }

  private waitForConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.ws) {
        reject(new Error('WebSocket not initialized'))
        return
      }

      if (this.ws.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      const timeout = setTimeout(() => {
        reject(new Error('Connection timeout'))
      }, 10000)

      this.ws.onopen = () => {
        clearTimeout(timeout)
        resolve()
      }

      this.ws.onerror = () => {
        clearTimeout(timeout)
        reject(new Error('WebSocket connection failed'))
      }
    })
  }

  startListening(): void {
    if (this.mediaRecorder && !this.isRecording) {
      this.startRecording()
    }
  }

  stopListening(): void {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop()
    }
  }

  sendTextMessage(text: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.isConnectedToOpenAI) return

    const message = {
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [{
          type: 'input_text',
          text: text
        }]
      }
    }

    this.ws.send(JSON.stringify(message))

    // Trigger response
    this.ws.send(JSON.stringify({
      type: 'response.create'
    }))
  }

  private async playAudioDelta(base64Audio: string): Promise<void> {
    if (!this.audioContext) return

    try {
      // Decode base64 to binary
      const binaryString = atob(base64Audio)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }

      // Create audio buffer from PCM16 data
      const audioBuffer = await this.audioContext.decodeAudioData(bytes.buffer)

      // Create audio source and play
      const source = this.audioContext.createBufferSource()
      source.buffer = audioBuffer
      source.connect(this.audioContext.destination)
      source.start()

      console.log('Playing audio delta')

    } catch (error) {
      console.error('Failed to play audio delta:', error)

      // Fallback: try to play as blob URL
      try {
        const binaryString = atob(base64Audio)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }

        const blob = new Blob([bytes], { type: 'audio/pcm' })
        const audioUrl = URL.createObjectURL(blob)
        const audio = new Audio(audioUrl)
        await audio.play()

        // Clean up
        audio.onended = () => URL.revokeObjectURL(audioUrl)

      } catch (fallbackError) {
        console.error('Fallback audio playback failed:', fallbackError)
      }
    }
  }

  disconnect(): void {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop()
    }

    if (this.ws) {
      this.ws.close(1000, 'User disconnected')
      this.ws = null
    }

    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }

    this.audioChunks = []
    this.audioQueue = []
    this.isRecording = false
    this.isPlayingAudio = false
    this.reconnectAttempts = 0
    this.isConnectedToOpenAI = false
  }
}