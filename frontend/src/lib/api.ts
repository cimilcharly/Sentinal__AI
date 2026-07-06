/**
 * API client for frontend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

export class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    method: string,
    endpoint: string,
    body?: any
  ): Promise<ApiResponse<T>> {
    const url = `${API_BASE}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || 'An error occurred',
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 500,
      };
    }
  }

  // Authentication endpoints
  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    if (response.ok && data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  async getCurrentUser() {
    return this.request('GET', '/auth/me');
  }

  // Organization endpoints
  async getOrganization() {
    return this.request('GET', '/organizations');
  }

  async listUsers() {
    return this.request('GET', '/organizations/users');
  }

  // Threat endpoints
  async analyzeThreat(employeeId: string, daysLookback: number = 30) {
    return this.request('POST', '/threats/analyze', {
      employee_id: employeeId,
      days_lookback: daysLookback,
    });
  }

  async getAssessments(days: number = 7, flaggedOnly: boolean = false) {
    const params = new URLSearchParams({
      days: days.toString(),
      flagged_only: flaggedOnly.toString(),
    });
    return this.request('GET', `/threats/assessments?${params}`);
  }

  async getEmployeeAssessment(employeeId: string) {
    return this.request('GET', `/threats/assessments/${employeeId}`);
  }

  // Report endpoints
  async generateReport(reportType: string, title: string, daysLookback: number = 30) {
    return this.request('POST', '/reports/generate', {
      report_type: reportType,
      title,
      days_lookback: daysLookback,
    });
  }

  async getReports(limit: number = 10) {
    const params = new URLSearchParams({ limit: limit.toString() });
    return this.request('GET', `/reports?${params}`);
  }

  // Integration endpoints
  async listIntegrations() {
    return this.request('GET', '/integrations');
  }

  async createIntegration(type: string, name: string, credentials: any) {
    return this.request('POST', '/integrations', {
      integration_type: type,
      name,
      credentials,
    });
  }

  async testIntegration(integrationId: string) {
    return this.request('POST', `/integrations/${integrationId}/test`);
  }

  async syncIntegration(integrationId: string) {
    return this.request('POST', `/integrations/${integrationId}/sync`);
  }
}

export const apiClient = new ApiClient();
