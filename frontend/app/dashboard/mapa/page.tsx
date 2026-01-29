"use client";

/**
 * VoxParaguay 2026 - Mapa de Opinión Pública
 * Visualización interactiva por departamento
 */

import { useState } from "react";
import ParaguayMap, { DepartmentData } from "@/components/map/ParaguayMap";
import { Map, BarChart3, Users, TrendingUp, Activity } from "lucide-react";

export default function MapaPage() {
  const [selectedDept, setSelectedDept] = useState<DepartmentData | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-3">
          <Map className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Mapa de Opinión Pública
            </h1>
            <p className="text-sm text-gray-500">
              Análisis de sentimiento por departamento - Paraguay 2026
            </p>
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
              <p className="text-lg font-semibold text-gray-900">8,934</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-500" />
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                Sentimiento Nacional
              </p>
              <p className="text-lg font-semibold text-green-600">+12%</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                Departamentos
              </p>
              <p className="text-lg font-semibold text-gray-900">
                17 <span className="text-sm text-green-600">(11 positivos)</span>
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                Tema Principal
              </p>
              <p className="text-lg font-semibold text-gray-900">
                Empleo y economía
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex h-[calc(100vh-140px)]">
        <ParaguayMap
          onDepartmentSelect={setSelectedDept}
          className="flex-1"
        />
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-2 text-center text-xs text-gray-500">
        VoxParaguay 2026 - Sistema de Encuestas y Análisis de Opinión Pública |
        Datos actualizados: {new Date().toLocaleDateString("es-PY")} |
        {selectedDept
          ? ` Departamento seleccionado: ${selectedDept.nombre}`
          : " Haga clic en un departamento para ver el análisis"}
      </footer>
    </div>
  );
}
