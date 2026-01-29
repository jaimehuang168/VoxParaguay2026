"use client";

/**
 * VoxParaguay 2026 - Mapa Interactivo de Paraguay
 * Visualización de datos por departamento con TopoJSON y códigos ISO 3166-2:PY
 */

import React, { useState, useCallback, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { X, TrendingUp, TrendingDown, Minus, Loader2, Shield, AlertCircle } from "lucide-react";

// ============ AI SUMMARY API TYPES ============

interface AISummaryResponse {
  department_id: string;
  department_name: string;
  region: string;
  sentiment_average: number | null;
  total_responses: number;
  summary: string;
  generated_at: string;
  topics_analyzed: string[];
  compliance_note: string;
}

// ============ TIPOS ============

export interface DepartmentData {
  id: string;  // ISO code: PY-XX
  nombre: string;
  capital: string;
  poblacion: number;
  encuestasCompletadas: number;
  sentimientoPromedio: number; // -1 a 1
  temas: {
    tema: string;
    menciones: number;
    sentimiento: number;
  }[];
}

// Datos de sentimiento del backend API (clave: PY-XX)
export interface SentimentPerDept {
  [isoCode: string]: number; // PY-ASU: 0.15, PY-1: 0.08, etc.
}

// TopoJSON geometry para cada departamento
interface DepartmentGeometry {
  id: string;        // ISO 3166-2:PY code
  path: string;      // SVG path
  labelX: number;    // Label position
  labelY: number;
  labelText: string; // Display name
  shortLabel?: string; // Short label for small areas
}

// ============ TOPOJSON: DEPARTAMENTOS DE PARAGUAY ============
// ISO 3166-2:PY codes: https://en.wikipedia.org/wiki/ISO_3166-2:PY

const PARAGUAY_TOPOJSON: DepartmentGeometry[] = [
  // Región Occidental (Chaco)
  { id: "PY-16", path: "M50 20 L180 20 L180 120 L50 120 Z", labelX: 115, labelY: 75, labelText: "Alto Paraguay" },
  { id: "PY-19", path: "M50 120 L180 120 L180 220 L50 220 Z", labelX: 115, labelY: 175, labelText: "Boquerón" },
  { id: "PY-15", path: "M50 220 L180 220 L180 320 L120 320 L120 350 L50 350 Z", labelX: 115, labelY: 280, labelText: "Pdte. Hayes" },

  // Región Oriental
  { id: "PY-1", path: "M180 80 L280 80 L280 140 L180 140 Z", labelX: 230, labelY: 115, labelText: "Concepción" },
  { id: "PY-13", path: "M280 80 L350 80 L350 140 L280 140 Z", labelX: 315, labelY: 115, labelText: "Amambay" },
  { id: "PY-2", path: "M180 140 L280 140 L280 200 L180 200 Z", labelX: 230, labelY: 175, labelText: "San Pedro" },
  { id: "PY-14", path: "M280 140 L370 140 L370 220 L280 220 Z", labelX: 325, labelY: 185, labelText: "Canindeyú" },
  { id: "PY-3", path: "M180 200 L230 200 L230 260 L180 260 Z", labelX: 205, labelY: 235, labelText: "Cordillera" },
  { id: "PY-5", path: "M230 200 L320 200 L320 270 L230 270 Z", labelX: 275, labelY: 240, labelText: "Caaguazú" },
  { id: "PY-10", path: "M320 200 L380 200 L380 310 L320 310 Z", labelX: 350, labelY: 260, labelText: "Alto Paraná" },
  { id: "PY-ASU", path: "M150 270 L180 270 L180 300 L150 300 Z", labelX: 165, labelY: 288, labelText: "Asunción", shortLabel: "ASU" },
  { id: "PY-11", path: "M180 260 L230 260 L230 320 L180 320 Z", labelX: 205, labelY: 295, labelText: "Central" },
  { id: "PY-9", path: "M180 320 L230 320 L230 370 L180 370 Z", labelX: 205, labelY: 350, labelText: "Paraguarí" },
  { id: "PY-4", path: "M230 270 L280 270 L280 330 L230 330 Z", labelX: 255, labelY: 305, labelText: "Guairá" },
  { id: "PY-6", path: "M280 270 L320 270 L320 350 L280 350 Z", labelX: 300, labelY: 315, labelText: "Caazapá" },
  { id: "PY-12", path: "M120 350 L180 350 L180 430 L120 430 Z", labelX: 150, labelY: 395, labelText: "Ñeembucú" },
  { id: "PY-8", path: "M180 370 L240 370 L240 440 L180 440 Z", labelX: 210, labelY: 410, labelText: "Misiones" },
  { id: "PY-7", path: "M240 350 L340 350 L340 470 L240 470 Z", labelX: 290, labelY: 415, labelText: "Itapúa" },
];

// ============ METADATA DE DEPARTAMENTOS ============

interface DepartmentMeta {
  nombre: string;
  capital: string;
  poblacion: number;
}

const DEPARTMENT_METADATA: Record<string, DepartmentMeta> = {
  "PY-ASU": { nombre: "Asunción", capital: "Asunción", poblacion: 524190 },
  "PY-1": { nombre: "Concepción", capital: "Concepción", poblacion: 251438 },
  "PY-2": { nombre: "San Pedro", capital: "San Pedro de Ycuamandiyú", poblacion: 431802 },
  "PY-3": { nombre: "Cordillera", capital: "Caacupé", poblacion: 314768 },
  "PY-4": { nombre: "Guairá", capital: "Villarrica", poblacion: 227794 },
  "PY-5": { nombre: "Caaguazú", capital: "Coronel Oviedo", poblacion: 550152 },
  "PY-6": { nombre: "Caazapá", capital: "Caazapá", poblacion: 193938 },
  "PY-7": { nombre: "Itapúa", capital: "Encarnación", poblacion: 601120 },
  "PY-8": { nombre: "Misiones", capital: "San Juan Bautista", poblacion: 124999 },
  "PY-9": { nombre: "Paraguarí", capital: "Paraguarí", poblacion: 254411 },
  "PY-10": { nombre: "Alto Paraná", capital: "Ciudad del Este", poblacion: 822823 },
  "PY-11": { nombre: "Central", capital: "Areguá", poblacion: 2221792 },
  "PY-12": { nombre: "Ñeembucú", capital: "Pilar", poblacion: 88995 },
  "PY-13": { nombre: "Amambay", capital: "Pedro Juan Caballero", poblacion: 164614 },
  "PY-14": { nombre: "Canindeyú", capital: "Salto del Guairá", poblacion: 221824 },
  "PY-15": { nombre: "Presidente Hayes", capital: "Villa Hayes", poblacion: 121075 },
  "PY-16": { nombre: "Alto Paraguay", capital: "Fuerte Olimpo", poblacion: 17587 },
  "PY-19": { nombre: "Boquerón", capital: "Filadelfia", poblacion: 68050 },
};

// Datos de ejemplo para temas (en producción vendrían del backend)
const DEFAULT_TEMAS = [
  { tema: "Empleo", menciones: 200, sentimiento: 0.1 },
  { tema: "Salud", menciones: 150, sentimiento: -0.1 },
  { tema: "Educación", menciones: 120, sentimiento: 0.2 },
  { tema: "Seguridad", menciones: 100, sentimiento: -0.2 },
  { tema: "Infraestructura", menciones: 80, sentimiento: 0.0 },
];

// ============ DATA MAPPER FUNCTION ============

const NO_DATA_COLOR = "#E2E8F0"; // Gris claro para sin datos
const HOVER_COLOR = "#60a5fa";   // Azul al hacer hover

/**
 * Mapea el valor de sentimiento a un color de relleno.
 * @param sentiment - Valor de sentimiento (-1 a 1) o null/undefined
 * @returns Color hexadecimal para el fill del path
 */
export function sentimentToColor(sentiment: number | null | undefined): string {
  if (sentiment === null || sentiment === undefined) {
    return NO_DATA_COLOR;
  }

  if (sentiment >= 0.3) return "#22c55e";  // Verde - Muy positivo
  if (sentiment >= 0.1) return "#84cc16";  // Lima - Positivo
  if (sentiment >= -0.1) return "#eab308"; // Amarillo - Neutral
  if (sentiment >= -0.3) return "#f97316"; // Naranja - Negativo
  return "#ef4444";                         // Rojo - Muy negativo
}

/**
 * DataMapper: Mapea los datos de sentimiento del backend a colores de fill.
 *
 * @param sentimentData - Objeto con códigos ISO (PY-XX) como claves y sentimiento como valores
 * @param departments - Array de geometrías de departamentos
 * @returns Objeto con códigos ISO como claves y colores como valores
 *
 * @example
 * const apiData = { "PY-ASU": 0.15, "PY-11": 0.08, "PY-10": 0.22 };
 * const fillColors = dataMapper(apiData, PARAGUAY_TOPOJSON);
 * // Result: { "PY-ASU": "#84cc16", "PY-11": "#eab308", "PY-10": "#84cc16", "PY-1": "#E2E8F0", ... }
 */
export function dataMapper(
  sentimentData: SentimentPerDept | null | undefined,
  departments: DepartmentGeometry[] = PARAGUAY_TOPOJSON
): Record<string, string> {
  const colorMap: Record<string, string> = {};

  for (const dept of departments) {
    const sentiment = sentimentData?.[dept.id];
    colorMap[dept.id] = sentimentToColor(sentiment ?? null);
  }

  return colorMap;
}

/**
 * Obtiene el color de fill para un departamento específico.
 *
 * @param isoCode - Código ISO del departamento (PY-XX)
 * @param sentimentData - Datos de sentimiento del backend
 * @param isHovered - Si el departamento está en hover
 * @returns Color de fill para el path SVG
 */
export function getDepartmentFill(
  isoCode: string,
  sentimentData: SentimentPerDept | null | undefined,
  isHovered: boolean
): string {
  if (isHovered) {
    return HOVER_COLOR;
  }

  const sentiment = sentimentData?.[isoCode];
  return sentimentToColor(sentiment ?? null);
}

// ============ HELPER FUNCTIONS ============

function getBarColor(sentiment: number): string {
  if (sentiment >= 0.2) return "#22c55e";
  if (sentiment >= 0) return "#84cc16";
  if (sentiment >= -0.2) return "#f97316";
  return "#ef4444";
}

// ============ COMPONENT PROPS ============

interface ParaguayMapProps {
  /** Datos de sentimiento del backend API (clave: PY-XX, valor: -1 a 1) */
  sentimentData?: SentimentPerDept | null;
  /** Datos detallados por departamento (opcional, para el panel de análisis) */
  departmentsDetail?: Record<string, DepartmentData>;
  /** Callback cuando se selecciona un departamento */
  onDepartmentSelect?: (department: DepartmentData | null) => void;
  /** Callback para solicitar análisis de Claude (legacy, use apiBaseUrl instead) */
  onRequestAnalysis?: (isoCode: string) => Promise<string>;
  /** Base URL for backend API (default: http://localhost:8000) */
  apiBaseUrl?: string;
  /** Clases CSS adicionales */
  className?: string;
  /** Mostrar leyenda */
  showLegend?: boolean;
}

// ============ MAIN COMPONENT ============

export default function ParaguayMap({
  sentimentData = null,
  departmentsDetail,
  onDepartmentSelect,
  onRequestAnalysis,
  apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  className = "",
  showLegend = true,
}: ParaguayMapProps) {
  const [selectedDeptId, setSelectedDeptId] = useState<string | null>(null);
  const [hoveredDeptId, setHoveredDeptId] = useState<string | null>(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [analysisText, setAnalysisText] = useState<string>("");
  const [aiSummary, setAiSummary] = useState<AISummaryResponse | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  // Mapear colores para todos los departamentos
  const fillColors = useMemo(
    () => dataMapper(sentimentData, PARAGUAY_TOPOJSON),
    [sentimentData]
  );

  // Obtener datos del departamento seleccionado
  const selectedDepartment = useMemo<DepartmentData | null>(() => {
    if (!selectedDeptId) return null;

    const meta = DEPARTMENT_METADATA[selectedDeptId];
    if (!meta) return null;

    // Si hay datos detallados del backend, usarlos
    if (departmentsDetail?.[selectedDeptId]) {
      return departmentsDetail[selectedDeptId];
    }

    // Construir datos básicos con sentimiento
    const sentiment = sentimentData?.[selectedDeptId] ?? null;

    return {
      id: selectedDeptId,
      nombre: meta.nombre,
      capital: meta.capital,
      poblacion: meta.poblacion,
      encuestasCompletadas: 0,
      sentimientoPromedio: sentiment ?? 0,
      temas: DEFAULT_TEMAS,
    };
  }, [selectedDeptId, sentimentData, departmentsDetail]);

  // Obtener datos del departamento en hover
  const hoveredDepartment = useMemo(() => {
    if (!hoveredDeptId) return null;
    const meta = DEPARTMENT_METADATA[hoveredDeptId];
    if (!meta) return null;

    return {
      ...meta,
      id: hoveredDeptId,
      sentimiento: sentimentData?.[hoveredDeptId] ?? null,
    };
  }, [hoveredDeptId, sentimentData]);

  // Fetch AI summary from backend API
  const fetchAISummary = useCallback(
    async (deptId: string): Promise<AISummaryResponse | null> => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/v1/summary/${deptId}`);

        if (!response.ok) {
          if (response.status === 503) {
            throw new Error("Servicio de IA no disponible. Verifique la configuración del servidor.");
          }
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data: AISummaryResponse = await response.json();
        return data;
      } catch (error) {
        console.error("Error fetching AI summary:", error);
        throw error;
      }
    },
    [apiBaseUrl]
  );

  // Handler para click en departamento
  const handleDepartmentClick = useCallback(
    async (isoCode: string) => {
      setSelectedDeptId(isoCode);
      setAnalysisText("");
      setAiSummary(null);
      setSummaryError(null);

      const meta = DEPARTMENT_METADATA[isoCode];
      if (!meta) return;

      // Notificar al padre
      const deptData = departmentsDetail?.[isoCode] || {
        id: isoCode,
        nombre: meta.nombre,
        capital: meta.capital,
        poblacion: meta.poblacion,
        encuestasCompletadas: 0,
        sentimientoPromedio: sentimentData?.[isoCode] ?? 0,
        temas: DEFAULT_TEMAS,
      };
      onDepartmentSelect?.(deptData);

      // Start loading
      setIsLoadingAnalysis(true);

      // Try to fetch AI summary from backend API
      try {
        const summaryData = await fetchAISummary(isoCode);
        if (summaryData) {
          setAiSummary(summaryData);
          setAnalysisText(summaryData.summary);
        }
      } catch (error) {
        // Fallback to legacy callback if available
        if (onRequestAnalysis) {
          try {
            const analysis = await onRequestAnalysis(isoCode);
            setAnalysisText(analysis);
          } catch (legacyError) {
            setSummaryError("Error al generar el análisis. Intente nuevamente.");
          }
        } else {
          // Generate local fallback summary
          const sentiment = sentimentData?.[isoCode] ?? 0;
          const sentimentWord =
            sentiment > 0.1 ? "positivo" : sentiment < -0.1 ? "negativo" : "neutral";
          setAnalysisText(
            `En ${meta.nombre}, el sentimiento ciudadano es predominantemente ${sentimentWord} ` +
            `con un índice de ${(sentiment * 100).toFixed(0)}%. ` +
            `La población de ${meta.poblacion.toLocaleString("es-PY")} habitantes ` +
            `muestra tendencias que requieren atención en políticas públicas focalizadas.\n\n` +
            `(Nota: Este es un resumen local. Para análisis completo de IA, configure el servidor backend.)`
          );
        }
      } finally {
        setIsLoadingAnalysis(false);
      }
    },
    [sentimentData, departmentsDetail, onDepartmentSelect, onRequestAnalysis, fetchAISummary]
  );

  // Handler para cerrar panel
  const closePanel = useCallback(() => {
    setSelectedDeptId(null);
    setAnalysisText("");
    setAiSummary(null);
    setSummaryError(null);
    onDepartmentSelect?.(null);
  }, [onDepartmentSelect]);

  // Componente de icono de sentimiento
  const SentimentIcon = ({ value }: { value: number | null }) => {
    if (value === null) return <Minus className="w-4 h-4 text-gray-400 inline" />;
    if (value > 0.1) return <TrendingUp className="w-4 h-4 text-green-500 inline" />;
    if (value < -0.1) return <TrendingDown className="w-4 h-4 text-red-500 inline" />;
    return <Minus className="w-4 h-4 text-yellow-500 inline" />;
  };

  return (
    <div className={`relative flex ${className}`}>
      {/* Mapa SVG de Paraguay */}
      <div className="flex-1 relative">
        <svg
          viewBox="0 0 400 500"
          className="w-full h-auto max-h-[600px]"
          style={{ filter: "drop-shadow(2px 4px 6px rgba(0,0,0,0.1))" }}
          role="img"
          aria-label="Mapa de Paraguay por departamentos"
        >
          {PARAGUAY_TOPOJSON.map((dept) => (
            <g key={dept.id} id={dept.id}>
              <path
                d={dept.path}
                fill={
                  hoveredDeptId === dept.id
                    ? HOVER_COLOR
                    : fillColors[dept.id] || NO_DATA_COLOR
                }
                stroke="#fff"
                strokeWidth="2"
                className="cursor-pointer transition-all duration-200 hover:brightness-110"
                onClick={() => handleDepartmentClick(dept.id)}
                onMouseEnter={() => setHoveredDeptId(dept.id)}
                onMouseLeave={() => setHoveredDeptId(null)}
                role="button"
                aria-label={`${dept.labelText}: ${sentimentData?.[dept.id] !== undefined ? `Sentimiento ${(sentimentData[dept.id] * 100).toFixed(0)}%` : 'Sin datos'}`}
              />
              <text
                x={dept.labelX}
                y={dept.labelY}
                className={`${dept.shortLabel ? 'text-[8px] font-bold' : 'text-[10px] font-medium'} fill-white pointer-events-none`}
                textAnchor="middle"
              >
                {dept.shortLabel || dept.labelText}
              </text>
            </g>
          ))}
        </svg>

        {/* Tooltip flotante */}
        <AnimatePresence>
          {hoveredDepartment && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3 z-10 border border-gray-200"
            >
              <h4 className="font-semibold text-gray-900">
                {hoveredDepartment.nombre}
              </h4>
              <p className="text-xs text-gray-400 mb-1">
                Código: {hoveredDepartment.id}
              </p>
              <p className="text-sm text-gray-600">
                Capital: {hoveredDepartment.capital}
              </p>
              <p className="text-sm text-gray-600">
                Población: {hoveredDepartment.poblacion.toLocaleString("es-PY")}
              </p>
              <p className="text-sm mt-1">
                Sentimiento:{" "}
                <SentimentIcon value={hoveredDepartment.sentimiento} />{" "}
                <span
                  className={
                    hoveredDepartment.sentimiento === null
                      ? "text-gray-400"
                      : hoveredDepartment.sentimiento > 0
                        ? "text-green-600"
                        : hoveredDepartment.sentimiento < 0
                          ? "text-red-600"
                          : "text-yellow-600"
                  }
                >
                  {hoveredDepartment.sentimiento !== null
                    ? `${(hoveredDepartment.sentimiento * 100).toFixed(0)}%`
                    : "Sin datos"}
                </span>
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Leyenda */}
        {showLegend && (
          <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow p-3 text-sm">
            <h5 className="font-medium text-gray-700 mb-2">
              Índice de Sentimiento
            </h5>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: "#22c55e" }}></div>
                <span className="text-gray-600">Muy positivo (+30%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: "#84cc16" }}></div>
                <span className="text-gray-600">Positivo (+10%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: "#eab308" }}></div>
                <span className="text-gray-600">Neutral</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: "#f97316" }}></div>
                <span className="text-gray-600">Negativo (-10%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: "#ef4444" }}></div>
                <span className="text-gray-600">Muy negativo (-30%)</span>
              </div>
              <div className="flex items-center gap-2 mt-2 pt-2 border-t border-gray-200">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: NO_DATA_COLOR }}></div>
                <span className="text-gray-600">Sin datos</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Panel de Análisis Detallado */}
      <AnimatePresence>
        {selectedDepartment && (
          <motion.div
            initial={{ x: "100%", opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: "100%", opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="w-96 bg-white border-l border-gray-200 shadow-xl overflow-y-auto"
          >
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 z-10">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-gray-900">
                  Análisis Detallado
                </h3>
                <button
                  onClick={closePanel}
                  className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                  aria-label="Cerrar panel"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <p className="text-2xl font-semibold text-blue-600 mt-1">
                {selectedDepartment.nombre}
              </p>
              <p className="text-xs text-gray-400">
                Código ISO: {selectedDepartment.id}
              </p>
            </div>

            <div className="p-4 space-y-6">
              {/* Estadísticas generales */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">
                    Encuestas
                  </p>
                  <p className="text-xl font-bold text-gray-900">
                    {selectedDepartment.encuestasCompletadas > 0
                      ? selectedDepartment.encuestasCompletadas.toLocaleString("es-PY")
                      : "—"}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">
                    Sentimiento
                  </p>
                  <p
                    className={`text-xl font-bold flex items-center gap-1 ${
                      sentimentData?.[selectedDepartment.id] === undefined
                        ? "text-gray-400"
                        : selectedDepartment.sentimientoPromedio > 0
                          ? "text-green-600"
                          : selectedDepartment.sentimientoPromedio < 0
                            ? "text-red-600"
                            : "text-yellow-600"
                    }`}
                  >
                    <SentimentIcon
                      value={sentimentData?.[selectedDepartment.id] ?? null}
                    />
                    {sentimentData?.[selectedDepartment.id] !== undefined
                      ? `${(selectedDepartment.sentimientoPromedio * 100).toFixed(0)}%`
                      : "Sin datos"}
                  </p>
                </div>
              </div>

              {/* Gráfico de temas */}
              {selectedDepartment.temas.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">
                    Temas Principales
                  </h4>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={selectedDepartment.temas}
                        layout="vertical"
                        margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
                      >
                        <CartesianGrid
                          strokeDasharray="3 3"
                          horizontal={true}
                          vertical={false}
                        />
                        <XAxis type="number" tick={{ fontSize: 11 }} />
                        <YAxis
                          type="category"
                          dataKey="tema"
                          tick={{ fontSize: 11 }}
                          width={100}
                        />
                        <Tooltip
                          formatter={(value: number) => [
                            `${value} menciones`,
                            "Cantidad",
                          ]}
                          labelFormatter={(label) => `Tema: ${label}`}
                          contentStyle={{
                            backgroundColor: "rgba(255,255,255,0.95)",
                            borderRadius: "8px",
                            border: "1px solid #e5e7eb",
                          }}
                        />
                        <Bar dataKey="menciones" radius={[0, 4, 4, 0]}>
                          {selectedDepartment.temas.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={getBarColor(entry.sentimiento)}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Lista de temas con sentimiento */}
              {selectedDepartment.temas.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">
                    Detalle por Tema
                  </h4>
                  <div className="space-y-2">
                    {selectedDepartment.temas.map((tema, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                      >
                        <span className="text-sm text-gray-700">{tema.tema}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">
                            {tema.menciones}
                          </span>
                          <span
                            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                              tema.sentimiento > 0.2
                                ? "bg-green-100 text-green-700"
                                : tema.sentimiento > 0
                                  ? "bg-lime-100 text-lime-700"
                                  : tema.sentimiento > -0.2
                                    ? "bg-orange-100 text-orange-700"
                                    : "bg-red-100 text-red-700"
                            }`}
                          >
                            {tema.sentimiento > 0 ? "+" : ""}
                            {(tema.sentimiento * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Análisis generado por IA */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <span>Resumen de Inteligencia Artificial</span>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                    Claude 3.5
                  </span>
                </h4>

                {/* Loading Skeleton */}
                {isLoadingAnalysis && (
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-100 space-y-3">
                    <div className="flex items-center gap-2 text-blue-600 mb-3">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Generando análisis con IA...</span>
                    </div>
                    {/* Skeleton lines */}
                    <div className="space-y-2 animate-pulse">
                      <div className="h-3 bg-blue-200/50 rounded w-full"></div>
                      <div className="h-3 bg-blue-200/50 rounded w-11/12"></div>
                      <div className="h-3 bg-blue-200/50 rounded w-4/5"></div>
                      <div className="h-3 bg-blue-200/50 rounded w-full"></div>
                      <div className="h-3 bg-blue-200/50 rounded w-3/4"></div>
                      <div className="h-3 bg-transparent rounded w-full"></div>
                      <div className="h-3 bg-blue-200/50 rounded w-full"></div>
                      <div className="h-3 bg-blue-200/50 rounded w-5/6"></div>
                      <div className="h-3 bg-blue-200/50 rounded w-2/3"></div>
                    </div>
                  </div>
                )}

                {/* Error State */}
                {!isLoadingAnalysis && summaryError && (
                  <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                    <div className="flex items-center gap-2 text-red-600 mb-2">
                      <AlertCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Error</span>
                    </div>
                    <p className="text-sm text-red-700">{summaryError}</p>
                  </div>
                )}

                {/* AI Summary Content */}
                {!isLoadingAnalysis && !summaryError && (
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                    {analysisText ? (
                      <div className="space-y-3">
                        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                          {analysisText}
                        </p>

                        {/* AI Summary Metadata */}
                        {aiSummary && (
                          <div className="mt-4 pt-3 border-t border-blue-200">
                            <div className="flex items-center gap-2 text-xs text-blue-600 mb-2">
                              <Shield className="w-3 h-3" />
                              <span>Datos anonimizados - Ley 7593/2025</span>
                            </div>
                            <div className="flex flex-wrap gap-2 text-xs">
                              <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                                {aiSummary.total_responses} respuestas
                              </span>
                              {aiSummary.topics_analyzed.length > 0 && (
                                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                                  {aiSummary.topics_analyzed.length} temas
                                </span>
                              )}
                              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                                {new Date(aiSummary.generated_at).toLocaleTimeString("es-PY", {
                                  hour: "2-digit",
                                  minute: "2-digit",
                                })}
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">
                        Haga clic en un departamento para generar el análisis de IA.
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ============ EXPORTS ============

export { PARAGUAY_TOPOJSON, DEPARTMENT_METADATA, NO_DATA_COLOR };
