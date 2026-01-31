/**
 * RakshakAI - WebSocket Client
 * Manages real-time connection to the backend for audio streaming
 */

import { Platform } from 'react-native';

// WebSocket message types
export type WebSocketMessageType = 
  | 'audio_chunk'
  | 'threat_update'
  | 'threat_alert'
  | 'ai_response'
  | 'handoff_request'
  | 'handoff_confirmed'
  | 'terminate_bait'
  | 'bait_terminated'
  | 'transcript'
  | 'ping'
  | 'pong'
  | 'error';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  payload: any;
  timestamp?: string;
}

/**
 * WebSocket Client for real-time communication with RakshakAI backend
 * 
 * This client handles:
 * - Connection management with automatic reconnection
 * - Audio chunk streaming to backend
 * - Receiving threat updates and alerts
 * - AI handoff coordination
 * - Transcript updates
 */
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private callId: string;
  private messageHandlers: ((message: WebSocketMessage) => void)[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;
  private messageQueue: WebSocketMessage[] = [];

  constructor(callId: string) {
    this.callId = callId;
  }

  /**
   * Connect to the WebSocket server
   */
  async connect(): Promise<void> {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.isConnecting = true;

    return new Promise((resolve, reject) => {
      try {
        // Backend WebSocket URL
        // In production, this would come from environment config
        const wsUrl = `wss://api.rakshak.ai/ws/call/${this.callId}`;
        
        // For development/testing, use localhost
        // const wsUrl = `ws://localhost:8000/ws/call/${this.callId}`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected for call:', this.callId);
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          
          // Send any queued messages
          this.flushMessageQueue();
          
          // Start keep-alive ping
          this.startPingInterval();
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          this.isConnecting = false;
          
          // Attempt reconnection if not intentionally closed
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect();
          }
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      // Close cleanly
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
  }

  /**
   * Send a message to the server
   */
  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      // Queue message for when connection is established
      this.messageQueue.push(message);
    }
  }

  /**
   * Send audio chunk to the server
   */
  sendAudioChunk(audioBase64: string, sequenceNumber: number, isFinal: boolean = false): void {
    this.send({
      type: 'audio_chunk',
      payload: {
        call_id: this.callId,
        audio_data: audioBase64,
        sequence_number: sequenceNumber,
        is_final: isFinal,
        timestamp: Date.now(),
      },
    });
  }

  /**
   * Request AI handoff
   */
  requestHandoff(persona: string = 'confused_senior', extractionEnabled: boolean = true): void {
    this.send({
      type: 'handoff_request',
      payload: {
        persona,
        extraction_enabled: extractionEnabled,
      },
    });
  }

  /**
   * Terminate AI bait agent
   */
  terminateBait(): void {
    this.send({
      type: 'terminate_bait',
      payload: {},
    });
  }

  /**
   * Register a message handler
   */
  onMessage(handler: (message: WebSocketMessage) => void): void {
    this.messageHandlers.push(handler);
  }

  /**
   * Remove a message handler
   */
  offMessage(handler: (message: WebSocketMessage) => void): void {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: WebSocketMessage): void {
    // Notify all registered handlers
    this.messageHandlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('Message handler error:', error);
      }
    });
  }

  /**
   * Attempt to reconnect
   */
  private attemptReconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, delay);
  }

  /**
   * Flush queued messages
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  /**
   * Start keep-alive ping interval
   */
  private pingInterval: NodeJS.Timeout | null = null;

  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send({
          type: 'ping',
          payload: { timestamp: Date.now() },
        });
      }
    }, 30000); // Ping every 30 seconds
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
}

/**
 * Singleton instance for app-wide WebSocket management
 */
let globalWebSocketClient: WebSocketClient | null = null;

export const setGlobalWebSocketClient = (client: WebSocketClient | null): void => {
  globalWebSocketClient = client;
};

export const getGlobalWebSocketClient = (): WebSocketClient | null => {
  return globalWebSocketClient;
};
