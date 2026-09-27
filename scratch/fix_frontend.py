import os

base_comp = r"C:\PROJECTS\Fullstack PBX\frontend\src\components"
base_src = r"C:\PROJECTS\Fullstack PBX\frontend\src"
base_services = r"C:\PROJECTS\Fullstack PBX\frontend\src\services"

# 1. SERVICES/API.TS
api_ts = '''import type { Tenant, Extension, User, SystemStatus } from '../types';

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

  // Auth & Seeding
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

  async createExtension(
    token: string,
    payload: {
      tenant_id?: string;
      extension_number: string;
      display_name: string;
      email?: string;
      sip_password: string;
      voicemail_pin?: string;
    }
  ) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create extension');
    }
    return res.json() as Promise<Extension>;
  },

  async resetPassword(token: string, extensionId: string, payload: { new_sip_password?: string; new_voicemail_pin?: string }) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/reset-password`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to reset extension credentials');
    }
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

  // Users Management
  async getUsers(token: string, tenantId?: string): Promise<User[]> {
    const url = tenantId ? `${API_BASE_URL}/api/v1/users?tenant_id=${tenantId}` : `${API_BASE_URL}/api/v1/users`;
    const res = await fetch(url, {
      headers: getHeaders(token),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to fetch users');
    }
    return res.json();
  },

  async createUser(
    token: string,
    payload: {
      tenant_id?: string;
      username: string;
      email: string;
      password: string;
      first_name?: string;
      last_name?: string;
      role: string;
    }
  ) {
    const res = await fetch(`${API_BASE_URL}/api/v1/users`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create user');
    }
    return res.json() as Promise<User>;
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
    const res = await fetch(`${API_BASE_URL}/api/v1/trunks`, {
      headers: getHeaders(token),
    });
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
    const res = await fetch(`${API_BASE_URL}/api/v1/gateways`, {
      headers: getHeaders(token),
    });
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
    const res = await fetch(`${API_BASE_URL}/api/v1/routing`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to fetch routing rules');
    return res.json();
  },

  // Queues
  async getQueues(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/queues`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to fetch queues');
    return res.json();
  },
};
'''

with open(os.path.join(base_services, "api.ts"), "w", encoding="utf-8") as f:
    f.write(api_ts)


# 2. SIDEBAR.TSX
sidebar_tsx = '''import React from 'react';
import { TerrixLogo } from './TerrixLogo';
import type { User } from '../types';

interface SidebarProps {
  collapsed: boolean;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: User | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  activeTab,
  setActiveTab,
  user,
}) => {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="brand">
        <TerrixLogo size={collapsed ? 'small' : 'medium'} />
        {!collapsed && (
          <div className="brand-name">
            Terrix AI
            <small>Technologies</small>
          </div>
        )}
      </div>

      <div className="sidebar-body">
        <div className="nav-label">Overview</div>
        <button
          className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <i className="bi bi-grid"></i>
          <span className="nav-text">Dashboard</span>
        </button>

        <div className="nav-label">Telephony Engine</div>
        <button
          className={`nav-item ${activeTab === 'extensions' ? 'active' : ''}`}
          onClick={() => setActiveTab('extensions')}
        >
          <i className="bi bi-telephone"></i>
          <span className="nav-text">Extensions</span>
        </button>

        <button
          className={`nav-item ${activeTab === 'trunks' ? 'active' : ''}`}
          onClick={() => setActiveTab('trunks')}
        >
          <i className="bi bi-diagram-3"></i>
          <span className="nav-text">SIP Trunks</span>
        </button>

        <button
          className={`nav-item ${activeTab === 'gateways' ? 'active' : ''}`}
          onClick={() => setActiveTab('gateways')}
        >
          <i className="bi bi-hdd-network"></i>
          <span className="nav-text">Gateways</span>
        </button>

        <button
          className={`nav-item ${activeTab === 'routing' ? 'active' : ''}`}
          onClick={() => setActiveTab('routing')}
        >
          <i className="bi bi-sign-turn-right"></i>
          <span className="nav-text">Call Routing</span>
        </button>

        <button
          className={`nav-item ${activeTab === 'queues' ? 'active' : ''}`}
          onClick={() => setActiveTab('queues')}
        >
          <i className="bi bi-people"></i>
          <span className="nav-text">Call Queues</span>
        </button>

        <div className="nav-label">Administration</div>
        <button
          className={`nav-item ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <i className="bi bi-person-badge"></i>
          <span className="nav-text">Users & Admins</span>
        </button>

        <button
          className={`nav-item ${activeTab === 'tenants' ? 'active' : ''}`}
          onClick={() => setActiveTab('tenants')}
        >
          <i className="bi bi-building"></i>
          <span className="nav-text">Tenants</span>
        </button>

        <button
          className={`nav-item ${activeTab === 'auth' ? 'active' : ''}`}
          onClick={() => setActiveTab('auth')}
        >
          <i className="bi bi-shield-check"></i>
          <span className="nav-text">Auth Controls</span>
        </button>

        <button
          className={`nav-item ${activeTab === 'xmlcurl' ? 'active' : ''}`}
          onClick={() => setActiveTab('xmlcurl')}
        >
          <i className="bi bi-code-slash"></i>
          <span className="nav-text">mod_xml_curl</span>
        </button>
      </div>
    </aside>
  );
};
'''

