import { useEffect, useRef } from "react";

import { ASSISTANT_GREETING } from "../constants";
import type { ChatMessage } from "../types";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming: boolean;
}

export function MessageList({ messages, isStreaming }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  // While streaming, the last assistant message starts empty — show the typing
  // indicator until the first token arrives.
  const lastMessage = messages[messages.length - 1];
  const showTyping =
    isStreaming && lastMessage?.content.length === 0;

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="mx-auto flex w-full max-w-2xl flex-col gap-4 px-4 py-6">
        {messages.length === 0 ? (
          <p className="mt-10 text-center text-neutral-400">
            {ASSISTANT_GREETING}
          </p>
        ) : (
          messages.map((message, index) => {
            if (showTyping && index === messages.length - 1) {
              return <TypingIndicator key={index} />;
            }

            return <MessageBubble key={index} message={message} />;
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
