import { client } from "./client";

export type SensorRow = {
  id: number;
  robot_id: number;
  sensor_type: string;
  value: number;
  ts: string;
};

export async function listSensors(robotId?: number): Promise<SensorRow[]> {
  const res = await client.get<SensorRow[]>("/sensors", { params: robotId ? { robot_id: robotId } : {} });
  return res.data;
}

export async function ingestSensor(payload: { robot_id: number; sensor_type: string; value: number }): Promise<SensorRow> {
  const res = await client.post<SensorRow>("/sensors/ingest", payload);
  return res.data;
}
