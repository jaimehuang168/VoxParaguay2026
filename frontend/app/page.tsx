import Link from 'next/link';
import { Phone, MessageCircle, BarChart3, Users } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                VoxParaguay 2026
              </h1>
              <p className="text-gray-500 mt-1">
                Sistema de Encuestas Multicanal
              </p>
            </div>
            <Link
              href="/dashboard"
              className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition"
            >
              Ingresar al Sistema
            </Link>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <FeatureCard
            icon={<Phone className="w-8 h-8" />}
            title="Llamadas de Voz"
            description="Integración con Twilio para encuestas telefónicas"
          />
          <FeatureCard
            icon={<MessageCircle className="w-8 h-8" />}
            title="WhatsApp & Redes"
            description="Conexión con WhatsApp, Facebook e Instagram"
          />
          <FeatureCard
            icon={<BarChart3 className="w-8 h-8" />}
            title="Análisis AI"
            description="Análisis de sentimiento con soporte Jopara"
          />
          <FeatureCard
            icon={<Users className="w-8 h-8" />}
            title="Multi-Agente"
            description="Panel de control para múltiples operadores"
          />
        </div>
      </section>

      {/* Stats Preview */}
      <section className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-center mb-12">
            Cobertura Nacional
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <StatCard region="Asunción" color="bg-paraguay-red" />
            <StatCard region="Central" color="bg-primary-600" />
            <StatCard region="Alto Paraná" color="bg-green-600" />
            <StatCard region="Itapúa" color="bg-yellow-500" />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-gray-400">
            VoxParaguay 2026 - Cumple con Ley 7593/2025 de Protección de Datos
          </p>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition">
      <div className="text-primary-600 mb-4">{icon}</div>
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}

function StatCard({ region, color }: { region: string; color: string }) {
  return (
    <div className="text-center">
      <div
        className={`w-16 h-16 ${color} rounded-full mx-auto mb-4 flex items-center justify-center`}
      >
        <span className="text-white font-bold text-xl">
          {region.charAt(0)}
        </span>
      </div>
      <p className="font-medium">{region}</p>
    </div>
  );
}
