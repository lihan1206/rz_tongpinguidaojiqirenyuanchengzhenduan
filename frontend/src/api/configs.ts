import { client } from "./client";

export type SystemConfig = { id: number; key: string; value: string; updated_at: string };

export async function listConfigs(): Promise<SystemConfig[]> {
  const res = await client.get<SystemConfig[]>("/configs");
  return res.data;
}

export async function upsertConfig(payload: { key: string; value: string }): Promise<SystemConfig> {
  const res = await client.post<SystemConfig>("/configs", payload);
  return res.data;
}
