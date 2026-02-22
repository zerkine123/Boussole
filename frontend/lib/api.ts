// API client for Boussole backend
// Hardcoded for debugging (CORRECTED URL)
export const API_BASE_URL = "https://boussole-production.up.railway.app";
console.log("DEBUG: API_BASE_URL is hardcoded to:", API_BASE_URL);

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
    // FastAPI returns detail as a string for HTTPException, or an array for 422 validation errors
    const rawDetail = errorData.detail ?? errorData.message;
    const message = Array.isArray(rawDetail)
      ? rawDetail.map((e: any) => `${e.loc?.join(".")}: ${e.msg}`).join("; ")
      : typeof rawDetail === "string"
        ? rawDetail
        : `Request failed (${response.status})`;
    throw new ApiError(message, response.status, errorData.details);
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

  async createSector(token: string, data: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/sectors`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async updateSector(token: string, slug: string, data: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/sectors/${slug}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async deleteSector(token: string, slug: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/sectors/${slug}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
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
  // Chat endpoints
  async chatCompletion(
    message: string,
    history: { role: "user" | "assistant"; content: string }[],
  ) {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/completion`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });
    return handleResponse<{ reply: string }>(response);
  },

  // Onboarding endpoints
  async getOnboardingData(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/data`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return handleResponse<any>(response);
  },

  async completeOnboarding(token: string, preferences: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/complete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ preferences }),
    });
    return handleResponse(response);
  },

  async skipOnboarding(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/skip`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({}),
    });
    return handleResponse(response);
  },

  // Search endpoints
  async getDashboardLayout(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/layout`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return handleResponse<{ layout: string[], metrics?: any }>(response);
  },

  async analyzeSearch(token: string | null, query: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/search/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify({ query }),
    });
    return handleResponse<any>(response);
  },

  async getDynamicLayout(query: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/search/dynamic-layout`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      },
    );
    return handleResponse<any>(response);
  },

  async generateDashboardLayout(token: string | null, query: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/layout/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` })
      },
      body: JSON.stringify({ query }),
    });
    return handleResponse<{ layout: any[] }>(response);
  },

  // Financial endpoints
  async simulateFinancials(data: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/finance/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return handleResponse<any>(response);
  },

  // Insights endpoints
  async getInsights(
    token: string,
    params?: { sector_id?: number; limit?: number }
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(`${API_BASE_URL}/api/v1/insights/?${queryParams}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  async generateInsights(
    token: string,
    params: { sector_slug: string; period_start?: string; period_end?: string }
  ) {
    const queryParams = new URLSearchParams(params as any);
    const response = await fetch(`${API_BASE_URL}/api/v1/insights/generate?${queryParams}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    });
    return handleResponse(response);
  },

  // Widgets / Data Query endpoint
  async queryData(
    token: string | null,
    payload: { metric_slugs: string[]; group_by?: string; filters?: any }
  ) {
    const response = await fetch(`${API_BASE_URL}/api/v1/data/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(response);
  },

  async triggerSeedMetrics(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/admin/seed-metrics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    return handleResponse<any>(response);
  },
};

export default api;
