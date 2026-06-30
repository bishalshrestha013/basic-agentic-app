import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { ROLE } from "../constants";
import type { ChatMessage } from "../types";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === ROLE.USER;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={
          isUser
            ? "max-w-[80%] rounded-2xl rounded-br-sm bg-neutral-900 px-4 py-2.5 text-neutral-50"
            : "max-w-[80%] rounded-2xl rounded-bl-sm bg-neutral-100 px-4 py-2.5 text-neutral-900"
        }
      >
        <div className="markdown break-words text-[15px] leading-relaxed">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
