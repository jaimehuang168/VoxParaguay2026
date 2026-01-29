"use client";

/**
 * VoxParaguay 2026 - Mapa de Opinión Pública
 * Visualización interactiva por departamento con actualizaciones en tiempo real via WebSocket
 */

import { useState, useEffect, useCallback } from "react";
import { ParaguayMap, SentimentPerDept, DepartmentData } from "@/components/map";
import { useSentimentWebSocket } from "@/hooks/useSentimentWebSocket";
import {
  Map,
  BarChart3,
  Users,
  TrendingUp,
  Activity,
  RefreshCw,
  Wifi,
  WifiOff,
  Zap,
} from "lucide-react";

// Datos de ejemplo como fallback
const MOCK_SENTIMENT_DATA: SentimentPerDept = {
  "PY-ASU": 0.15,
  "PY-11": 0.08,
  "PY-10": 0.22,
  "PY-7": 0.35,
  "PY-2": -0.12,
  "PY-5": 0.05,
  "PY-9": 0.18,
  "PY-4": 0.28,
  "PY-6": -0.08,
  "PY-8": 0.32,
  "PY-12": 0.12,
  "PY-13": -0.15,
  "PY-14": 0.10,
  "PY-15": 0.08,
  "PY-19": 0.25,
  "PY-16": -0.22,
  "PY-1": -0.05,
  "PY-3": 0.38,
};

