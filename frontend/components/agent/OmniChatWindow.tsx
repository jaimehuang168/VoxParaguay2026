'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Phone, PhoneOff, Mic, MicOff, Languages } from 'lucide-react';

interface Message {
  id: string;
  sender: 'agent' | 'respondent';
  content: string;
  timestamp: Date;
  translation?: string; // Spanish translation for Jopara/Guaraní
  language?: 'español' | 'guaraní' | 'jopara';
}

interface OmniChatWindowProps {
  conversationId: string;
}

// Mock messages for demonstration
const mockMessages: Message[] = [
  {
    id: '1',
    sender: 'agent',
    content: 'Buenas tardes, mi nombre es María. ¿Podría participar en una breve encuesta?',
    timestamp: new Date(Date.now() - 5 * 60000),
  },
  {
    id: '2',
    sender: 'respondent',
    content: "Héẽ, añembyatýma",
    timestamp: new Date(Date.now() - 4 * 60000),
    translation: 'Sí, estoy listo/a',
    language: 'jopara',
  },
  {
    id: '3',
    sender: 'agent',
    content: 'Excelente, gracias. En una escala del 1 al 5, ¿cómo calificaría los servicios de salud en su comunidad?',
    timestamp: new Date(Date.now() - 3 * 60000),
  },
];

export function OmniChatWindow({ conversationId }: OmniChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [newMessage, setNewMessage] = useState('');
  const [showTranslations, setShowTranslations] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [isCallActive, setIsCallActive] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!newMessage.trim()) return;

    const message: Message = {
      id: Date.now().toString(),
      sender: 'agent',
      content: newMessage,
      timestamp: new Date(),
    };

    setMessages([...messages, message]);
    setNewMessage('');
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div>
          <h3 className="font-semibold">+595 981 XXX XXX</h3>
          <p className="text-sm text-gray-500">Asunción • Llamada activa</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Translation toggle */}
          <button
            onClick={() => setShowTranslations(!showTranslations)}
            className={`p-2 rounded-lg ${
              showTranslations ? 'bg-primary-100 text-primary-600' : 'bg-gray-100'
            }`}
            title="Mostrar traducciones"
          >
            <Languages className="w-5 h-5" />
          </button>

          {/* Call controls */}
          <button
            onClick={() => setIsMuted(!isMuted)}
            className={`p-2 rounded-lg ${
              isMuted ? 'bg-red-100 text-red-600' : 'bg-gray-100'
            }`}
          >
            {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          <button
            onClick={() => setIsCallActive(!isCallActive)}
            className={`p-2 rounded-lg ${
              isCallActive ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
            }`}
          >
            {isCallActive ? (
              <PhoneOff className="w-5 h-5" />
            ) : (
              <Phone className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'agent' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-2xl px-4 py-2 ${
                msg.sender === 'agent'
                  ? 'bg-primary-500 text-white rounded-br-md'
                  : 'bg-white border rounded-bl-md'
              }`}
            >
              <p>{msg.content}</p>

              {/* Jopara Translation */}
              {msg.translation && showTranslations && (
                <div
                  className={`mt-2 pt-2 border-t text-sm italic ${
                    msg.sender === 'agent'
                      ? 'border-primary-400 text-primary-100'
                      : 'border-gray-200 text-gray-500'
                  }`}
                >
                  <span className="text-xs uppercase mr-1">ES:</span>
                  {msg.translation}
                </div>
              )}

              <p
                className={`text-xs mt-1 ${
                  msg.sender === 'agent' ? 'text-primary-200' : 'text-gray-400'
                }`}
              >
                {msg.timestamp.toLocaleTimeString('es-PY', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
                {msg.language && msg.language !== 'español' && (
                  <span className="ml-2 uppercase">{msg.language}</span>
                )}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Escriba su mensaje..."
            className="flex-1 border rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={handleSend}
            disabled={!newMessage.trim()}
            className="bg-primary-500 text-white p-2 rounded-full hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
