import { ref, onUnmounted } from 'vue'

export type ConnectionStatus = 'connecting' | 'connected' | 'reconnecting' | 'disconnected' | 'error'

export interface ResilientWebSocketOptions {
  url: string
  protocols?: string | string[]
  maxReconnectAttempts?: number
  heartbeatIntervalMs?: number
  heartbeatMessage?: string | object
  onMessage?: (data: any, rawEvent: MessageEvent) => void
  onOpen?: (event: Event) => void
  onClose?: (event: CloseEvent) => void
  onError?: (event: Event) => void
}

export function useResilientWebSocket(options: ResilientWebSocketOptions) {
  const status = ref<ConnectionStatus>('disconnected')
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const lastError = ref<string | null>(null)
  const offlineQueueCount = ref(0)

  let ws: WebSocket | null = null
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null
  let heartbeatInterval: ReturnType<typeof setInterval> | null = null
  let isManuallyClosed = false

  const offlineQueue: string[] = []
  const maxAttempts = options.maxReconnectAttempts ?? 10
  const heartbeatMs = options.heartbeatIntervalMs ?? 25000

  function connect() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    isManuallyClosed = false
    status.value = reconnectAttempts.value > 0 ? 'reconnecting' : 'connecting'

    try {
      ws = new WebSocket(options.url, options.protocols)

      ws.onopen = (event) => {
        status.value = 'connected'
        isConnected.value = true
        reconnectAttempts.value = 0
        lastError.value = null
        startHeartbeat()
        flushOfflineQueue()
        options.onOpen?.(event)
      }

      ws.onmessage = (event) => {
        let parsed = event.data
        try {
          parsed = JSON.parse(event.data)
        } catch {
          // Keep as raw text
        }
        options.onMessage?.(parsed, event)
      }

      ws.onerror = (event) => {
        lastError.value = 'WebSocket connection error'
        status.value = 'error'
        options.onError?.(event)
      }

      ws.onclose = (event) => {
        stopHeartbeat()
        isConnected.value = false
        options.onClose?.(event)

        if (!isManuallyClosed) {
          scheduleReconnect()
        } else {
          status.value = 'disconnected'
        }
      }
    } catch (err: any) {
      lastError.value = err?.message || 'Failed to create WebSocket instance'
      status.value = 'error'
      scheduleReconnect()
    }
  }

  function scheduleReconnect() {
    if (reconnectAttempts.value >= maxAttempts) {
      status.value = 'disconnected'
      lastError.value = `Max reconnection attempts (${maxAttempts}) reached`
      return
    }

    status.value = 'reconnecting'
    reconnectAttempts.value++

    // Exponential backoff with jitter: min(1000 * 2^attempt, 15000) + jitter
    const delay = Math.min(1000 * Math.pow(1.8, reconnectAttempts.value - 1), 15000) + Math.random() * 500

    if (reconnectTimeout) clearTimeout(reconnectTimeout)
    reconnectTimeout = setTimeout(() => {
      connect()
    }, delay)
  }

  function startHeartbeat() {
    stopHeartbeat()
    heartbeatInterval = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        const ping = options.heartbeatMessage ?? { type: 'ping', timestamp: Date.now() }
        const payload = typeof ping === 'string' ? ping : JSON.stringify(ping)
        ws.send(payload)
      }
    }, heartbeatMs)
  }

  function stopHeartbeat() {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }

  function flushOfflineQueue() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return
    while (offlineQueue.length > 0) {
      const msg = offlineQueue.shift()
      if (msg) {
        ws.send(msg)
      }
    }
    offlineQueueCount.value = 0
  }

  function send(data: string | object): boolean {
    const payload = typeof data === 'string' ? data : JSON.stringify(data)

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(payload)
      return true
    } else {
      // Queue offline message to be sent upon reconnection
      offlineQueue.push(payload)
      offlineQueueCount.value = offlineQueue.length
      if (status.value === 'disconnected') {
        connect()
      }
      return false
    }
  }

  function disconnect() {
    isManuallyClosed = true
    stopHeartbeat()
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
    status.value = 'disconnected'
    isConnected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    status,
    isConnected,
    reconnectAttempts,
    lastError,
    offlineQueueCount,
    connect,
    disconnect,
    send,
  }
}
