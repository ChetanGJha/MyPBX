import os

base_comp = r"C:\PROJECTS\Fullstack PBX\frontend\src\components"
base_src = r"C:\PROJECTS\Fullstack PBX\frontend\src"

# 1. TrunksView.tsx
trunks_view = '''import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export const TrunksView: React.FC = () => {
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
      const data = await api.getTrunks();
      setTrunks(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load SIP trunks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrunks();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createTrunk(formData);
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
      alert(err.response?.data?.detail || 'Failed to create SIP trunk');
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

# 2. GatewaysView.tsx
gateways_view = '''import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export const GatewaysView: React.FC = () => {
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
      const [gData, tData] = await Promise.all([api.getGateways(), api.getTenants()]);
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
  }, []);

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.assignGateway(assignForm);
      setShowAssignModal(false);
      alert('Gateway assigned successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Assignment failed');
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

# 3. RoutingView.tsx
routing_view = '''import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export const RoutingView: React.FC = () => {
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadRoutes = async () => {
    try {
      setLoading(true);
      const data = await api.getRoutes();
      setRoutes(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoutes();
  }, []);

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

# 4. QueuesView.tsx
queues_view = '''import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export const QueuesView: React.FC = () => {
  const [queues, setQueues] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadQueues = async () => {
    try {
      setLoading(true);
      const data = await api.getQueues();
      setQueues(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueues();
  }, []);

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

# 5. UPDATE SIDEBAR.TSX
sidebar_tsx = '''import React from 'react';
import { TerrixLogo } from './TerrixLogo';

interface SidebarProps {
  activePage: string;
  setActivePage: (page: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  setActivePage,
  collapsed,
}) => {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="brand">
        <TerrixLogo size={collapsed ? 24 : 32} />
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
          className={`nav-item ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActivePage('dashboard')}
        >
          <i className="bi bi-grid"></i>
          <span className="nav-text">Dashboard</span>
        </button>

        <div className="nav-label">Telephony Engine</div>
        <button
          className={`nav-item ${activePage === 'extensions' ? 'active' : ''}`}
          onClick={() => setActivePage('extensions')}
        >
          <i className="bi bi-telephone"></i>
          <span className="nav-text">Extensions</span>
        </button>

        <button
          className={`nav-item ${activePage === 'trunks' ? 'active' : ''}`}
          onClick={() => setActivePage('trunks')}
        >
          <i className="bi bi-diagram-3"></i>
          <span className="nav-text">SIP Trunks</span>
        </button>

        <button
          className={`nav-item ${activePage === 'gateways' ? 'active' : ''}`}
          onClick={() => setActivePage('gateways')}
        >
          <i className="bi bi-hdd-network"></i>
          <span className="nav-text">Gateways</span>
        </button>

        <button
          className={`nav-item ${activePage === 'routing' ? 'active' : ''}`}
          onClick={() => setActivePage('routing')}
        >
          <i className="bi bi-sign-turn-right"></i>
          <span className="nav-text">Call Routing</span>
        </button>

        <button
          className={`nav-item ${activePage === 'queues' ? 'active' : ''}`}
          onClick={() => setActivePage('queues')}
        >
          <i className="bi bi-people"></i>
          <span className="nav-text">Call Queues</span>
        </button>

        <div className="nav-label">Administration</div>
        <button
          className={`nav-item ${activePage === 'users' ? 'active' : ''}`}
          onClick={() => setActivePage('users')}
        >
          <i className="bi bi-person-badge"></i>
          <span className="nav-text">Users & Admins</span>
        </button>

        <button
          className={`nav-item ${activePage === 'tenants' ? 'active' : ''}`}
          onClick={() => setActivePage('tenants')}
        >
          <i className="bi bi-building"></i>
          <span className="nav-text">Tenants</span>
        </button>

        <button
          className={`nav-item ${activePage === 'auth' ? 'active' : ''}`}
          onClick={() => setActivePage('auth')}
        >
          <i className="bi bi-shield-check"></i>
          <span className="nav-text">Auth Controls</span>
        </button>
      </div>
    </aside>
  );
};
'''

with open(os.path.join(base_comp, "Sidebar.tsx"), "w", encoding="utf-8") as f:
    f.write(sidebar_tsx)

# 6. UPDATE API.TS
api_ts = '''import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  login: async (formData: FormData) => {
    const response = await apiClient.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },
  getMe: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  // Tenants
  getTenants: async () => {
    const response = await apiClient.get('/tenants');
    return response.data;
  },
  createTenant: async (data: any) => {
    const response = await apiClient.post('/tenants', data);
    return response.data;
  },

  // Extensions
  getExtensions: async () => {
    const response = await apiClient.get('/extensions');
    return response.data;
  },
  createExtension: async (data: any) => {
    const response = await apiClient.post('/extensions', data);
    return response.data;
  },

  // Users
  getUsers: async () => {
    const response = await apiClient.get('/users');
    return response.data;
  },
  createUser: async (data: any) => {
    const response = await apiClient.post('/users', data);
    return response.data;
  },

  // Trunks
  getTrunks: async () => {
    const response = await apiClient.get('/trunks');
    return response.data;
  },
  createTrunk: async (data: any) => {
    const response = await apiClient.post('/trunks', data);
    return response.data;
  },

  // Gateways
  getGateways: async () => {
    const response = await apiClient.get('/gateways');
    return response.data;
  },
  assignGateway: async (data: any) => {
    const response = await apiClient.post('/gateways/assign', data);
    return response.data;
  },

  // Routing
  getRoutes: async () => {
    const response = await apiClient.get('/routing');
    return response.data;
  },

  // Queues
  getQueues: async () => {
    const response = await apiClient.get('/queues');
    return response.data;
  },
};
'''

with open(os.path.join(base_src, "services", "api.ts"), "w", encoding="utf-8") as f:
    f.write(api_ts)

# 7. UPDATE APP.TSX
app_tsx = '''import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { LoginScreen } from './components/LoginScreen';
import { DashboardView } from './components/DashboardView';
import { ExtensionsView } from './components/ExtensionsView';
import { TenantsView } from './components/TenantsView';
import { UsersView } from './components/UsersView';
import { AuthView } from './components/AuthView';
import { TrunksView } from './components/TrunksView';
import { GatewaysView } from './components/GatewaysView';
import { RoutingView } from './components/RoutingView';
import { QueuesView } from './components/QueuesView';

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [activePage, setActivePage] = useState<string>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div id="appScreen" style={{ display: 'block' }}>
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <div className="main">
        <Topbar
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
          onLogout={handleLogout}
        />

        {activePage === 'dashboard' && <DashboardView />}
        {activePage === 'extensions' && <ExtensionsView />}
        {activePage === 'trunks' && <TrunksView />}
        {activePage === 'gateways' && <GatewaysView />}
        {activePage === 'routing' && <RoutingView />}
        {activePage === 'queues' && <QueuesView />}
        {activePage === 'users' && <UsersView />}
        {activePage === 'tenants' && <TenantsView />}
        {activePage === 'auth' && <AuthView />}
      </div>
    </div>
  );
}

export default App;
'''

with open(os.path.join(base_src, "App.tsx"), "w", encoding="utf-8") as f:
    f.write(app_tsx)

print("Frontend files successfully updated in C:\\PROJECTS\\Fullstack PBX\\frontend")