with open(os.path.join(base_comp, "Sidebar.tsx"), "w", encoding="utf-8") as f:
    f.write(sidebar_tsx)


# 3. TRUNKSVIEW.TSX
trunks_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface TrunksViewProps {
  token: string;
}

export const TrunksView: React.FC<TrunksViewProps> = ({ token }) => {
  const [trunks, setTrunks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    host: '',
    port: 5060,
    transport: 'UDP',
    username: '',
    password: '',
    realm: '',
    priority: 1,
    register: true,
    srtp: false
  });

  const loadTrunks = async () => {
    try {
      setLoading(true);
      const data = await apiService.getTrunks(token);
      setTrunks(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load SIP trunks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrunks();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createTrunk(token, formData);
      setShowModal(false);
      setFormData({
        name: '',
        host: '',
        port: 5060,
        transport: 'UDP',
        username: '',
        password: '',
        realm: '',
        priority: 1,
        register: true,
        srtp: false
      });
      loadTrunks();
    } catch (err: any) {
      alert(err.message || 'Failed to create SIP trunk');
    }
  };

  return (
    <div className="content">
      <div className="page-head">
        <div>
          <div className="eyebrow">Telephony Infrastructure</div>
          <div className="page-title">SIP Trunks</div>
          <div className="page-sub">Configure carrier SIP trunk connections and gateway routes</div>
        </div>
        <div className="head-actions">
          <button className="btn-primaryx" onClick={() => setShowModal(true)}>
            <i className="bi bi-plus-lg me-1"></i> Add SIP Trunk
          </button>
        </div>
      </div>

      {error && <div className="alert alert-danger mb-3">{error}</div>}

      <div className="card">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Trunk Name</th>
                <th>SIP Host</th>
                <th>Port</th>
                <th>Transport</th>
                <th>Username</th>
                <th>Priority</th>
                <th>Registration</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="text-center py-4">Loading SIP trunks...</td></tr>
              ) : trunks.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-4 text-muted">No SIP trunks configured yet</td></tr>
              ) : (
                trunks.map((t) => (
                  <tr key={t.id}>
                    <td><strong>{t.name}</strong></td>
                    <td><code className="code-box">{t.host}</code></td>
                    <td>{t.port}</td>
                    <td><span className="badge badge-grey">{t.transport}</span></td>
                    <td>{t.username || '-'}</td>
                    <td>{t.priority}</td>
                    <td>{t.register ? <span className="badge badge-green">REGISTERED</span> : <span className="badge badge-grey">IP AUTH</span>}</td>
                    <td>{t.enabled ? <span className="badge badge-green">ACTIVE</span> : <span className="badge badge-orange">DISABLED</span>}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-backdropx show">
          <div className="pbx-modal">
            <div className="modal-head">
              <div className="modal-icon"><i className="bi bi-diagram-3"></i></div>
              <div>
                <h3>Create New SIP Trunk</h3>
                <p>Configure provider proxy parameters and authentication</p>
              </div>
              <button className="modal-close" onClick={() => setShowModal(false)}><i className="bi bi-x-lg"></i></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="modal-grid">
                  <div className="field">
                    <label>Trunk Name</label>
                    <input required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Twilio Primary" />
                  </div>
                  <div className="field">
                    <label>SIP Host / Proxy</label>
                    <input required value={formData.host} onChange={e => setFormData({...formData, host: e.target.value})} placeholder="e.g. sip.twilio.com" />
                  </div>
                  <div className="field">
                    <label>SIP Port</label>
                    <input type="number" value={formData.port} onChange={e => setFormData({...formData, port: parseInt(e.target.value) || 5060})} />
                  </div>
                  <div className="field">
                    <label>Transport</label>
                    <select value={formData.transport} onChange={e => setFormData({...formData, transport: e.target.value})}>
                      <option value="UDP">UDP</option>
                      <option value="TCP">TCP</option>
                      <option value="TLS">TLS</option>
                    </select>
                  </div>
                  <div className="field">
                    <label>Auth Username</label>
                    <input value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} placeholder="Optional for IP auth" />
                  </div>
                  <div className="field">
                    <label>Auth Password</label>
                    <input type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} placeholder="Optional" />
                  </div>
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-lightx" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primaryx">Save Trunk</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "TrunksView.tsx"), "w", encoding="utf-8") as f:
    f.write(trunks_view)


