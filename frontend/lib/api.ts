// API client for Boussole backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any,
  ) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.details = details;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || "An error occurred",
      response.status,
      errorData.details,
    );
  }
  return response.json();
}

export const api = {
  // Auth endpoints
  async login(email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }),
    });
    return handleResponse<{
      access_token: string;
      refresh_token: string;
      token_type: string;
    }>(response);
  },

  async register(data: {
    email: string;
    password: string;
    full_name: string;
    preferred_language?: string;
  }) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async refreshToken(refreshToken: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    return handleResponse<{
      access_token: string;
      refresh_token: string;
      token_type: string;
    }>(response);
  },

  async getMe(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return handleResponse(response);
  },

  // Sectors endpoints
  async getSectors(
    token: string,
    params?: { skip?: number; limit?: number; active_only?: boolean },
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(
      `${API_BASE_URL}/api/v1/sectors/?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    return handleResponse(response);
  },

  async getSector(token: string, slug: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/sectors/${slug}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return handleResponse(response);
  },

  async getSectorIndicators(
    token: string,
    slug: string,
    params?: { skip?: number; limit?: number },
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(
      `${API_BASE_URL}/api/v1/sectors/${slug}/indicators?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    return handleResponse(response);
  },

  // Data endpoints
  async getIndicators(
    token: string,
    params?: { sector_id?: number; skip?: number; limit?: number },
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(
      `${API_BASE_URL}/api/v1/data/indicators?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    return handleResponse(response);
  },

  async getDataPoints(
    token: string,
    params?: {
      indicator_id?: number;
      sector_id?: number;
      region?: string;
      period_start?: string;
      period_end?: string;
      is_verified?: boolean;
      skip?: number;
      limit?: number;
    },
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(
      `${API_BASE_URL}/api/v1/data/data-points?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    return handleResponse(response);
  },

  async createDataPoint(token: string, data: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/data/data-points`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Analytics endpoints
  async getSectorSummary(
    token: string,
    sectorSlug: string,
    params?: {
      period_start?: string;
      period_end?: string;
      region?: string;
    },
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(
      `${API_BASE_URL}/api/v1/analytics/sectors/${sectorSlug}/summary?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    return handleResponse(response);
  },

  async getSectorTrends(
    token: string,
    sectorSlug: string,
    params?: {
      indicator_slug?: string;
      period_start?: string;
      period_end?: string;
      region?: string;
    },
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(
      `${API_BASE_URL}/api/v1/analytics/sectors/${sectorSlug}/trends?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    return handleResponse(response);
  },

  async getSectorComparison(
    token: string,
    sectorSlug: string,
    compareWith: string[],
    params?: {
      indicator_slug?: string;
      period?: string;
    },
  ) {
    const queryParams = new URLSearchParams({
      ...params,
      compare_with: compareWith.join(","),
    } as any);
    const response = await fetch(
      `${API_BASE_URL}/api/v1/analytics/sectors/${sectorSlug}/comparison?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    return handleResponse(response);
  },

  // RAG endpoints
  async queryRAG(
    token: string,
    query: string,
    params?: {
      language?: string;
      sector_slug?: string;
      top_k?: number;
    },
  ) {
    const queryParams = new URLSearchParams({ ...params, query } as any);
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ query, ...params }),
    });
    return handleResponse(response);
  },

  async uploadDocument(token: string, formData: FormData) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/rag/documents/upload`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      },
    );
    return handleResponse(response);
  },

  async listDocuments(
    token: string,
    params?: {
      sector_slug?: string;
      language?: string;
      skip?: number;
      limit?: number;
    },
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(
      `${API_BASE_URL}/api/v1/rag/documents?${queryParams}`,
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    return handleResponse(response);
  },
};

export default api;
