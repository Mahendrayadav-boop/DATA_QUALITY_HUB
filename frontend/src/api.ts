import type { Dashboard, Dataset, QualityCheck, QualityRun } from "./types";

const baseUrl = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail ?? "Request failed");
  }
  return response.json();
}

export const api = {
  dashboard: () => request<Dashboard>("/api/dashboard"),
  datasets: () => request<Dataset[]>("/api/datasets"),
  createDataset: (data: Omit<Dataset, "id" | "status" | "created_at">) =>
    request<Dataset>("/api/datasets", { method: "POST", body: JSON.stringify(data) }),
  checks: (datasetId?: number) =>
    request<QualityCheck[]>(`/api/checks${datasetId ? `?dataset_id=${datasetId}` : ""}`),
  createCheck: (data: Omit<QualityCheck, "id" | "status">) =>
    request<QualityCheck>("/api/checks", { method: "POST", body: JSON.stringify(data) }),
  runCheck: (id: number) =>
    request<QualityRun>(`/api/checks/${id}/run`, { method: "POST" }),
  runs: () => request<QualityRun[]>("/api/runs"),
  sync: (provider: string) =>
    request<{ provider: string; status: string; items: number }>(
      `/api/integrations/${provider}/sync`,
      { method: "POST" },
    ),
};
