'use client';

import { Phone, MessageCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface Conversation {
  id: string;
  channel: 'voice' | 'whatsapp' | 'facebook' | 'instagram';
  phone: string;
  region: string;
  startedAt: Date;
  lastMessage?: string;
  unread: boolean;
}

interface ActiveConversationsListProps {
  selectedId: string | null;
  onSelect: (id: string) => void;
}

// Mock data for demonstration
const mockConversations: Conversation[] = [
  {
    id: '1',
    channel: 'voice',
    phone: '+595 981 XXX XXX',
    region: 'Asunción',
    startedAt: new Date(Date.now() - 5 * 60000),
    unread: true,
  },
  {
    id: '2',
    channel: 'whatsapp',
    phone: '+595 971 XXX XXX',
    region: 'Central',
    startedAt: new Date(Date.now() - 15 * 60000),
    lastMessage: 'Che areko problema...',
    unread: false,
  },
  {
    id: '3',
    channel: 'facebook',
    phone: 'Usuario FB',
    region: 'Alto Paraná',
    startedAt: new Date(Date.now() - 30 * 60000),
    lastMessage: 'Buenas tardes',
    unread: true,
  },
];

export function ActiveConversationsList({
  selectedId,
  onSelect,
}: ActiveConversationsListProps) {
  const channelIcons = {
    voice: <Phone className="w-4 h-4" />,
    whatsapp: <MessageCircle className="w-4 h-4 text-green-500" />,
    facebook: <MessageCircle className="w-4 h-4 text-blue-500" />,
    instagram: <MessageCircle className="w-4 h-4 text-pink-500" />,
  };

  const channelColors = {
    voice: 'bg-gray-100',
    whatsapp: 'bg-green-50',
    facebook: 'bg-blue-50',
    instagram: 'bg-pink-50',
  };

  return (
    <div className="divide-y">
      {mockConversations.map((conv) => (
        <button
          key={conv.id}
          onClick={() => onSelect(conv.id)}
          className={`w-full p-4 text-left hover:bg-gray-50 transition ${
            selectedId === conv.id ? 'bg-blue-50 border-l-4 border-primary-500' : ''
          }`}
        >
          <div className="flex items-start gap-3">
            {/* Channel Icon */}
            <div className={`p-2 rounded-full ${channelColors[conv.channel]}`}>
              {channelIcons[conv.channel]}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="font-medium text-gray-900 truncate">
                  {conv.phone}
                </p>
                {conv.unread && (
                  <span className="w-2 h-2 bg-primary-500 rounded-full" />
                )}
              </div>

              <p className="text-sm text-gray-500">{conv.region}</p>

              {conv.lastMessage && (
                <p className="text-sm text-gray-600 truncate mt-1">
                  {conv.lastMessage}
                </p>
              )}

              <p className="text-xs text-gray-400 mt-1">
                {formatDistanceToNow(conv.startedAt, {
                  addSuffix: true,
                  locale: es,
                })}
              </p>
            </div>
          </div>
        </button>
      ))}

      {mockConversations.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          No hay conversaciones activas
        </div>
      )}
    </div>
  );
}
