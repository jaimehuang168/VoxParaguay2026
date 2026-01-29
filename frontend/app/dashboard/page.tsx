'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/ui/Sidebar';
import { ActiveConversationsList } from '@/components/agent/ActiveConversationsList';
import { OmniChatWindow } from '@/components/agent/OmniChatWindow';
import { VisualSurveyScript } from '@/components/survey/VisualSurveyScript';
import { RealtimeStats } from '@/components/analytics/RealtimeStats';

export default function DashboardPage() {
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [agentStatus, setAgentStatus] = useState<'disponible' | 'ocupado' | 'descanso'>('disponible');

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar
        agentStatus={agentStatus}
        onStatusChange={setAgentStatus}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Conversations List */}
        <div className="w-80 bg-white border-r overflow-y-auto">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-lg">Conversaciones Activas</h2>
          </div>
          <ActiveConversationsList
            selectedId={selectedConversation}
            onSelect={setSelectedConversation}
          />
        </div>

        {/* Chat Window + Survey Script */}
        <div className="flex-1 flex">
          {/* Chat */}
          <div className="flex-1 flex flex-col">
            {selectedConversation ? (
              <OmniChatWindow conversationId={selectedConversation} />
            ) : (
              <EmptyState />
            )}
          </div>

          {/* Survey Script Panel */}
          {selectedConversation && (
            <div className="w-96 bg-white border-l overflow-y-auto">
              <VisualSurveyScript
                conversationId={selectedConversation}
              />
            </div>
          )}
        </div>
      </div>

      {/* Realtime Stats Bar */}
      <div className="fixed bottom-0 left-64 right-0 bg-white border-t shadow-lg">
        <RealtimeStats />
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex-1 flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="text-6xl mb-4">📞</div>
        <h3 className="text-xl font-medium text-gray-700">
          Seleccione una conversación
        </h3>
        <p className="text-gray-500 mt-2">
          O espere una nueva llamada o mensaje
        </p>
      </div>
    </div>
  );
}
