/**
 * VoxParaguay 2026 - API Client
 * Handles all backend communication with offline support
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions extends RequestInit {
  skipOfflineQueue?: boolean;
}

// Offline queue for sync when connection is restored
const OFFLINE_QUEUE_KEY = 'voxparaguay_offline_queue';

interface QueuedRequest {
  id: string;
  endpoint: string;
  method: string;
  body?: any;
  timestamp: number;
}

class ApiClient {
  private getOfflineQueue(): QueuedRequest[] {
    if (typeof window === 'undefined') return [];
    const queue = localStorage.getItem(OFFLINE_QUEUE_KEY);
    return queue ? JSON.parse(queue) : [];
  }

  private saveOfflineQueue(queue: QueuedRequest[]): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
  }

  private addToOfflineQueue(request: Omit<QueuedRequest, 'id' | 'timestamp'>): void {
    const queue = this.getOfflineQueue();
    queue.push({
      ...request,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    });
    this.saveOfflineQueue(queue);
  }

  async syncOfflineQueue(): Promise<{ success: number; failed: number }> {
    const queue = this.getOfflineQueue();
    let success = 0;
    let failed = 0;

    for (const request of queue) {
      try {
        await this.request(request.endpoint, {
          method: request.method,
          body: request.body ? JSON.stringify(request.body) : undefined,
          skipOfflineQueue: true,
        });
        success++;
      } catch {
        failed++;
      }
    }

    // Clear successfully synced items
    this.saveOfflineQueue([]);

    return { success, failed };
  }

  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { skipOfflineQueue, ...fetchOptions } = options;

    const url = `${API_URL}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers: {
          'Content-Type': 'application/json',
          ...fetchOptions.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      // If offline and it's a write operation, queue it
      if (
        !navigator.onLine &&
        !skipOfflineQueue &&
        ['POST', 'PUT', 'PATCH', 'DELETE'].includes(fetchOptions.method || 'GET')
      ) {
        this.addToOfflineQueue({
          endpoint,
          method: fetchOptions.method || 'POST',
          body: fetchOptions.body ? JSON.parse(fetchOptions.body as string) : undefined,
        });
        throw new Error('Sin conexión - solicitud guardada para sincronizar');
      }

      throw error;
    }
  }

  // Campaign endpoints
  async getCampaigns() {
    return this.request<{ campaigns: any[]; total: number }>('/api/campaigns/');
  }

  async getCampaign(id: string) {
    return this.request<any>(`/api/campaigns/${id}`);
  }

  async createCampaign(data: any) {
    return this.request('/api/campaigns/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Response endpoints
  async startSurveySession(data: {
    campaign_id: string;
    agent_id: string;
    canal: string;
    telefono_encriptado: string;
  }) {
    return this.request<{ session_id: string }>('/api/responses/session/start', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async recordResponse(data: {
    campaign_id: string;
    agent_id: string;
    respondent_id: string;
    question_id: string;
    respuesta: any;
    canal: string;
  }) {
    return this.request('/api/responses/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async checkDuplicate(campaign_id: string, telefono_hash: string) {
    return this.request<{ is_duplicate: boolean }>(
      `/api/responses/check-duplicate?campaign_id=${campaign_id}&telefono_hash=${telefono_hash}`,
      { method: 'POST' }
    );
  }

  // Analytics endpoints
  async getCampaignAnalytics(id: string) {
    return this.request<any>(`/api/analytics/campaign/${id}/summary`);
  }

  async getSentimentAnalysis(id: string, params?: { region?: string }) {
    const queryString = params?.region ? `?region=${params.region}` : '';
    return this.request<any>(`/api/analytics/campaign/${id}/sentiment${queryString}`);
  }

  async getGeographicDistribution(id: string) {
    return this.request<any>(`/api/analytics/campaign/${id}/geographic`);
  }

  async getRealtimeStats() {
    return this.request<any>('/api/analytics/dashboard/realtime');
  }

  async generateReport(id: string, formato: 'pdf' | 'csv' | 'json' = 'pdf') {
    return this.request<any>(`/api/analytics/campaign/${id}/report?formato=${formato}`, {
      method: 'POST',
    });
  }
}

export const api = new ApiClient();

// Auto-sync when coming back online
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    api.syncOfflineQueue().then(({ success, failed }) => {
      if (success > 0) {
        console.log(`Sincronizados ${success} registros pendientes`);
      }
      if (failed > 0) {
        console.error(`Fallaron ${failed} registros`);
      }
    });
  });
}
