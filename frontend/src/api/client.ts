import type {
  ApiClientOptions,
  RequisitionInput,
  WorkflowRunPayload,
} from "./types";

function resolveUrl(base: string, path: string): string {
  if (!base || base === "/") {
    return path;
  }
  return `${base.replace(/\/$/, "")}${path}`;
}

async function parseJsonSafe(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { message: text };
  }
}

export function createApiClient(options: ApiClientOptions) {
  const { baseUrl, getAuthHeaders } = options;

  async function fetchJson<T>(
    path: string,
    init: RequestInit & { parse?: "json" | "text" },
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(getAuthHeaders?.() ?? {}),
    };

    const res = await fetch(resolveUrl(baseUrl, path), {
      ...init,
      headers: { ...headers, ...(init.headers as Record<string, string>) },
    });

    const body = await parseJsonSafe(res);
    if (!res.ok) {
      const err = body as { message?: string; detail?: string };
      throw new Error(err.message ?? err.detail ?? `HTTP ${res.status}`);
    }

    return body as T;
  }

  return {
    async healthCheck(): Promise<boolean> {
      try {
        await fetchJson<{ status?: string }>("/api/v1/health", {
          method: "GET",
        });
        return true;
      } catch {
        return false;
      }
    },

    async createRun(input: RequisitionInput): Promise<WorkflowRunPayload> {
      return fetchJson<WorkflowRunPayload>("/api/v1/runs", {
        method: "POST",
        body: JSON.stringify({ requisition: input }),
      });
    },

    async getRun(runId: string): Promise<WorkflowRunPayload> {
      return fetchJson<WorkflowRunPayload>(`/api/v1/runs/${encodeURIComponent(runId)}`, {
        method: "GET",
      });
    },

    async approveRun(runId: string): Promise<WorkflowRunPayload> {
      return fetchJson<WorkflowRunPayload>(
        `/api/v1/runs/${encodeURIComponent(runId)}/approve`,
        { method: "POST", body: JSON.stringify({}) },
      );
    },

    async rerunFromStage(
      runId: string,
      body: { from_stage: "researcher" | "evaluator" | "recommender"; notes?: string },
    ): Promise<WorkflowRunPayload> {
      return fetchJson<WorkflowRunPayload>(
        `/api/v1/runs/${encodeURIComponent(runId)}/rerun`,
        { method: "POST", body: JSON.stringify(body) },
      );
    },
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;
