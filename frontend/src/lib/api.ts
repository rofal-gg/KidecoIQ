/**
 * KidecoIQ — API Client
 * ======================
 * Helper untuk komunikasi dengan backend FastAPI.
 *
 * Di development, Next.js rewrite di next.config.ts mengarahkan
 * /api/* → http://localhost:8000/* sehingga frontend cukup fetch
 * relatif tanpa perlu full URL.
 */

const API_BASE = "/api";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {
      // ignore parse error, use default message
    }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}
