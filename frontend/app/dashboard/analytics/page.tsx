'use client';

import { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  MapPin,
  Download,
  Calendar,
  Filter,
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Mock data
const sentimentTrend = [
  { fecha: 'Lun', positivo: 45, neutro: 30, negativo: 25 },
  { fecha: 'Mar', positivo: 48, neutro: 28, negativo: 24 },
  { fecha: 'Mié', positivo: 42, neutro: 35, negativo: 23 },
  { fecha: 'Jue', positivo: 50, neutro: 28, negativo: 22 },
  { fecha: 'Vie', positivo: 55, neutro: 25, negativo: 20 },
  { fecha: 'Sáb', positivo: 52, neutro: 30, negativo: 18 },
  { fecha: 'Dom', positivo: 58, neutro: 27, negativo: 15 },
];

const regionData = [
  { region: 'Asunción', encuestas: 450, sentimiento: 0.42 },
  { region: 'Central', encuestas: 380, sentimiento: 0.35 },
  { region: 'Alto Paraná', encuestas: 280, sentimiento: 0.28 },
  { region: 'Itapúa', encuestas: 140, sentimiento: 0.45 },
];

const tagData = [
  { name: 'Salud', value: 35, color: '#22C55E' },
  { name: 'Educación', value: 25, color: '#3B82F6' },
  { name: 'Seguridad', value: 20, color: '#EF4444' },
  { name: 'Empleo', value: 12, color: '#F59E0B' },
  { name: 'Economía', value: 8, color: '#8B5CF6' },
];

export default function AnalyticsPage() {
  const [selectedRegion, setSelectedRegion] = useState<string>('todas');
  const [dateRange, setDateRange] = useState<string>('semana');

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Panel de Análisis
          </h1>
          <p className="text-gray-500">
            Encuesta Nacional 2026 - Análisis en tiempo real
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Region Filter */}
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow-sm">
            <MapPin className="w-4 h-4 text-gray-500" />
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="border-none focus:outline-none bg-transparent"
            >
              <option value="todas">Todas las regiones</option>
              <option value="asuncion">Asunción</option>
              <option value="central">Central</option>
              <option value="alto-parana">Alto Paraná</option>
              <option value="itapua">Itapúa</option>
            </select>
          </div>

          {/* Date Range */}
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-lg shadow-sm">
            <Calendar className="w-4 h-4 text-gray-500" />
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="border-none focus:outline-none bg-transparent"
            >
              <option value="hoy">Hoy</option>
              <option value="semana">Esta semana</option>
              <option value="mes">Este mes</option>
              <option value="total">Total campaña</option>
            </select>
          </div>

          {/* Export Button */}
          <button className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
            <Download className="w-4 h-4" />
            Exportar PDF
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-6 mb-6">
        <SummaryCard
          title="Total Encuestas"
          value="1,250"
          change="+12%"
          positive
        />
        <SummaryCard
          title="Tasa Completación"
          value="78.5%"
          change="+3.2%"
          positive
        />
        <SummaryCard
          title="Sentimiento Promedio"
          value="+0.32"
          change="+0.05"
          positive
        />
        <SummaryCard
          title="Margen de Error"
          value="±2.8%"
          change="-0.3%"
          positive
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Sentiment Trend */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold text-lg mb-4">Tendencia de Sentimiento</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={sentimentTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="fecha" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="positivo"
                stroke="#22C55E"
                strokeWidth={2}
                name="Positivo"
              />
              <Line
                type="monotone"
                dataKey="neutro"
                stroke="#6B7280"
                strokeWidth={2}
                name="Neutro"
              />
              <Line
                type="monotone"
                dataKey="negativo"
                stroke="#EF4444"
                strokeWidth={2}
                name="Negativo"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Region Distribution */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold text-lg mb-4">Distribución por Región</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={regionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="encuestas" fill="#3B82F6" name="Encuestas" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-3 gap-6">
        {/* Top Tags */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold text-lg mb-4">Temas Principales</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={tagData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {tagData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment by Region */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold text-lg mb-4">Sentimiento por Región</h3>
          <div className="space-y-4">
            {regionData.map((region) => (
              <div key={region.region}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{region.region}</span>
                  <span className={region.sentimiento > 0 ? 'text-green-500' : 'text-red-500'}>
                    {region.sentimiento > 0 ? '+' : ''}{region.sentimiento.toFixed(2)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      region.sentimiento > 0.3
                        ? 'bg-green-500'
                        : region.sentimiento > 0
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${(region.sentimiento + 1) * 50}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold text-lg mb-4">Actividad Reciente</h3>
          <div className="space-y-4">
            <ActivityItem
              time="Hace 2 min"
              text="Nueva encuesta completada en Asunción"
              type="success"
            />
            <ActivityItem
              time="Hace 5 min"
              text="Análisis de sentimiento actualizado"
              type="info"
            />
            <ActivityItem
              time="Hace 12 min"
              text="3 encuestas en progreso"
              type="warning"
            />
            <ActivityItem
              time="Hace 25 min"
              text="Reporte diario generado"
              type="success"
            />
            <ActivityItem
              time="Hace 1 hora"
              text="Nuevo agente conectado"
              type="info"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({
  title,
  value,
  change,
  positive,
}: {
  title: string;
  value: string;
  change: string;
  positive: boolean;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <p className="text-gray-500 text-sm">{title}</p>
      <p className="text-3xl font-bold mt-2">{value}</p>
      <p className={`text-sm mt-2 ${positive ? 'text-green-500' : 'text-red-500'}`}>
        {change} vs. período anterior
      </p>
    </div>
  );
}

function ActivityItem({
  time,
  text,
  type,
}: {
  time: string;
  text: string;
  type: 'success' | 'warning' | 'info';
}) {
  const colors = {
    success: 'bg-green-100 text-green-600',
    warning: 'bg-yellow-100 text-yellow-600',
    info: 'bg-blue-100 text-blue-600',
  };

  return (
    <div className="flex items-start gap-3">
      <div className={`w-2 h-2 rounded-full mt-2 ${colors[type].split(' ')[0]}`} />
      <div>
        <p className="text-sm text-gray-700">{text}</p>
        <p className="text-xs text-gray-400">{time}</p>
      </div>
    </div>
  );
}
