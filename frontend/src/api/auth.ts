import { client } from "./client";

export type TokenOut = { access_token: string; token_type: string };
export type MeOut = { id: number; username: string; full_name?: string | null; roles: string[] };

export async function login(account: string, password: string): Promise<TokenOut> {
  const res = await client.post<TokenOut>("/auth/login", { account, password });
  return res.data;
}

export async function me(): Promise<MeOut> {
  const res = await client.get<MeOut>("/auth/me");
  return res.data;
}
