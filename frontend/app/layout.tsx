import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'VoxParaguay 2026 - Sistema de Encuestas',
  description: 'Plataforma multicanal de encuestas y análisis de opinión pública',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es-PY">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
