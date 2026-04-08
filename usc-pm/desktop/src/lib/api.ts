import { getBackend, getToken } from "./auth";

async function req(path: string, init: RequestInit = {}) {
  const base = await getBackend();
  const token = await getToken();
  if (!base) throw new Error("Backend URL not configured");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> ?? {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const r = await fetch(`${base}${path}`, { ...init, headers });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.status === 204 ? null : r.json();
}

export const api = {
  servers: () => req("/api/servers"),
  channels: {
    list: () => req("/api/channels"),
    save: (channels: any[]) => req("/api/channels", { method: "POST", body: JSON.stringify({ channels }) }),
  },
  rules: {
    list: () => req("/api/rules"),
    create: (r: any) => req("/api/rules", { method: "POST", body: JSON.stringify(r) }),
    delete: (id: number) => req(`/api/rules/${id}`, { method: "DELETE" }),
  },
  macro: () => req("/api/macro"),
  approve: (pid: number) => req(`/api/pending/${pid}/approve`, { method: "POST" }),
  reject: (pid: number) => req(`/api/pending/${pid}/reject`, { method: "POST" }),
  unity: {
    list: () => req("/api/unity"),
    add: (entry: string) => req("/api/unity", { method: "POST", body: JSON.stringify({ entry }) }),
  },
};
