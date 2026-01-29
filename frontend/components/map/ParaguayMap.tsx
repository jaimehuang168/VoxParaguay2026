"use client";

/**
 * VoxParaguay 2026 - Mapa Interactivo de Paraguay
 * Visualización de datos por departamento con análisis detallado
 */

import React, { useState, useCallback } from "react";
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
import { X, TrendingUp, TrendingDown, Minus, Loader2 } from "lucide-react";

// Departamentos de Paraguay con datos de ejemplo
export interface DepartmentData {
  id: string;
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

// Datos de ejemplo para todos los departamentos
const departmentsData: Record<string, DepartmentData> = {
  asuncion: {
    id: "asuncion",
    nombre: "Asunción",
    capital: "Asunción",
    poblacion: 524190,
    encuestasCompletadas: 1245,
    sentimientoPromedio: 0.15,
    temas: [
      { tema: "Transporte público", menciones: 342, sentimiento: -0.3 },
      { tema: "Seguridad ciudadana", menciones: 287, sentimiento: -0.45 },
      { tema: "Empleo", menciones: 256, sentimiento: 0.1 },
      { tema: "Educación", menciones: 189, sentimiento: 0.25 },
      { tema: "Salud pública", menciones: 171, sentimiento: -0.15 },
    ],
  },
  central: {
    id: "central",
    nombre: "Central",
    capital: "Areguá",
    poblacion: 2221792,
    encuestasCompletadas: 2156,
    sentimientoPromedio: 0.08,
    temas: [
      { tema: "Infraestructura vial", menciones: 523, sentimiento: -0.4 },
      { tema: "Agua potable", menciones: 412, sentimiento: -0.55 },
      { tema: "Empleo", menciones: 378, sentimiento: 0.05 },
      { tema: "Vivienda", menciones: 298, sentimiento: -0.2 },
      { tema: "Educación", menciones: 245, sentimiento: 0.3 },
    ],
  },
  alto_parana: {
    id: "alto_parana",
    nombre: "Alto Paraná",
    capital: "Ciudad del Este",
    poblacion: 822823,
    encuestasCompletadas: 987,
    sentimientoPromedio: 0.22,
    temas: [
      { tema: "Comercio fronterizo", menciones: 412, sentimiento: 0.4 },
      { tema: "Turismo", menciones: 287, sentimiento: 0.55 },
      { tema: "Seguridad", menciones: 234, sentimiento: -0.3 },
      { tema: "Empleo", menciones: 198, sentimiento: 0.15 },
      { tema: "Medio ambiente", menciones: 156, sentimiento: -0.1 },
    ],
  },
  itapua: {
    id: "itapua",
    nombre: "Itapúa",
    capital: "Encarnación",
    poblacion: 601120,
    encuestasCompletadas: 756,
    sentimientoPromedio: 0.35,
    temas: [
      { tema: "Agricultura", menciones: 345, sentimiento: 0.45 },
      { tema: "Turismo", menciones: 298, sentimiento: 0.6 },
      { tema: "Exportaciones", menciones: 212, sentimiento: 0.35 },
      { tema: "Infraestructura", menciones: 178, sentimiento: -0.1 },
      { tema: "Educación", menciones: 143, sentimiento: 0.25 },
    ],
  },
  san_pedro: {
    id: "san_pedro",
    nombre: "San Pedro",
    capital: "San Pedro de Ycuamandiyú",
    poblacion: 431802,
    encuestasCompletadas: 423,
    sentimientoPromedio: -0.12,
    temas: [
      { tema: "Agricultura familiar", menciones: 234, sentimiento: -0.2 },
      { tema: "Acceso a salud", menciones: 198, sentimiento: -0.45 },
      { tema: "Caminos rurales", menciones: 176, sentimiento: -0.35 },
      { tema: "Educación rural", menciones: 145, sentimiento: -0.1 },
      { tema: "Agua potable", menciones: 123, sentimiento: -0.5 },
    ],
  },
  caaguazu: {
    id: "caaguazu",
    nombre: "Caaguazú",
    capital: "Coronel Oviedo",
    poblacion: 550152,
    encuestasCompletadas: 534,
    sentimientoPromedio: 0.05,
    temas: [
      { tema: "Producción agrícola", menciones: 267, sentimiento: 0.2 },
      { tema: "Infraestructura", menciones: 198, sentimiento: -0.25 },
      { tema: "Empleo", menciones: 167, sentimiento: -0.1 },
      { tema: "Salud", menciones: 145, sentimiento: -0.2 },
      { tema: "Educación", menciones: 123, sentimiento: 0.15 },
    ],
  },
  paraguari: {
    id: "paraguari",
    nombre: "Paraguarí",
    capital: "Paraguarí",
    poblacion: 254411,
    encuestasCompletadas: 312,
    sentimientoPromedio: 0.18,
    temas: [
      { tema: "Turismo interno", menciones: 156, sentimiento: 0.45 },
      { tema: "Artesanía", menciones: 134, sentimiento: 0.35 },
      { tema: "Agricultura", menciones: 112, sentimiento: 0.1 },
      { tema: "Caminos", menciones: 98, sentimiento: -0.2 },
      { tema: "Cultura", menciones: 87, sentimiento: 0.4 },
    ],
  },
  guaira: {
    id: "guaira",
    nombre: "Guairá",
    capital: "Villarrica",
    poblacion: 227794,
    encuestasCompletadas: 287,
    sentimientoPromedio: 0.28,
    temas: [
      { tema: "Cultura y tradición", menciones: 145, sentimiento: 0.55 },
      { tema: "Educación universitaria", menciones: 123, sentimiento: 0.4 },
      { tema: "Turismo", menciones: 98, sentimiento: 0.35 },
      { tema: "Agricultura", menciones: 87, sentimiento: 0.15 },
      { tema: "Comercio", menciones: 76, sentimiento: 0.2 },
    ],
  },
  caazapa: {
    id: "caazapa",
    nombre: "Caazapá",
    capital: "Caazapá",
    poblacion: 193938,
    encuestasCompletadas: 198,
    sentimientoPromedio: -0.08,
    temas: [
      { tema: "Pobreza rural", menciones: 112, sentimiento: -0.45 },
      { tema: "Acceso a servicios", menciones: 98, sentimiento: -0.35 },
      { tema: "Agricultura", menciones: 87, sentimiento: 0.1 },
      { tema: "Educación", menciones: 76, sentimiento: -0.15 },
      { tema: "Salud", menciones: 65, sentimiento: -0.3 },
    ],
  },
  misiones: {
    id: "misiones",
    nombre: "Misiones",
    capital: "San Juan Bautista",
    poblacion: 124999,
    encuestasCompletadas: 156,
    sentimientoPromedio: 0.32,
    temas: [
      { tema: "Turismo jesuítico", menciones: 87, sentimiento: 0.6 },
      { tema: "Ganadería", menciones: 76, sentimiento: 0.35 },
      { tema: "Historia y cultura", menciones: 65, sentimiento: 0.45 },
      { tema: "Infraestructura", menciones: 54, sentimiento: -0.1 },
      { tema: "Empleo", menciones: 45, sentimiento: 0.05 },
    ],
  },
  neembucu: {
    id: "neembucu",
    nombre: "Ñeembucú",
    capital: "Pilar",
    poblacion: 88995,
    encuestasCompletadas: 112,
    sentimientoPromedio: 0.12,
    temas: [
      { tema: "Inundaciones", menciones: 67, sentimiento: -0.55 },
      { tema: "Pesca", menciones: 54, sentimiento: 0.3 },
      { tema: "Turismo fluvial", menciones: 45, sentimiento: 0.4 },
      { tema: "Aislamiento", menciones: 38, sentimiento: -0.4 },
      { tema: "Ganadería", menciones: 32, sentimiento: 0.25 },
    ],
  },
  amambay: {
    id: "amambay",
    nombre: "Amambay",
    capital: "Pedro Juan Caballero",
    poblacion: 164614,
    encuestasCompletadas: 234,
    sentimientoPromedio: -0.15,
    temas: [
      { tema: "Seguridad fronteriza", menciones: 134, sentimiento: -0.55 },
      { tema: "Comercio", menciones: 98, sentimiento: 0.2 },
      { tema: "Narcotráfico", menciones: 87, sentimiento: -0.7 },
      { tema: "Empleo", menciones: 67, sentimiento: -0.1 },
      { tema: "Turismo", menciones: 45, sentimiento: 0.15 },
    ],
  },
  canindeyu: {
    id: "canindeyu",
    nombre: "Canindeyú",
    capital: "Salto del Guairá",
    poblacion: 221824,
    encuestasCompletadas: 267,
    sentimientoPromedio: 0.1,
    temas: [
      { tema: "Soja", menciones: 145, sentimiento: 0.35 },
      { tema: "Comercio fronterizo", menciones: 112, sentimiento: 0.25 },
      { tema: "Medio ambiente", menciones: 87, sentimiento: -0.3 },
      { tema: "Comunidades indígenas", menciones: 76, sentimiento: -0.2 },
      { tema: "Infraestructura", menciones: 54, sentimiento: -0.15 },
    ],
  },
  presidente_hayes: {
    id: "presidente_hayes",
    nombre: "Presidente Hayes",
    capital: "Villa Hayes",
    poblacion: 121075,
    encuestasCompletadas: 145,
    sentimientoPromedio: 0.08,
    temas: [
      { tema: "Ganadería Chaco", menciones: 78, sentimiento: 0.3 },
      { tema: "Comunidades indígenas", menciones: 67, sentimiento: -0.25 },
      { tema: "Acceso a agua", menciones: 54, sentimiento: -0.4 },
      { tema: "Caminos", menciones: 45, sentimiento: -0.35 },
      { tema: "Desarrollo", menciones: 38, sentimiento: 0.1 },
    ],
  },
  boqueron: {
    id: "boqueron",
    nombre: "Boquerón",
    capital: "Filadelfia",
    poblacion: 68050,
    encuestasCompletadas: 89,
    sentimientoPromedio: 0.25,
    temas: [
      { tema: "Colonias menonitas", menciones: 45, sentimiento: 0.5 },
      { tema: "Ganadería", menciones: 38, sentimiento: 0.35 },
      { tema: "Agua", menciones: 32, sentimiento: -0.3 },
      { tema: "Comunidades indígenas", menciones: 28, sentimiento: -0.15 },
      { tema: "Desarrollo económico", menciones: 23, sentimiento: 0.4 },
    ],
  },
  alto_paraguay: {
    id: "alto_paraguay",
    nombre: "Alto Paraguay",
    capital: "Fuerte Olimpo",
    poblacion: 17587,
    encuestasCompletadas: 34,
    sentimientoPromedio: -0.22,
    temas: [
      { tema: "Aislamiento", menciones: 18, sentimiento: -0.55 },
      { tema: "Servicios básicos", menciones: 15, sentimiento: -0.5 },
      { tema: "Comunidades indígenas", menciones: 12, sentimiento: -0.3 },
      { tema: "Medio ambiente", menciones: 10, sentimiento: 0.2 },
      { tema: "Turismo ecológico", menciones: 8, sentimiento: 0.35 },
    ],
  },
  concepcion: {
    id: "concepcion",
    nombre: "Concepción",
    capital: "Concepción",
    poblacion: 251438,
    encuestasCompletadas: 312,
    sentimientoPromedio: -0.05,
    temas: [
      { tema: "Ganadería", menciones: 167, sentimiento: 0.25 },
      { tema: "Seguridad", menciones: 134, sentimiento: -0.45 },
      { tema: "Río Paraguay", menciones: 98, sentimiento: 0.15 },
      { tema: "Empleo", menciones: 87, sentimiento: -0.2 },
      { tema: "Educación", menciones: 76, sentimiento: 0.1 },
    ],
  },
  cordillera: {
    id: "cordillera",
    nombre: "Cordillera",
    capital: "Caacupé",
    poblacion: 314768,
    encuestasCompletadas: 398,
    sentimientoPromedio: 0.38,
    temas: [
      { tema: "Turismo religioso", menciones: 198, sentimiento: 0.65 },
      { tema: "Artesanía", menciones: 145, sentimiento: 0.45 },
      { tema: "Fiestas tradicionales", menciones: 123, sentimiento: 0.55 },
      { tema: "Comercio", menciones: 98, sentimiento: 0.25 },
      { tema: "Infraestructura", menciones: 87, sentimiento: 0.1 },
    ],
  },
};

// Colores según sentimiento
const getSentimentColor = (sentiment: number): string => {
  if (sentiment >= 0.3) return "#22c55e"; // Verde positivo
  if (sentiment >= 0.1) return "#84cc16"; // Verde claro
  if (sentiment >= -0.1) return "#eab308"; // Amarillo neutral
  if (sentiment >= -0.3) return "#f97316"; // Naranja negativo
  return "#ef4444"; // Rojo muy negativo
};

const getBarColor = (sentiment: number): string => {
  if (sentiment >= 0.2) return "#22c55e";
  if (sentiment >= 0) return "#84cc16";
  if (sentiment >= -0.2) return "#f97316";
  return "#ef4444";
};

interface ParaguayMapProps {
  onDepartmentSelect?: (department: DepartmentData | null) => void;
  className?: string;
}

export default function ParaguayMap({
  onDepartmentSelect,
  className = "",
}: ParaguayMapProps) {
  const [selectedDepartment, setSelectedDepartment] =
    useState<DepartmentData | null>(null);
  const [hoveredDepartment, setHoveredDepartment] = useState<string | null>(
    null
  );
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [analysisText, setAnalysisText] = useState<string>("");

  const handleDepartmentClick = useCallback(
    async (departmentId: string) => {
      const department = departmentsData[departmentId];
      if (department) {
        setSelectedDepartment(department);
        onDepartmentSelect?.(department);

        // Simular llamada a Claude API para análisis
        setIsLoadingAnalysis(true);
        setAnalysisText("");

        // En producción, esto llamaría al backend que usa Claude API
        setTimeout(() => {
          const analysis = generateMockAnalysis(department);
          setAnalysisText(analysis);
          setIsLoadingAnalysis(false);
        }, 1500);
      }
    },
    [onDepartmentSelect]
  );

  const closePanel = useCallback(() => {
    setSelectedDepartment(null);
    setAnalysisText("");
    onDepartmentSelect?.(null);
  }, [onDepartmentSelect]);

  // Mock de análisis generado por Claude (en producción vendría del backend)
  const generateMockAnalysis = (dept: DepartmentData): string => {
    const topTema = dept.temas[0];
    const sentimentWord =
      dept.sentimientoPromedio > 0.1
        ? "positivo"
        : dept.sentimientoPromedio < -0.1
          ? "negativo"
          : "neutral";

    return `En ${dept.nombre}, el sentimiento ciudadano es predominantemente ${sentimentWord} con un índice de ${(dept.sentimientoPromedio * 100).toFixed(0)}%. El tema más mencionado es "${topTema.tema}" con ${topTema.menciones} referencias. La población muestra ${topTema.sentimiento > 0 ? "satisfacción" : "preocupación"} respecto a este tema. Se recomienda priorizar políticas públicas enfocadas en ${dept.temas.filter((t) => t.sentimiento < 0).map((t) => t.tema).slice(0, 2).join(" y ") || "fortalecer los logros actuales"}.`;
  };

  const SentimentIcon = ({ value }: { value: number }) => {
    if (value > 0.1)
      return <TrendingUp className="w-4 h-4 text-green-500 inline" />;
    if (value < -0.1)
      return <TrendingDown className="w-4 h-4 text-red-500 inline" />;
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
        >
          {/* Departamentos del Chaco (oeste) */}
          <g id="chaco">
            {/* Alto Paraguay */}
            <path
              id="alto_paraguay"
              d="M50 20 L180 20 L180 120 L50 120 Z"
              fill={
                hoveredDepartment === "alto_paraguay"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.alto_paraguay.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("alto_paraguay")}
              onMouseEnter={() => setHoveredDepartment("alto_paraguay")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="115"
              y="75"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Alto Paraguay
            </text>

            {/* Boquerón */}
            <path
              id="boqueron"
              d="M50 120 L180 120 L180 220 L50 220 Z"
              fill={
                hoveredDepartment === "boqueron"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.boqueron.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("boqueron")}
              onMouseEnter={() => setHoveredDepartment("boqueron")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="115"
              y="175"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Boquerón
            </text>

            {/* Presidente Hayes */}
            <path
              id="presidente_hayes"
              d="M50 220 L180 220 L180 320 L120 320 L120 350 L50 350 Z"
              fill={
                hoveredDepartment === "presidente_hayes"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.presidente_hayes.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("presidente_hayes")}
              onMouseEnter={() => setHoveredDepartment("presidente_hayes")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="115"
              y="280"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Pdte. Hayes
            </text>
          </g>

          {/* Región Oriental */}
          <g id="oriental">
            {/* Concepción */}
            <path
              id="concepcion"
              d="M180 80 L280 80 L280 140 L180 140 Z"
              fill={
                hoveredDepartment === "concepcion"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.concepcion.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("concepcion")}
              onMouseEnter={() => setHoveredDepartment("concepcion")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="230"
              y="115"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Concepción
            </text>

            {/* Amambay */}
            <path
              id="amambay"
              d="M280 80 L350 80 L350 140 L280 140 Z"
              fill={
                hoveredDepartment === "amambay"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.amambay.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("amambay")}
              onMouseEnter={() => setHoveredDepartment("amambay")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="315"
              y="115"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Amambay
            </text>

            {/* San Pedro */}
            <path
              id="san_pedro"
              d="M180 140 L280 140 L280 200 L180 200 Z"
              fill={
                hoveredDepartment === "san_pedro"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.san_pedro.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("san_pedro")}
              onMouseEnter={() => setHoveredDepartment("san_pedro")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="230"
              y="175"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              San Pedro
            </text>

            {/* Canindeyú */}
            <path
              id="canindeyu"
              d="M280 140 L370 140 L370 220 L280 220 Z"
              fill={
                hoveredDepartment === "canindeyu"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.canindeyu.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("canindeyu")}
              onMouseEnter={() => setHoveredDepartment("canindeyu")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="325"
              y="185"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Canindeyú
            </text>

            {/* Cordillera */}
            <path
              id="cordillera"
              d="M180 200 L230 200 L230 260 L180 260 Z"
              fill={
                hoveredDepartment === "cordillera"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.cordillera.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("cordillera")}
              onMouseEnter={() => setHoveredDepartment("cordillera")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="205"
              y="235"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Cordillera
            </text>

            {/* Caaguazú */}
            <path
              id="caaguazu"
              d="M230 200 L320 200 L320 270 L230 270 Z"
              fill={
                hoveredDepartment === "caaguazu"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.caaguazu.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("caaguazu")}
              onMouseEnter={() => setHoveredDepartment("caaguazu")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="275"
              y="240"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Caaguazú
            </text>

            {/* Alto Paraná */}
            <path
              id="alto_parana"
              d="M320 200 L380 200 L380 310 L320 310 Z"
              fill={
                hoveredDepartment === "alto_parana"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.alto_parana.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("alto_parana")}
              onMouseEnter={() => setHoveredDepartment("alto_parana")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="350"
              y="260"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Alto Paraná
            </text>

            {/* Asunción */}
            <path
              id="asuncion"
              d="M150 270 L180 270 L180 300 L150 300 Z"
              fill={
                hoveredDepartment === "asuncion"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.asuncion.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("asuncion")}
              onMouseEnter={() => setHoveredDepartment("asuncion")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="165"
              y="288"
              className="text-[8px] fill-white font-bold pointer-events-none"
              textAnchor="middle"
            >
              ASU
            </text>

            {/* Central */}
            <path
              id="central"
              d="M180 260 L230 260 L230 320 L180 320 Z"
              fill={
                hoveredDepartment === "central"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.central.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("central")}
              onMouseEnter={() => setHoveredDepartment("central")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="205"
              y="295"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Central
            </text>

            {/* Paraguarí */}
            <path
              id="paraguari"
              d="M180 320 L230 320 L230 370 L180 370 Z"
              fill={
                hoveredDepartment === "paraguari"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.paraguari.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("paraguari")}
              onMouseEnter={() => setHoveredDepartment("paraguari")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="205"
              y="350"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Paraguarí
            </text>

            {/* Guairá */}
            <path
              id="guaira"
              d="M230 270 L280 270 L280 330 L230 330 Z"
              fill={
                hoveredDepartment === "guaira"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.guaira.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("guaira")}
              onMouseEnter={() => setHoveredDepartment("guaira")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="255"
              y="305"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Guairá
            </text>

            {/* Caazapá */}
            <path
              id="caazapa"
              d="M280 270 L320 270 L320 350 L280 350 Z"
              fill={
                hoveredDepartment === "caazapa"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.caazapa.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("caazapa")}
              onMouseEnter={() => setHoveredDepartment("caazapa")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="300"
              y="315"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Caazapá
            </text>

            {/* Ñeembucú */}
            <path
              id="neembucu"
              d="M120 350 L180 350 L180 430 L120 430 Z"
              fill={
                hoveredDepartment === "neembucu"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.neembucu.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("neembucu")}
              onMouseEnter={() => setHoveredDepartment("neembucu")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="150"
              y="395"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Ñeembucú
            </text>

            {/* Misiones */}
            <path
              id="misiones"
              d="M180 370 L240 370 L240 440 L180 440 Z"
              fill={
                hoveredDepartment === "misiones"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.misiones.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("misiones")}
              onMouseEnter={() => setHoveredDepartment("misiones")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="210"
              y="410"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Misiones
            </text>

            {/* Itapúa */}
            <path
              id="itapua"
              d="M240 350 L340 350 L340 470 L240 470 Z"
              fill={
                hoveredDepartment === "itapua"
                  ? "#60a5fa"
                  : getSentimentColor(
                      departmentsData.itapua.sentimientoPromedio
                    )
              }
              stroke="#fff"
              strokeWidth="2"
              className="cursor-pointer transition-all duration-200 hover:brightness-110"
              onClick={() => handleDepartmentClick("itapua")}
              onMouseEnter={() => setHoveredDepartment("itapua")}
              onMouseLeave={() => setHoveredDepartment(null)}
            />
            <text
              x="290"
              y="415"
              className="text-[10px] fill-white font-medium pointer-events-none"
              textAnchor="middle"
            >
              Itapúa
            </text>
          </g>
        </svg>

        {/* Tooltip flotante */}
        <AnimatePresence>
          {hoveredDepartment && departmentsData[hoveredDepartment] && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg p-3 z-10 border border-gray-200"
            >
              <h4 className="font-semibold text-gray-900">
                {departmentsData[hoveredDepartment].nombre}
              </h4>
              <p className="text-sm text-gray-600">
                Capital: {departmentsData[hoveredDepartment].capital}
              </p>
              <p className="text-sm text-gray-600">
                Población:{" "}
                {departmentsData[
                  hoveredDepartment
                ].poblacion.toLocaleString("es-PY")}
              </p>
              <p className="text-sm mt-1">
                Sentimiento:{" "}
                <SentimentIcon
                  value={
                    departmentsData[hoveredDepartment].sentimientoPromedio
                  }
                />{" "}
                <span
                  className={
                    departmentsData[hoveredDepartment].sentimientoPromedio > 0
                      ? "text-green-600"
                      : departmentsData[hoveredDepartment]
                            .sentimientoPromedio < 0
                        ? "text-red-600"
                        : "text-yellow-600"
                  }
                >
                  {(
                    departmentsData[hoveredDepartment].sentimientoPromedio * 100
                  ).toFixed(0)}
                  %
                </span>
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Leyenda */}
        <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow p-3 text-sm">
          <h5 className="font-medium text-gray-700 mb-2">
            Índice de Sentimiento
          </h5>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-green-500"></div>
              <span className="text-gray-600">Muy positivo (+30%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-lime-500"></div>
              <span className="text-gray-600">Positivo (+10%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-yellow-500"></div>
              <span className="text-gray-600">Neutral</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-orange-500"></div>
              <span className="text-gray-600">Negativo (-10%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-500"></div>
              <span className="text-gray-600">Muy negativo (-30%)</span>
            </div>
          </div>
        </div>
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
            </div>

            <div className="p-4 space-y-6">
              {/* Estadísticas generales */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">
                    Encuestas
                  </p>
                  <p className="text-xl font-bold text-gray-900">
                    {selectedDepartment.encuestasCompletadas.toLocaleString(
                      "es-PY"
                    )}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">
                    Sentimiento
                  </p>
                  <p
                    className={`text-xl font-bold flex items-center gap-1 ${
                      selectedDepartment.sentimientoPromedio > 0
                        ? "text-green-600"
                        : selectedDepartment.sentimientoPromedio < 0
                          ? "text-red-600"
                          : "text-yellow-600"
                    }`}
                  >
                    <SentimentIcon
                      value={selectedDepartment.sentimientoPromedio}
                    />
                    {(selectedDepartment.sentimientoPromedio * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* Gráfico de temas */}
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

              {/* Lista de temas con sentimiento */}
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

              {/* Análisis generado por IA */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <span>Resumen de Inteligencia Artificial</span>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                    Claude
                  </span>
                </h4>
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                  {isLoadingAnalysis ? (
                    <div className="flex items-center gap-2 text-blue-600">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Generando análisis...</span>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {analysisText}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
