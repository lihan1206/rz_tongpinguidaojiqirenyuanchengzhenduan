import { client } from "./client";

export type FaultRule = {
  id: number;
  name: string;
  sensor_type: string;
  operator: string;
  threshold: number;
  level: string;
  enabled: boolean;
  created_at: string;
};

export type FaultLog = {
  id: number;
  robot_id: number;
  rule_id?: number | null;
  fault_type: string;
  description: string;
  level: string;
  status: string;
  created_at: string;
};

export async function listFaultRules(): Promise<FaultRule[]> {
  const res = await client.get<FaultRule[]>("/faults/rules");
  return res.data;
}

export async function createFaultRule(payload: Omit<FaultRule, "id" | "created_at">): Promise<FaultRule> {
  const res = await client.post<FaultRule>("/faults/rules", payload);
  return res.data;
}

export async function listFaultLogs(): Promise<FaultLog[]> {
  const res = await client.get<FaultLog[]>("/faults/logs");
  return res.data;
}
