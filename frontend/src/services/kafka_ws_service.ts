/**
 * WebSocket bridge for real-time frontend notifications from Kafka
 */

interface NotificationMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface WebSocketBridgeOptions {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

class KafkaWebSocketBridge {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectInterval: number;
  private maxReconnectAttempts: number;
  private reconnectAttempts: number = 0;
  private listeners: Map<string, Array<(data: any) => void>> = new Map();
  private isConnected: boolean = false;

  constructor(options: WebSocketBridgeOptions) {
    this.url = options.url;
    this.reconnectInterval = options.reconnectInterval || 5000;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
  }

  /**
   * Connect to the WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('Connected to Kafka WebSocket bridge');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: NotificationMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('Disconnected from Kafka WebSocket bridge');
          this.isConnected = false;

          // Attempt to reconnect if we haven't exceeded max attempts
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
              this.reconnectAttempts++;
              console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
              this.connect();
            }, this.reconnectInterval);
          }
        };
      } catch (error) {
        console.error('Failed to establish WebSocket connection:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: NotificationMessage): void {
    // Notify all registered listeners for this message type
    const listeners = this.listeners.get(message.type) || [];
    listeners.forEach(listener => {
      try {
        listener(message.data);
      } catch (error) {
        console.error(`Error in ${message.type} listener:`, error);
      }
    });

    // Also notify general listeners
    const generalListeners = this.listeners.get('*') || [];
    generalListeners.forEach(listener => {
      try {
        listener(message);
      } catch (error) {
        console.error('Error in general listener:', error);
      }
    });
  }

  /**
   * Subscribe to a specific notification type
   */
  subscribe(type: string, callback: (data: any) => void): void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }

    const listeners = this.listeners.get(type)!;
    listeners.push(callback);
  }

  /**
   * Unsubscribe from a specific notification type
   */
  unsubscribe(type: string, callback: (data: any) => void): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * Send a message to the WebSocket server
   */
  sendMessage(message: NotificationMessage): void {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected, cannot send message:', message);
    }
  }

  /**
   * Check if the WebSocket is currently connected
   */
  isConnectedToKafka(): boolean {
    return this.isConnected;
  }

  /**
   * Subscribe to task-related notifications
   */
  subscribeToTaskNotifications(callback: (data: any) => void): void {
    this.subscribe('task.created', callback);
    this.subscribe('task.updated', callback);
    this.subscribe('task.deleted', callback);
    this.subscribe('task.completed', callback);
  }

  /**
   * Subscribe to reminder notifications
   */
  subscribeToReminderNotifications(callback: (data: any) => void {
    this.subscribe('task.reminder', callback);
  }

  /**
   * Subscribe to audit notifications
   */
  subscribeToAuditNotifications(callback: (data: any) => void {
    this.subscribe('audit.log', callback);
  }
}

// Export a singleton instance
const kafkaWebSocketBridge = new KafkaWebSocketBridge({
  url: process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws/notifications'
});

export default kafkaWebSocketBridge;
export { KafkaWebSocketBridge, NotificationMessage };