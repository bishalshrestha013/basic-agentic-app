import { useCallback, useState } from "react";

import { streamChat } from "../api/chat";
import { ROLE } from "../constants";
import type { ChatMessage } from "../types";

interface UseChatResult {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  sendMessage: (text: string) => Promise<void>;
}

export function useChat(): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isStreaming) {
        return;
      }

      setError(null);
      const history = messages;
      const userMessage: ChatMessage = { role: ROLE.USER, content: trimmed };

      // Append the user message and an empty assistant placeholder to fill in.
      setMessages((prev) => [
        ...prev,
        userMessage,
        { role: ROLE.ASSISTANT, content: "" },
      ]);
      setIsStreaming(true);

      const appendToken = (token: string) => {
        setMessages((prev) => {
          const next = [...prev];
          const last = next[next.length - 1];
          next[next.length - 1] = { ...last, content: last.content + token };

          return next;
        });
      };

      try {
        await streamChat(trimmed, history, {
          onToken: appendToken,
          onError: (message) => setError(message),
        });
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unknown error");
      } finally {
        setIsStreaming(false);
      }
    },
    [messages, isStreaming],
  );

  return { messages, isStreaming, error, sendMessage };
}