export default function MapaPage() {
  const [selectedDept, setSelectedDept] = useState<DepartmentData | null>(null);
  const [useMockData, setUseMockData] = useState(false);

  // WebSocket hook for real-time updates
  const {
    sentiments,
    isConnected,
    isReconnecting,
    lastUpdate,
    updateCount,
    error,
    reconnect,
    requestState,
  } = useSentimentWebSocket({
    onUpdate: (update) => {
      if (update.type === "sentiment_update") {
        console.log(
          `[Real-time] ${update.department_id}: ${update.average?.toFixed(3)}`
        );
      }
    },
    onConnectionChange: (connected) => {
      console.log(`[WS] Connection: ${connected ? "Connected" : "Disconnected"}`);
    },
  });

  // Use WebSocket data or fallback to mock
  const sentimentData = useMockData
    ? MOCK_SENTIMENT_DATA
    : Object.keys(sentiments).length > 0
      ? sentiments
      : null;

  // Calculate statistics
  const stats = sentimentData ? calculateStats(sentimentData) : null;

  // Toggle mock data mode
  const toggleMockData = () => {
    setUseMockData((prev) => !prev);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Map className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Mapa de Opinión Pública
              </h1>
              <p className="text-sm text-gray-500">
                Análisis de sentimiento en tiempo real - ISO 3166-2:PY
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Connection Status */}
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
                isConnected
                  ? "bg-green-100 text-green-700"
                  : isReconnecting
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-red-100 text-red-700"
              }`}
            >
              {isConnected ? (
                <>
                  <Wifi className="w-4 h-4" />
                  <span>En vivo</span>
                  <Zap className="w-3 h-3 text-yellow-500" />
                </>
              ) : isReconnecting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Reconectando...</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4" />
                  <span>Desconectado</span>
                </>
              )}
            </div>

            {/* Mock Data Toggle */}
            <button
              onClick={toggleMockData}
              className={`px-3 py-1.5 rounded-lg text-sm transition ${
                useMockData
                  ? "bg-orange-100 text-orange-700 hover:bg-orange-200"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {useMockData ? "Datos Mock" : "Datos en Vivo"}
            </button>

            {/* Reconnect Button */}
            {!isConnected && !isReconnecting && (
              <button
                onClick={reconnect}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <RefreshCw className="w-4 h-4" />
                Reconectar
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                Total Encuestas
              </p>
              <p className="text-lg font-semibold text-gray-900">
                {stats?.totalEncuestas.toLocaleString("es-PY") || "—"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp
              className={`w-5 h-5 ${(stats?.sentimientoNacional ?? 0) >= 0 ? "text-green-500" : "text-red-500"}`}
            />
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                Sentimiento Nacional
              </p>
              <p
                className={`text-lg font-semibold ${(stats?.sentimientoNacional ?? 0) >= 0 ? "text-green-600" : "text-red-600"}`}
              >
                {stats
                  ? `${stats.sentimientoNacional >= 0 ? "+" : ""}${(stats.sentimientoNacional * 100).toFixed(0)}%`
                  : "—"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                Departamentos
              </p>
              <p className="text-lg font-semibold text-gray-900">
                {stats ? (
                  <>
                    18{" "}
                    <span className="text-sm text-green-600">
                      ({stats.positivos} positivos)
                    </span>
                  </>
                ) : (
                  "—"
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                Actualizaciones
              </p>
              <p className="text-lg font-semibold text-gray-900">
                {updateCount > 0 ? (
                  <span className="text-blue-600">{updateCount}</span>
                ) : (
                  "—"
                )}
              </p>
            </div>
          </div>
          {lastUpdate && lastUpdate.type === "sentiment_update" && (
            <div className="flex items-center gap-2 ml-auto">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="text-sm text-gray-600">
                Última: <strong>{lastUpdate.department_id}</strong>
                {lastUpdate.average !== undefined && (
                  <span
                    className={
                      lastUpdate.average >= 0
                        ? "text-green-600 ml-1"
                        : "text-red-600 ml-1"
                    }
                  >
                    {lastUpdate.average >= 0 ? "+" : ""}
                    {(lastUpdate.average * 100).toFixed(1)}%
                  </span>
                )}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-2 flex items-center justify-between">
          <span className="text-sm text-red-700">{error}</span>
          <button
            onClick={reconnect}
            className="text-sm text-red-700 underline hover:no-underline"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Main Content */}
      <main className="flex h-[calc(100vh-180px)]">
        {!sentimentData && !useMockData ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              {isConnected ? (
                <>
                  <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
                  <p className="text-gray-600">
                    Esperando datos del servidor...
                  </p>
                  <p className="text-sm text-gray-400 mt-2">
                    Ejecute mock_data_stream.py para generar datos de prueba
                  </p>
                </>
              ) : (
                <>
                  <WifiOff className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Sin conexión al servidor</p>
                  <button
                    onClick={reconnect}
                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Conectar
                  </button>
                  <button
                    onClick={toggleMockData}
                    className="mt-4 ml-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                  >
                    Usar datos de prueba
                  </button>
                </>
              )}
            </div>
          </div>
        ) : (
          <ParaguayMap
            sentimentData={sentimentData}
            onDepartmentSelect={setSelectedDept}
            className="flex-1"
            showLegend={true}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            VoxParaguay 2026 - Sistema de Encuestas y Análisis de Opinión Pública
          </span>
          <span>
            {isConnected && (
              <span className="text-green-600 mr-3">
                <Wifi className="w-3 h-3 inline mr-1" />
                WebSocket activo
              </span>
            )}
            {selectedDept
              ? `Seleccionado: ${selectedDept.nombre} (${selectedDept.id})`
              : "Haga clic en un departamento para ver el análisis"}
          </span>
        </div>
      </footer>
    </div>
  );
}

// Calculate statistics from sentiment data
function calculateStats(data: SentimentPerDept) {
  const values = Object.values(data);
  if (values.length === 0) return null;

  const sentimientoNacional =
    values.reduce((sum, v) => sum + v, 0) / values.length;
  const positivos = values.filter((v) => v > 0.1).length;
  const negativos = values.filter((v) => v < -0.1).length;

  return {
    totalEncuestas: values.length * 500, // Estimated from data points
    sentimientoNacional,
    positivos,
    negativos,
    neutral: values.length - positivos - negativos,
  };
}
