import { client } from "./client";

export type Role = { id: number; code: string; name: string };
export type Permission = { id: number; code: string; name: string };
export type AdminUser = {
  id: number;
  username: string;
  full_name?: string | null;
  phone?: string | null;
  employee_no?: string | null;
  is_active: boolean;
  roles: string[];
  created_at: string;
};

export type UserLog = {
  id: number;
  user_id?: number | null;
  action: string;
  ip?: string | null;
  user_agent?: string | null;
  created_at: string;
};

export async function listRoles(): Promise<Role[]> {
  const res = await client.get<Role[]>("/admin/roles");
  return res.data;
}

export async function createRole(payload: { code: string; name: string }): Promise<Role> {
  const res = await client.post<Role>("/admin/roles", payload);
  return res.data;
}

export async function listPermissions(): Promise<Permission[]> {
  const res = await client.get<Permission[]>("/admin/permissions");
  return res.data;
}

export async function createPermission(payload: { code: string; name: string }): Promise<Permission> {
  const res = await client.post<Permission>("/admin/permissions", payload);
  return res.data;
}

export async function listUsers(): Promise<AdminUser[]> {
  const res = await client.get<AdminUser[]>("/admin/users");
  return res.data;
}

export async function setUserRoles(userId: number, roleCodes: string[]): Promise<void> {
  await client.put(`/admin/users/${userId}/roles`, { role_codes: roleCodes });
}

export async function listUserLogs(): Promise<UserLog[]> {
  const res = await client.get<UserLog[]>("/admin/user-logs");
  return res.data;
}
