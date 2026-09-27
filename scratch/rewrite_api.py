import os

api_path = r"C:\PROJECTS\Fullstack PBX\frontend\src\services\api.ts"

api_ts_content = '''import type { Tenant, Extension, User, SystemStatus } from '../types';

let API_BASE_URL = 'http://localhost:8000';

export const getApiBaseUrl = () => API_BASE_URL;
export const setApiBaseUrl = (url: string) => {
  API_BASE_URL = url.replace(/\\/$/, '');
};

const getHeaders = (token?: string | null, isForm = false) => {
  const headers: Record<string, string> = {};
  if (!isForm) {
    headers['Content-Type'] = 'application/json';
  } else {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

export const apiService = {
  // System Health
  async checkHealth(): Promise<SystemStatus> {
    try {
      const hRes = await fetch(`${API_BASE_URL}/health`);
      const hData = await hRes.json();
      const rRes = await fetch(`${API_BASE_URL}/ready`);
      const rData = await rRes.json();

      return {
        healthy: hRes.ok && hData.status === 'healthy',
        ready: rRes.ok && rData.status === 'ready',
        database: rData.components?.database || 'disconnected',
        redis: rData.components?.redis || 'disconnected',
      };
    } catch {
      return {
        healthy: false,
        ready: false,
        database: 'disconnected',
        redis: 'disconnected',
      };
    }
  },

  // Auth
  async seedSuperAdmin(payload: { username: string; email: string; password: string }) {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/seed-superadmin`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to seed super admin');
    }
    return res.json();
  },

  async login(payload: { username_or_email: string; password: string }) {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Authentication failed');
    }
    return res.json() as Promise<{ access_token: string; user: User }>;
  },

  async getMe(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Invalid token');
    return res.json() as Promise<User>;
  },

  // Tenants
  async getTenants(token: string): Promise<Tenant[]> {
    const res = await fetch(`${API_BASE_URL}/api/v1/tenants`, {
      headers: getHeaders(token),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to fetch tenants');
    }
    return res.json();
  },

  async createTenant(token: string, payload: { name: string; domain: string; sip_domain: string }) {
    const res = await fetch(`${API_BASE_URL}/api/v1/tenants`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create tenant');
    }
    return res.json() as Promise<Tenant>;
  },

  async toggleTenantStatus(token: string, id: string, enabled: boolean) {
    const res = await fetch(`${API_BASE_URL}/api/v1/tenants/${id}/status`, {
      method: 'PUT',
      headers: getHeaders(token),
      body: JSON.stringify({ enabled }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to update tenant status');
    }
    return res.json();
  },

  async deleteTenant(token: string, id: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/tenants/${id}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete tenant');
    }
  },

  // Extensions
  async getExtensions(token: string): Promise<Extension[]> {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions`, {
      headers: getHeaders(token),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to fetch extensions');
    }
    return res.json();
  },

  async createExtension(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create extension');
    }
    return res.json();
  },

  async resetExtensionPassword(token: string, extensionId: string, payload: { new_sip_password?: string; new_voicemail_pin?: string }) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/reset-password`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to reset extension password');
    }
    return res.json();
  },

  async updateExtensionSettings(token: string, extensionId: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/settings`, {
      method: 'PUT',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to update extension settings');
    }
    return res.json();
  },

  // DIDs
  async getDids(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/dids`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to fetch DIDs');
    return res.json();
  },

  async createDid(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/dids`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create DID');
    }
    return res.json();
  },

  async assignDid(token: string, didId: string, tenantId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/dids/${didId}/assign`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify({ tenant_id: tenantId }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to assign DID');
    }
    return res.json();
  },

  async unassignDid(token: string, didId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/dids/${didId}/unassign`, {
      method: 'POST',
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to unassign DID');
    return res.json();
  },

  // Hunt Groups
  async getHuntGroups(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/hunt-groups`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to fetch hunt groups');
    return res.json();
  },

  async createHuntGroup(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/hunt-groups`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create hunt group');
    }
    return res.json();
  },

  // IVR
  async getIvrs(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/ivr`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to fetch IVRs');
    return res.json();
  },

  async createIvr(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/ivr`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create IVR');
    }
    return res.json();
  },

  // Users
  async getUsers(token: string, tenantId?: string): Promise<User[]> {
    const url = tenantId ? `${API_BASE_URL}/api/v1/users?tenant_id=${tenantId}` : `${API_BASE_URL}/api/v1/users`;
    const res = await fetch(url, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch users');
    return res.json();
  },

  async createUser(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/users`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create user');
    }
    return res.json();
  },

  async deleteUser(token: string, userId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete user');
    }
  },

  // Trunks
  async getTrunks(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/trunks`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch trunks');
    return res.json();
  },

  async createTrunk(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/trunks`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create trunk');
    }
    return res.json();
  },

  // Gateways
  async getGateways(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/gateways`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch gateways');
    return res.json();
  },

  async assignGateway(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/gateways/assign`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to assign gateway');
    }
    return res.json();
  },

  // Routing
  async getRoutes(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/routing`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch routing rules');
    return res.json();
  },

  // Queues
  async getQueues(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/queues`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch queues');
    return res.json();
  },

  // FreeSWITCH mod_xml_curl Tester
  async testXmlCurl(domain: string, user: string): Promise<string> {
    const body = new URLSearchParams();
    body.append('section', 'directory');
    body.append('domain', domain);
    body.append('user', user);

    const res = await fetch(`${API_BASE_URL}/freeswitch/xml`, {
      method: 'POST',
      headers: getHeaders(null, true),
      body: body.toString(),
    });
    return res.text();
  },
};
'''

with open(api_path, "w", encoding="utf-8") as f:
    f.write(api_ts_content)

print("api.ts cleanly rewritten.")
