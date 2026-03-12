import { client } from "./client";

export type Robot = {
  id: number;
  device_id: string;
  model?: string | null;
  location?: string | null;
  status: string;
  ip?: string | null;
  port?: number | null;
  created_at: string;
};

export async function listRobots(): Promise<Robot[]> {
  const res = await client.get<Robot[]>("/robots");
  return res.data;
}

export async function createRobot(payload: Partial<Robot> & { device_id: string }): Promise<Robot> {
  const res = await client.post<Robot>("/robots", payload);
  return res.data;
}

export async function updateRobot(id: number, payload: Partial<Robot>): Promise<Robot> {
  const res = await client.put<Robot>(`/robots/${id}`, payload);
  return res.data;
}

export async function deleteRobot(id: number): Promise<void> {
  await client.delete(`/robots/${id}`);
}
