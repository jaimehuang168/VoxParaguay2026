/**
 * VoxParaguay 2026 - Real-time Sentiment WebSocket Hook
 *
 * Connects to the backend WebSocket for live sentiment updates.
 * Automatically reconnects on disconnect and provides current sentiment state.
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { SentimentPerDept } from "@/components/map/ParaguayMap";

interface SentimentUpdate {
  type: "sentiment_update" | "initial_state" | "state" | "pong";
  department_id?: string;
  sentiment_score?: number;
  average?: number;
  total_count?: number;
  timestamp?: string;
  sentiments?: SentimentPerDept;
  message?: string;
  metadata?: {
    name?: string;
    region?: string;
    topic?: string;
    channel?: string;
  };
}

interface UseSentimentWebSocketOptions {
  /** WebSocket URL (default: auto-detect based on window location) */
  url?: string;
  /** Enable automatic reconnection (default: true) */
  autoReconnect?: boolean;
  /** Reconnect interval in ms (default: 3000) */
  reconnectInterval?: number;
  /** Maximum reconnect attempts (default: 10) */
  maxReconnectAttempts?: number;
  /** Callback when a new sentiment update arrives */
  onUpdate?: (update: SentimentUpdate) => void;
  /** Callback when connection status changes */
  onConnectionChange?: (connected: boolean) => void;
}

interface UseSentimentWebSocketReturn {
  /** Current sentiment data for all departments */
  sentiments: SentimentPerDept;
  /** WebSocket connection status */
  isConnected: boolean;
  /** Whether currently attempting to reconnect */
  isReconnecting: boolean;
  /** Last received update */
  lastUpdate: SentimentUpdate | null;
  /** Total number of updates received this session */
  updateCount: number;
  /** Error message if any */
  error: string | null;
  /** Manually trigger reconnection */
  reconnect: () => void;
  /** Request current state from server */
  requestState: () => void;
}

/**
 * Default WebSocket URL based on current location
 */
function getDefaultWsUrl(): string {
  if (typeof window === "undefined") {
    return "ws://localhost:8000/ws/sentiment";
  }

  // Check for explicit WS URL first
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL;
  if (wsUrl) {
    return `${wsUrl}/ws/sentiment`;
  }

  // Then check for WS host
  const wsHost = process.env.NEXT_PUBLIC_WS_HOST;
  if (wsHost) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${wsHost}/ws/sentiment`;
  }

  // Default fallback - use same host as page but port 8000
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//localhost:8000/ws/sentiment`;
}

/**
 * React hook for real-time sentiment updates via WebSocket.
 *
 * @example
 * ```tsx
 * const { sentiments, isConnected, lastUpdate } = useSentimentWebSocket();
 *
 * return (
 *   <ParaguayMap sentimentData={sentiments} />
 * );
 * ```
 */
export function useSentimentWebSocket(
  options: UseSentimentWebSocketOptions = {}
): UseSentimentWebSocketReturn {
  const {
    url = getDefaultWsUrl(),
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    onUpdate,
    onConnectionChange,
  } = options;

  // State
  const [sentiments, setSentiments] = useState<SentimentPerDept>({});
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<SentimentUpdate | null>(null);
  const [updateCount, setUpdateCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Handle incoming message
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const data: SentimentUpdate = JSON.parse(event.data);
        setLastUpdate(data);
        setUpdateCount((prev) => prev + 1);

        switch (data.type) {
          case "initial_state":
          case "state":
            // Full state update
            if (data.sentiments) {
              setSentiments(data.sentiments);
            }
            break;

          case "sentiment_update":
            // Single department update
            if (data.department_id && data.average !== undefined) {
              setSentiments((prev) => ({
                ...prev,
                [data.department_id!]: data.average!,
              }));
            }
            break;

          case "pong":
            // Ping response, connection is alive
            break;
        }

        // Call user callback
        onUpdate?.(data);
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    },
    [onUpdate]
  );

  // Connect to WebSocket
  const connect = useCallback(() => {
    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Clear existing ping interval
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }

    setError(null);

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[WS] Connected to sentiment stream");
        setIsConnected(true);
        setIsReconnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;
        onConnectionChange?.(true);

        // Start ping interval to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send("ping");
          }
        }, 30000);
      };

      ws.onmessage = handleMessage;

      ws.onclose = (event) => {
        console.log("[WS] Disconnected:", event.code, event.reason);
        setIsConnected(false);
        onConnectionChange?.(false);

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }

        // Attempt reconnection if enabled and not a clean close
        if (autoReconnect && event.code !== 1000) {
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            setIsReconnecting(true);
            reconnectAttemptsRef.current += 1;
            console.log(
              `[WS] Reconnecting in ${reconnectInterval}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
            );

            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, reconnectInterval);
          } else {
            setError("Maximum reconnection attempts reached");
            setIsReconnecting(false);
          }
        }
      };

      ws.onerror = (event) => {
        console.error("[WS] Error:", event);
        setError("WebSocket connection error");
      };
    } catch (err) {
      console.error("[WS] Failed to connect:", err);
      setError("Failed to establish WebSocket connection");
    }
  }, [
    url,
    autoReconnect,
    reconnectInterval,
    maxReconnectAttempts,
    handleMessage,
    onConnectionChange,
  ]);

  // Manual reconnect
  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    setIsReconnecting(false);
    connect();
  }, [connect]);

  // Request current state
  const requestState = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send("get_state");
    }
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      // Cleanup on unmount
      if (wsRef.current) {
        wsRef.current.close(1000, "Component unmounted");
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [connect]);

  return {
    sentiments,
    isConnected,
    isReconnecting,
    lastUpdate,
    updateCount,
    error,
    reconnect,
    requestState,
  };
}

export default useSentimentWebSocket;
