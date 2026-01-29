"use client";

/**
 * VoxParaguay 2026 - Panel de Agentes
 * Monitoreo en tiempo real de agentes con distribución de carga
 */

import { useState, useEffect } from "react";
import {
  Users,
  Phone,
  MessageSquare,
  Clock,
  TrendingUp,
  Activity,
  Circle,
  RefreshCw,
} from "lucide-react";

interface Agent {
  id: string;
  nombre: string;
  estado: "disponible" | "ocupado" | "descanso" | "desconectado";
  region: string;
  cargaActual: number;
  encuestasHoy: number;
  tiempoPromedio: number;
  canal: string;
}

// Datos de ejemplo
const mockAgents: Agent[] = [
  {
    id: "1",
    nombre: "María García",
    estado: "ocupado",
    region: "Asunción",
    cargaActual: 3,
    encuestasHoy: 15,
    tiempoPromedio: 4.2,
    canal: "whatsapp",
  },
  {
    id: "2",
    nombre: "Carlos Benítez",
    estado: "disponible",
    region: "Central",
    cargaActual: 0,
    encuestasHoy: 12,
    tiempoPromedio: 3.8,
    canal: "voice",
  },
  {
    id: "3",
    nombre: "Ana Martínez",
    estado: "ocupado",
    region: "Alto Paraná",
    cargaActual: 2,
    encuestasHoy: 18,
    tiempoPromedio: 3.5,
    canal: "whatsapp",
  },
  {
    id: "4",
    nombre: "José Fernández",
    estado: "descanso",
    region: "Itapúa",
    cargaActual: 0,
    encuestasHoy: 8,
    tiempoPromedio: 5.1,
    canal: "voice",
  },
  {
    id: "5",
    nombre: "Laura Giménez",
    estado: "disponible",
    region: "Asunción",
    cargaActual: 1,
    encuestasHoy: 20,
    tiempoPromedio: 3.2,
    canal: "whatsapp",
  },
  {
    id: "6",
    nombre: "Roberto Acosta",
    estado: "ocupado",
    region: "Central",
    cargaActual: 4,
    encuestasHoy: 14,
    tiempoPromedio: 4.0,
    canal: "voice",
  },
];

const estadoColors = {
  disponible: "bg-green-500",
  ocupado: "bg-red-500",
  descanso: "bg-yellow-500",
  desconectado: "bg-gray-400",
};

const estadoLabels = {
  disponible: "Disponible",
  ocupado: "Ocupado",
  descanso: "En Descanso",
  desconectado: "Desconectado",
};

const canalIcons = {
  voice: Phone,
  whatsapp: MessageSquare,
};

export default function AgentesPage() {
  const [agents, setAgents] = useState<Agent[]>(mockAgents);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  const totalAgentes = agents.length;
  const agentesDisponibles = agents.filter((a) => a.estado === "disponible").length;
  const agentesOcupados = agents.filter((a) => a.estado === "ocupado").length;
  const totalCarga = agents.reduce((sum, a) => sum + a.cargaActual, 0);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Users className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Panel de Agentes
            </h1>
            <p className="text-sm text-gray-500">
              Monitoreo en tiempo real - Algoritmo Least Connections
            </p>
          </div>
        </div>

        <button
          onClick={refresh}
          className={`flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition ${
            isRefreshing ? "animate-pulse" : ""
          }`}
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
          Actualizar
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6 mb-6">
        <StatCard
          icon={<Users className="w-6 h-6 text-blue-500" />}
          label="Total Agentes"
          value={totalAgentes.toString()}
          sublabel="En el sistema"
        />
        <StatCard
          icon={<Circle className="w-6 h-6 text-green-500" fill="#22c55e" />}
          label="Disponibles"
          value={agentesDisponibles.toString()}
          sublabel="Listos para asignar"
        />
        <StatCard
          icon={<Activity className="w-6 h-6 text-red-500" />}
          label="En Conversación"
          value={agentesOcupados.toString()}
          sublabel="Atendiendo clientes"
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6 text-purple-500" />}
          label="Carga Total"
          value={totalCarga.toString()}
          sublabel="Conversaciones activas"
        />
      </div>

      {/* Agents Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Lista de Agentes
          </h2>
        </div>

        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Agente
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Región
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Canal
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Carga Actual
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Encuestas Hoy
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tiempo Prom.
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {agents.map((agent) => {
              const CanalIcon = canalIcons[agent.canal as keyof typeof canalIcons] || Phone;
              return (
                <tr key={agent.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <span className="text-blue-600 font-medium">
                          {agent.nombre.split(" ").map((n) => n[0]).join("")}
                        </span>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">
                          {agent.nombre}
                        </p>
                        <p className="text-xs text-gray-500">ID: {agent.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                        agent.estado === "disponible"
                          ? "bg-green-100 text-green-700"
                          : agent.estado === "ocupado"
                            ? "bg-red-100 text-red-700"
                            : agent.estado === "descanso"
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      <Circle
                        className={`w-2 h-2 ${estadoColors[agent.estado]}`}
                        fill="currentColor"
                      />
                      {estadoLabels[agent.estado]}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {agent.region}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-1.5 text-sm text-gray-600">
                      <CanalIcon className="w-4 h-4" />
                      {agent.canal === "voice" ? "Voz" : "WhatsApp"}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 w-20">
                        <div
                          className={`h-2 rounded-full ${
                            agent.cargaActual >= 4
                              ? "bg-red-500"
                              : agent.cargaActual >= 2
                                ? "bg-yellow-500"
                                : "bg-green-500"
                          }`}
                          style={{ width: `${(agent.cargaActual / 5) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-700">
                        {agent.cargaActual}/5
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {agent.encuestasHoy}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-1 text-sm text-gray-600">
                      <Clock className="w-4 h-4" />
                      {agent.tiempoPromedio.toFixed(1)} min
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Load Distribution Info */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-800 mb-2">
          Algoritmo de Distribución: Least Connections
        </h3>
        <p className="text-sm text-blue-700">
          Las nuevas conversaciones se asignan automáticamente al agente disponible
          con menor carga actual. El sistema considera la región del cliente y las
          habilidades del agente para optimizar la asignación.
        </p>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  sublabel,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sublabel: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center gap-3 mb-3">
        {icon}
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{sublabel}</p>
    </div>
  );
}
