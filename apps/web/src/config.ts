/** Single source of truth for runtime configuration read from Vite env. */

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const config = {
  apiUrl: API_URL,
  chatStreamEndpoint: `${API_URL}/chat/stream`,
  chatEndpoint: `${API_URL}/chat`,
} as const;
