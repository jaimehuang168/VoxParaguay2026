/**
 * VoxParaguay 2026 - Global State Management
 * Using Zustand for lightweight state management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Types
interface Agent {
  id: string;
  nombre: string;
  email: string;
  estado: 'disponible' | 'ocupado' | 'desconectado' | 'descanso';
}

interface Conversation {
  id: string;
  channel: 'voice' | 'whatsapp' | 'facebook' | 'instagram';
  respondentPhone: string;
  region: string;
  campaignId: string;
  startedAt: Date;
  messages: Message[];
  surveyProgress: Record<string, any>;
}

interface Message {
  id: string;
  sender: 'agent' | 'respondent';
  content: string;
  timestamp: Date;
  translation?: string;
  language?: string;
}

interface AppState {
  // Agent
  currentAgent: Agent | null;
  setCurrentAgent: (agent: Agent | null) => void;
  updateAgentStatus: (status: Agent['estado']) => void;

  // Conversations
  conversations: Conversation[];
  activeConversationId: string | null;
  addConversation: (conversation: Conversation) => void;
  setActiveConversation: (id: string | null) => void;
  addMessage: (conversationId: string, message: Message) => void;
  updateSurveyProgress: (conversationId: string, questionId: string, answer: any) => void;

  // Offline
  isOffline: boolean;
  setIsOffline: (offline: boolean) => void;
  pendingSyncCount: number;
  setPendingSyncCount: (count: number) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Agent
      currentAgent: null,
      setCurrentAgent: (agent) => set({ currentAgent: agent }),
      updateAgentStatus: (estado) =>
        set((state) => ({
          currentAgent: state.currentAgent
            ? { ...state.currentAgent, estado }
            : null,
        })),

      // Conversations
      conversations: [],
      activeConversationId: null,
      addConversation: (conversation) =>
        set((state) => ({
          conversations: [...state.conversations, conversation],
        })),
      setActiveConversation: (id) => set({ activeConversationId: id }),
      addMessage: (conversationId, message) =>
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? { ...conv, messages: [...conv.messages, message] }
              : conv
          ),
        })),
      updateSurveyProgress: (conversationId, questionId, answer) =>
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  surveyProgress: {
                    ...conv.surveyProgress,
                    [questionId]: answer,
                  },
                }
              : conv
          ),
        })),

      // Offline
      isOffline: false,
      setIsOffline: (offline) => set({ isOffline: offline }),
      pendingSyncCount: 0,
      setPendingSyncCount: (count) => set({ pendingSyncCount: count }),
    }),
    {
      name: 'voxparaguay-storage',
      partialize: (state) => ({
        currentAgent: state.currentAgent,
        conversations: state.conversations,
      }),
    }
  )
);

// Selectors
export const useCurrentAgent = () => useAppStore((state) => state.currentAgent);
export const useConversations = () => useAppStore((state) => state.conversations);
export const useActiveConversation = () => {
  const conversations = useAppStore((state) => state.conversations);
  const activeId = useAppStore((state) => state.activeConversationId);
  return conversations.find((c) => c.id === activeId);
};
export const useIsOffline = () => useAppStore((state) => state.isOffline);
