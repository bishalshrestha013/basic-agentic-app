import { config } from "../config";
import type { ChatMessage } from "../types";

interface StreamHandlers {
  onToken: (token: string) => void;
  onError: (message: string) => void;
}

interface SseFrame {
  event: string;
  data: string;
}

function parseFrame(raw: string): SseFrame {
  let event = "message";
  const dataLines: string[] = [];

  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) {
      event = line.slice("event:".length).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trim());
    }
  }

  return { event, data: dataLines.join("\n") };
}

/**
 * POST to the streaming chat endpoint and forward assistant tokens as they
 * arrive. Resolves when the stream completes.
 */
export async function streamChat(
  message: string,
  history: ChatMessage[],
  handlers: StreamHandlers,
): Promise<void> {
  const response = await fetch(config.chatStreamEndpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok || !response.body) {
    handlers.onError(`Request failed with status ${response.status}`);

    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    // SSE lines arrive CRLF-terminated; normalize so frames split on "\n\n".
    buffer += decoder.decode(value, { stream: true }).replace(/\r/g, "");

    let separatorIndex = buffer.indexOf("\n\n");
    while (separatorIndex !== -1) {
      const rawFrame = buffer.slice(0, separatorIndex);
      buffer = buffer.slice(separatorIndex + 2);

      const { event, data } = parseFrame(rawFrame);
      if (data) {
        const payload = JSON.parse(data);
        if (event === "token") {
          handlers.onToken(payload.token);
        } else if (event === "error") {
          handlers.onError(payload.error);
        }
      }

      separatorIndex = buffer.indexOf("\n\n");
    }
  }
}
