import { create } from "zustand";
import { persist } from "zustand/middleware";
import { ChatMessage, Citation } from "@/types/rag";

interface ChatState {
  // Messages keyed by document_id
  threads: Record<string, ChatMessage[]>;
  isGenerating: boolean;
  pendingPrompt: string | null;
  selectedCitation: Citation | null;
  isCitationDrawerOpen: boolean;

  // Actions
  getThread: (documentId: string) => ChatMessage[];
  addMessage: (
    documentId: string,
    message: Omit<ChatMessage, "id" | "timestamp">
  ) => ChatMessage;
  clearThread: (documentId: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setPendingPrompt: (prompt: string | null) => void;
  openCitationDrawer: (citation: Citation) => void;
  closeCitationDrawer: () => void;
  setSelectedCitation: (citation: Citation | null) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      threads: {},
      isGenerating: false,
      pendingPrompt: null,
      selectedCitation: null,
      isCitationDrawerOpen: false,

      getThread: (documentId: string) => {
        return get().threads[documentId] || [];
      },

      addMessage: (documentId, messageData) => {
        const newMessage: ChatMessage = {
          ...messageData,
          id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
          timestamp: new Date().toISOString(),
        };

        set((state) => {
          const currentThread = state.threads[documentId] || [];
          return {
            threads: {
              ...state.threads,
              [documentId]: [...currentThread, newMessage],
            },
          };
        });

        return newMessage;
      },

      clearThread: (documentId: string) => {
        set((state) => {
          const updated = { ...state.threads };
          delete updated[documentId];
          return { threads: updated };
        });
      },

      setIsGenerating: (isGenerating: boolean) => set({ isGenerating }),
      setPendingPrompt: (pendingPrompt: string | null) => set({ pendingPrompt }),

      openCitationDrawer: (citation: Citation) =>
        set({
          selectedCitation: citation,
          isCitationDrawerOpen: true,
        }),

      closeCitationDrawer: () =>
        set({
          isCitationDrawerOpen: false,
          selectedCitation: null,
        }),

      setSelectedCitation: (citation: Citation | null) =>
        set({
          selectedCitation: citation,
          isCitationDrawerOpen: !!citation,
        }),
    }),
    {
      name: "findoc-chat-threads",
      partialize: (state) => ({ threads: state.threads }),
    }
  )
);
