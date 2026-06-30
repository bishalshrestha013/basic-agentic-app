import { ROLE } from "./constants";

export type Role = (typeof ROLE)[keyof typeof ROLE];

export interface ChatMessage {
  role: Role;
  content: string;
}
