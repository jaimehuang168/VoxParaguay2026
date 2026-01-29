import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Panel de Agente - VoxParaguay 2026',
  description: 'Consola de operador para encuestas multicanal',
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
