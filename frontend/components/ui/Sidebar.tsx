'use client';

import Link from 'next/link';
import {
  Home,
  Phone,
  MessageSquare,
  BarChart3,
  Settings,
  LogOut,
  Circle,
  Map,
  Users,
} from 'lucide-react';

interface SidebarProps {
  agentStatus: 'disponible' | 'ocupado' | 'descanso';
  onStatusChange: (status: 'disponible' | 'ocupado' | 'descanso') => void;
}

export function Sidebar({ agentStatus, onStatusChange }: SidebarProps) {
  const statusColors = {
    disponible: 'bg-green-500',
    ocupado: 'bg-red-500',
    descanso: 'bg-yellow-500',
  };

  const statusLabels = {
    disponible: 'Disponible',
    ocupado: 'Ocupado',
    descanso: 'En Descanso',
  };

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-xl font-bold">VoxParaguay</h1>
        <p className="text-gray-400 text-sm">2026</p>
      </div>

      {/* Agent Status */}
      <div className="p-4 border-b border-gray-800">
        <p className="text-gray-400 text-xs uppercase mb-2">Mi Estado</p>
        <div className="relative">
          <select
            value={agentStatus}
            onChange={(e) => onStatusChange(e.target.value as any)}
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 pl-8 appearance-none cursor-pointer"
          >
            <option value="disponible">Disponible</option>
            <option value="ocupado">Ocupado</option>
            <option value="descanso">En Descanso</option>
          </select>
          <Circle
            className={`absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 ${statusColors[agentStatus]} rounded-full`}
            fill="currentColor"
          />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <NavItem href="/dashboard" icon={<Home />} label="Inicio" />
          <NavItem href="/dashboard/calls" icon={<Phone />} label="Llamadas" />
          <NavItem href="/dashboard/messages" icon={<MessageSquare />} label="Mensajes" />
          <NavItem href="/dashboard/analytics" icon={<BarChart3 />} label="Análisis" />
          <NavItem href="/dashboard/mapa" icon={<Map />} label="Mapa" />
          <NavItem href="/dashboard/agentes" icon={<Users />} label="Agentes" />
          <NavItem href="/dashboard/settings" icon={<Settings />} label="Configuración" />
        </ul>
      </nav>

      {/* Stats */}
      <div className="p-4 border-t border-gray-800">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-green-400">12</p>
            <p className="text-xs text-gray-400">Encuestas Hoy</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-blue-400">4.5m</p>
            <p className="text-xs text-gray-400">Tiempo Prom.</p>
          </div>
        </div>
      </div>

      {/* Logout */}
      <div className="p-4 border-t border-gray-800">
        <button className="flex items-center gap-2 text-gray-400 hover:text-white transition w-full">
          <LogOut className="w-5 h-5" />
          Cerrar Sesión
        </button>
      </div>
    </aside>
  );
}

function NavItem({
  href,
  icon,
  label,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <li>
      <Link
        href={href}
        className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-gray-800 transition"
      >
        {icon}
        {label}
      </Link>
    </li>
  );
}
