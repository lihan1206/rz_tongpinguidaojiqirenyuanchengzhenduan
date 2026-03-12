import { client } from "./client";

export type RemoteCommand = {
  id: number;
  robot_id: number;
  command_type: string;
  params: Record<string, unknown>;
  status: string;
  result?: string | null;
  created_at: string;
  updated_at: string;
};

export async function listCommands(): Promise<RemoteCommand[]> {
  const res = await client.get<RemoteCommand[]>("/commands");
  return res.data;
}

export async function createCommand(payload: { robot_id: number; command_type: string; params: Record<string, unknown> }): Promise<RemoteCommand> {
  const res = await client.post<RemoteCommand>("/commands", payload);
  return res.data;
}

export async function updateCommand(id: number, payload: { status: string; result?: string | null }): Promise<RemoteCommand> {
  const res = await client.put<RemoteCommand>(`/commands/${id}`, payload);
  return res.data;
}

export async function deleteCommand(id: number): Promise<void> {
  await client.delete(`/commands/${id}`);
}