# 4. GATEWAYSVIEW.TSX
gateways_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface GatewaysViewProps {
  token: string;
}

export const GatewaysView: React.FC<GatewaysViewProps> = ({ token }) => {
  const [gateways, setGateways] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignForm, setAssignForm] = useState({
    tenant_id: '',
    gateway_id: '',
    direction: 'inbound_outbound',
    priority: 1,
    caller_id_policy: 'tenant_default',
    allow_outbound: true,
    accept_inbound: true,
    allow_international: false
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [gData, tData] = await Promise.all([
        apiService.getGateways(token),
        apiService.getTenants(token)
      ]);
      setGateways(gData);
      setTenants(tData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.assignGateway(token, assignForm);
      setShowAssignModal(false);
      alert('Gateway assigned successfully!');
    } catch (err: any) {
      alert(err.message || 'Assignment failed');
    }
  };

  return (
    <div className="content">
      <div className="page-head">
        <div>
          <div className="eyebrow">FreeSWITCH Sofia Engine</div>
          <div className="page-title">Gateways & Trunk Assignments</div>
          <div className="page-sub">Assign gateway channels and specify inbound/outbound priority rules per tenant</div>
        </div>
        <div className="head-actions">
          <button className="btn-primaryx" onClick={() => setShowAssignModal(true)}>
            <i className="bi bi-link-45deg me-1"></i> Assign Gateway to Tenant
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Gateway Name</th>
                <th>SIP Proxy</th>
                <th>Assigned Tenant</th>
                <th>Codecs</th>
                <th>Registration</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="text-center py-4">Loading Sofia Gateways...</td></tr>
              ) : gateways.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-4 text-muted">No gateways registered</td></tr>
              ) : (
                gateways.map((g) => (
                  <tr key={g.id}>
                    <td><strong>{g.name}</strong></td>
                    <td><code className="code-box">{g.proxy}</code></td>
                    <td>{g.tenant_name || <span className="badge badge-grey">Global</span>}</td>
                    <td>{g.codecs}</td>
                    <td>{g.register ? <span className="badge badge-green">REGISTERED</span> : <span className="badge badge-grey">INBOUND ONLY</span>}</td>
                    <td><span className="badge badge-green">ONLINE</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showAssignModal && (
        <div className="modal-backdropx show">
          <div className="pbx-modal">
            <div className="modal-head">
              <div className="modal-icon"><i className="bi bi-hdd-network"></i></div>
              <div>
                <h3>Assign Gateway to Tenant</h3>
                <p>Set call direction, caller ID policies and routing limits</p>
              </div>
              <button className="modal-close" onClick={() => setShowAssignModal(false)}><i className="bi bi-x-lg"></i></button>
            </div>
            <form onSubmit={handleAssign}>
              <div className="modal-body">
                <div className="modal-grid">
                  <div className="field">
                    <label>Target Tenant</label>
                    <select required value={assignForm.tenant_id} onChange={e => setAssignForm({...assignForm, tenant_id: e.target.value})}>
                      <option value="">-- Select Tenant --</option>
                      {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                    </select>
                  </div>
                  <div className="field">
                    <label>Sofia Gateway</label>
                    <select required value={assignForm.gateway_id} onChange={e => setAssignForm({...assignForm, gateway_id: e.target.value})}>
                      <option value="">-- Select Gateway --</option>
                      {gateways.map(g => <option key={g.id} value={g.id}>{g.name} ({g.proxy})</option>)}
                    </select>
                  </div>
                  <div className="field">
                    <label>Call Direction</label>
                    <select value={assignForm.direction} onChange={e => setAssignForm({...assignForm, direction: e.target.value})}>
                      <option value="inbound_outbound">Inbound & Outbound</option>
                      <option value="inbound_only">Inbound Only</option>
                      <option value="outbound_only">Outbound Only</option>
                    </select>
                  </div>
                  <div className="field">
                    <label>Route Priority (1 = Highest)</label>
                    <input type="number" value={assignForm.priority} onChange={e => setAssignForm({...assignForm, priority: parseInt(e.target.value) || 1})} />
                  </div>
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-lightx" onClick={() => setShowAssignModal(false)}>Cancel</button>
                <button type="submit" className="btn-primaryx">Save Assignment</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "GatewaysView.tsx"), "w", encoding="utf-8") as f:
    f.write(gateways_view)


# 5. ROUTINGVIEW.TSX
routing_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface RoutingViewProps {
  token: string;
}

export const RoutingView: React.FC<RoutingViewProps> = ({ token }) => {
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadRoutes = async () => {
    try {
      setLoading(true);
      const data = await apiService.getRoutes(token);
      setRoutes(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoutes();
  }, [token]);

  return (
    <div className="content">
      <div className="page-head">
        <div>
          <div className="eyebrow">Dialplan & Call Distribution</div>
          <div className="page-title">Call Routing</div>
          <div className="page-sub">Manage inbound DID number routing and outbound pattern matching</div>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Route Name</th>
                <th>DID / Pattern</th>
                <th>Type</th>
                <th>Destination Type</th>
                <th>Target Destination</th>
                <th>Priority</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="text-center py-4">Loading routing rules...</td></tr>
              ) : routes.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-4 text-muted">No routing rules created</td></tr>
              ) : (
                routes.map((r) => (
                  <tr key={r.id}>
                    <td><strong>{r.name}</strong></td>
                    <td><code className="code-box">{r.did_number || r.regex_pattern || '*'}</code></td>
                    <td><span className="badge badge-grey">{r.route_type}</span></td>
                    <td>{r.destination_type}</td>
                    <td><strong>{r.destination}</strong></td>
                    <td>{r.priority}</td>
                    <td><span className="badge badge-green">ENABLED</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
'''

with open(os.path.join(base_comp, "RoutingView.tsx"), "w", encoding="utf-8") as f:
    f.write(routing_view)


# 6. QUEUESVIEW.TSX
queues_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface QueuesViewProps {
  token: string;
}

export const QueuesView: React.FC<QueuesViewProps> = ({ token }) => {
  const [queues, setQueues] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadQueues = async () => {
    try {
      setLoading(true);
      const data = await apiService.getQueues(token);
      setQueues(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueues();
  }, [token]);

  return (
    <div className="content">
      <div className="page-head">
        <div>
          <div className="eyebrow">Call Center & ACR Engine</div>
          <div className="page-title">Call Queues</div>
          <div className="page-sub">FreeSWITCH mod_callcenter queues and agent distribution strategies</div>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Queue Name</th>
                <th>Extension</th>
                <th>Strategy</th>
                <th>Agent Timeout</th>
                <th>Max Wait Time</th>
                <th>Agents</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="text-center py-4">Loading call queues...</td></tr>
              ) : queues.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-4 text-muted">No call queues configured</td></tr>
              ) : (
                queues.map((q) => (
                  <tr key={q.id}>
                    <td><strong>{q.name}</strong></td>
                    <td><code className="code-box">{q.queue_number}</code></td>
                    <td><span className="badge badge-grey">{q.strategy}</span></td>
                    <td>{q.agent_timeout}s</td>
                    <td>{q.max_wait_time}s</td>
                    <td>{q.agents || 'All Extension Agents'}</td>
                    <td><span className="badge badge-green">ACTIVE</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
'''

with open(os.path.join(base_comp, "QueuesView.tsx"), "w", encoding="utf-8") as f:
    f.write(queues_view)


# 7. APP.TSX
app_tsx = '''import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { LoginScreen } from './components/LoginScreen';
import { DashboardView } from './components/DashboardView';
import { AuthView } from './components/AuthView';
import { TenantsView } from './components/TenantsView';
import { ExtensionsView } from './components/ExtensionsView';
import { UsersView } from './components/UsersView';
import { XmlCurlConsole } from './components/XmlCurlConsole';
import { TrunksView } from './components/TrunksView';
import { GatewaysView } from './components/GatewaysView';
import { RoutingView } from './components/RoutingView';
import { QueuesView } from './components/QueuesView';
import { apiService } from './services/api';
import type { SystemStatus, User, Tenant, Extension } from './types';

export const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [status, setStatus] = useState<SystemStatus>({
    healthy: false,
    ready: false,
    database: 'unknown',
    redis: 'unknown',
  });

  const [token, setToken] = useState<string | null>(localStorage.getItem('pbx_access_token'));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('pbx_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [extensions, setExtensions] = useState<Extension[]>([]);

  useEffect(() => {
    const check = async () => {
      const s = await apiService.checkHealth();
      setStatus(s);
    };
    check();
    const interval = setInterval(check, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (token) {
      apiService.getTenants(token).then(setTenants).catch(() => {});
      apiService.getExtensions(token).then(setExtensions).catch(() => {});
    }
  }, [token]);

  const handleLoginSuccess = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem('pbx_access_token', newToken);
    localStorage.setItem('pbx_user', JSON.stringify(newUser));
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('pbx_access_token');
    localStorage.removeItem('pbx_user');
  };

  if (!token) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div id="appScreen" style={{ display: 'block' }}>
      <Sidebar
        collapsed={collapsed}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
      />

      <main className="main">
        <Topbar
          collapsed={collapsed}
          onToggleCollapse={() => setCollapsed(!collapsed)}
          status={status}
          user={user}
          onLogout={handleLogout}
        />

        <div className="content">
          {activeTab === 'dashboard' && (
            <DashboardView
              status={status}
              user={user}
              tenantCount={tenants.length}
              extensionCount={extensions.length}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'auth' && (
            <AuthView onLoginSuccess={handleLoginSuccess} user={user} />
          )}

          {activeTab === 'tenants' && <TenantsView token={token} />}

          {activeTab === 'users' && <UsersView token={token} currentUser={user} />}

          {activeTab === 'extensions' && <ExtensionsView token={token} />}

          {activeTab === 'trunks' && <TrunksView token={token} />}

          {activeTab === 'gateways' && <GatewaysView token={token} />}

          {activeTab === 'routing' && <RoutingView token={token} />}

          {activeTab === 'queues' && <QueuesView token={token} />}

          {activeTab === 'xmlcurl' && <XmlCurlConsole />}
        </div>
      </main>
    </div>
  );
};

export default App;
'''

with open(os.path.join(base_src, "App.tsx"), "w", encoding="utf-8") as f:
    f.write(app_tsx)

print("Frontend files successfully fixed and updated in C:\\PROJECTS\\Fullstack PBX\\frontend")
