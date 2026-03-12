import { client } from "./client";

export type OperationLog = {
  id: number;
  user_id?: number | null;
  method: string;
  path: string;
  summary?: string | null;
  created_at: string;
};

export async function listOperationLogs(): Promise<OperationLog[]> {
  const res = await client.get<OperationLog[]>("/audits/operations");
  return res.data;
}
