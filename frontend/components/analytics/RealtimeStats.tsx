'use client';

import { useState, useEffect } from 'react';
import { Users, Phone, MessageSquare, TrendingUp } from 'lucide-react';

interface Stats {
  agentesActivos: number;
  encuestasHoy: number;
  conversacionesActivas: number;
  sentimientoActual: number;
}

export function RealtimeStats() {
  const [stats, setStats] = useState<Stats>({
    agentesActivos: 5,
    encuestasHoy: 127,
    conversacionesActivas: 3,
    sentimientoActual: 0.45,
  });

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setStats((prev) => ({
        ...prev,
        encuestasHoy: prev.encuestasHoy + Math.floor(Math.random() * 2),
        sentimientoActual: Math.min(
          1,
          Math.max(-1, prev.sentimientoActual + (Math.random() - 0.5) * 0.1)
        ),
      }));
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-500';
    if (score < -0.3) return 'text-red-500';
    return 'text-yellow-500';
  };

  const getSentimentLabel = (score: number) => {
    if (score > 0.3) return 'Positivo';
    if (score < -0.3) return 'Negativo';
    return 'Neutro';
  };

  return (
    <div className="px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-8">
        <StatItem
          icon={<Users className="w-4 h-4" />}
          label="Agentes Activos"
          value={stats.agentesActivos.toString()}
          color="text-blue-500"
        />
        <StatItem
          icon={<Phone className="w-4 h-4" />}
          label="Encuestas Hoy"
          value={stats.encuestasHoy.toString()}
          color="text-green-500"
        />
        <StatItem
          icon={<MessageSquare className="w-4 h-4" />}
          label="Conversaciones"
          value={stats.conversacionesActivas.toString()}
          color="text-purple-500"
        />
      </div>

      <div className="flex items-center gap-3">
        <TrendingUp className={`w-5 h-5 ${getSentimentColor(stats.sentimientoActual)}`} />
        <div>
          <p className="text-xs text-gray-500">Sentimiento Actual</p>
          <p className={`font-semibold ${getSentimentColor(stats.sentimientoActual)}`}>
            {getSentimentLabel(stats.sentimientoActual)} ({(stats.sentimientoActual * 100).toFixed(0)}%)
          </p>
        </div>
      </div>
    </div>
  );
}

function StatItem({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <div className={color}>{icon}</div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="font-semibold">{value}</p>
      </div>
    </div>
  );
}
