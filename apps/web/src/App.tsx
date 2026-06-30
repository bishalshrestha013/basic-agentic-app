import { APP_TITLE } from "./constants";
import { Composer } from "./components/Composer";
import { MessageList } from "./components/MessageList";
import { useChat } from "./hooks/useChat";

function App() {
  const { messages, isStreaming, error, sendMessage } = useChat();

  return (
    <div className="flex h-screen flex-col bg-white text-neutral-900">
      <header className="border-b border-neutral-200">
        <div className="mx-auto w-full max-w-2xl px-4 py-3">
          <h1 className="text-sm font-semibold text-neutral-700">{APP_TITLE}</h1>
        </div>
      </header>

      <MessageList messages={messages} isStreaming={isStreaming} />

      {error ? (
        <div className="mx-auto w-full max-w-2xl px-4 pb-2">
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        </div>
      ) : null}

      <Composer disabled={isStreaming} onSend={sendMessage} />
    </div>
  );
}

export default App;
