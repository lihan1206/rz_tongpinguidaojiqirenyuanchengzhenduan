import { client } from "./client";

export type Overview = { robots: number; faults: number; tickets: number; commands: number; sensor_rows: number };

export async function getOverview(): Promise<Overview> {
  const res = await client.get<Overview>("/reports/overview");
  return res.data;
}
