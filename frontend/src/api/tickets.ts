import { client } from "./client";

export type Ticket = {
  id: number;
  robot_id: number;
  title: string;
  description: string;
  status: string;
  assignee_user_id?: number | null;
  created_at: string;
};

export async function listTickets(): Promise<Ticket[]> {
  const res = await client.get<Ticket[]>("/tickets");
  return res.data;
}

export async function createTicket(payload: { robot_id: number; title: string; description: string; assignee_user_id?: number | null }): Promise<Ticket> {
  const res = await client.post<Ticket>("/tickets", payload);
  return res.data;
}

export async function updateTicket(id: number, payload: { status?: string; assignee_user_id?: number | null }): Promise<Ticket> {
  const res = await client.put<Ticket>(`/tickets/${id}`, payload);
  return res.data;
}

export async function deleteTicket(id: number): Promise<void> {
  await client.delete(`/tickets/${id}`);
}
