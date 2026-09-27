import os

base_comp = r"C:\PROJECTS\Fullstack PBX\frontend\src\components"
base_src = r"C:\PROJECTS\Fullstack PBX\frontend\src"

# 1. UPDATE SERVICES/API.TS WITH ALL NEW ENDPOINTS
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

  // Tenants (Requirement 2 & 3: Disable option & Safeguards)
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

  // Extensions (Requirement 1, 7, 11, 12: Password Reset, Voicemail-to-Email, Call Forwarding, Follow Me)
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

  // DID Inventory (Requirement 6)
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

  // Hunt Groups (Requirement 10)
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

  // IVR Menus (Requirement 8)
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

  // Users, Trunks, Gateways, Routes, Queues
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

  async getRoutes(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/routing`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch routing rules');
    return res.json();
  },

  async getQueues(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/queues`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch queues');
    return res.json();
  },
};
'''

with open(os.path.join(base_src, "services", "api.ts"), "w", encoding="utf-8") as f:
    f.write(api_ts)

# 2. TENANTSVIEW.TSX (Requirement 2 & 3: Disable Toggle & Deletion Safeguard Modal)
tenants_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { Tenant } from '../types';
import { Building2, Plus, RefreshCw, Trash2, Search, AlertCircle, Power } from 'lucide-react';

interface TenantsViewProps {
  token: string;
}

export const TenantsView: React.FC<TenantsViewProps> = ({ token }) => {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  // Requirement 2: Delete Confirmation Modal & Error Safeguard State
  const [tenantToDelete, setTenantToDelete] = useState<Tenant | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    sip_domain: '',
  });

  const loadTenants = async () => {
    try {
      setLoading(true);
      const data = await apiService.getTenants(token);
      setTenants(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTenants();
  }, [token]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createTenant(token, formData);
      setShowCreateModal(false);
      setFormData({ name: '', domain: '', sip_domain: '' });
      loadTenants();
    } catch (err: any) {
      alert(err.message || 'Failed to create tenant');
    }
  };

  // Requirement 3: Disable / Enable Tenants Option
  const handleToggleStatus = async (tenant: Tenant) => {
    try {
      await apiService.toggleTenantStatus(token, tenant.id, !tenant.enabled);
      loadTenants();
    } catch (err: any) {
      alert(err.message || 'Failed to update tenant status');
    }
  };

  // Requirement 2: Delete with Confirmation Modal & Safeguards
  const confirmDeleteTenant = async () => {
    if (!tenantToDelete) return;
    setDeleteError(null);
    try {
      await apiService.deleteTenant(token, tenantToDelete.id);
      setTenantToDelete(null);
      loadTenants();
    } catch (err: any) {
      setDeleteError(err.message);
    }
  };

  const filteredTenants = tenants.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.domain.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Multi-Tenant Core</div>
          <h1 className="page-title">Tenant Organizations</h1>
          <p className="page-sub">Isolated customer domains, maximum extensions, and status controls</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-secondary" onClick={loadTenants}><RefreshCw size={16} /></button>
          <button className="btn-primary" onClick={() => setShowCreateModal(true)}><Plus size={16} /> Create Tenant</button>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
            <input
              className="form-control"
              style={{ paddingLeft: '36px', height: '38px', fontSize: '12px' }}
              placeholder="Search tenants..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Tenant Name</th>
                <th>Domain</th>
                <th>SIP Domain</th>
                <th>Timezone</th>
                <th>Limits</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="text-center py-4">Loading tenants...</td></tr>
              ) : filteredTenants.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-4 text-muted">No tenants found</td></tr>
              ) : (
                filteredTenants.map((t) => (
                  <tr key={t.id}>
                    <td>
                      <div style={{ fontWeight: 700, color: '#111827' }}>{t.name}</div>
                      <div style={{ fontSize: '10px', color: '#9CA3AF' }}>ID: {t.id.slice(0, 8)}...</div>
                    </td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{t.domain}</code></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{t.sip_domain}</code></td>
                    <td>{t.timezone}</td>
                    <td>{t.max_extensions} Exts / {t.max_concurrent_calls} Calls</td>
                    <td>
                      {t.enabled ? (
                        <span className="terrix-badge green">ACTIVE</span>
                      ) : (
                        <span className="terrix-badge orange">DISABLED</span>
                      )}
                    </td>
                    <td className="text-right">
                      {/* Requirement 3: Disable/Enable Toggle */}
                      <button
                        className={`btn-secondary ${t.enabled ? 'text-amber-600' : 'text-emerald-600'}`}
                        style={{ padding: '6px 10px', fontSize: '11px', marginRight: '6px' }}
                        onClick={() => handleToggleStatus(t)}
                        title={t.enabled ? 'Disable Tenant' : 'Enable Tenant'}
                      >
                        <Power size={14} style={{ marginRight: '4px' }} />
                        {t.enabled ? 'Disable' : 'Enable'}
                      </button>

                      {/* Requirement 2: Delete with Confirmation Modal */}
                      <button
                        className="btn-secondary text-rose-600"
                        style={{ padding: '6px 10px', fontSize: '11px' }}
                        onClick={() => { setTenantToDelete(t); setDeleteError(null); }}
                        title="Delete Tenant"
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CREATE TENANT MODAL */}
      {showCreateModal && (
        <div className="modal-backdrop">
          <div className="terrix-modal">
            <div className="modal-head">
              <div className="modal-icon"><Building2 size={20} /></div>
              <div>
                <h3>Create New Tenant</h3>
                <p>Provision a new isolated domain and PBX context</p>
              </div>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-group mb-3">
                  <label className="form-label">Tenant Name</label>
                  <input required className="form-control" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="e.g. Acme Corp" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Domain Name</label>
                  <input required className="form-control" value={formData.domain} onChange={(e) => setFormData({ ...formData, domain: e.target.value })} placeholder="e.g. acme.pbx.com" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">SIP Domain</label>
                  <input className="form-control" value={formData.sip_domain} onChange={(e) => setFormData({ ...formData, sip_domain: e.target.value })} placeholder="e.g. acme.local (Optional)" />
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Create Tenant</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* REQUIREMENT 2: DELETE CONFIRMATION & SAFEGUARD ERROR MODAL */}
      {tenantToDelete && (
        <div className="modal-backdrop">
          <div className="terrix-modal" style={{ maxWidth: '480px' }}>
            <div className="modal-head">
              <div className="modal-icon text-rose-600 bg-rose-50"><AlertCircle size={20} /></div>
              <div>
                <h3>Confirm Tenant Deletion</h3>
                <p>Are you sure you want to delete <strong>{tenantToDelete.name}</strong>?</p>
              </div>
              <button className="modal-close" onClick={() => setTenantToDelete(null)}>×</button>
            </div>
            <div className="modal-body">
              {deleteError ? (
                <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold leading-relaxed">
                  <div className="font-extrabold mb-1">Cannot Delete Tenant!</div>
                  {deleteError}
                </div>
              ) : (
                <p className="text-xs text-slate-600">
                  This action will soft-delete tenant <strong>{tenantToDelete.domain}</strong>. Ensure all allocated extensions, DIDs, and gateways have been unassigned first.
                </p>
              )}
            </div>
            <div className="modal-foot">
              <button className="btn-secondary" onClick={() => setTenantToDelete(null)}>Cancel</button>
              {!deleteError && (
                <button className="btn-primary bg-rose-600 border-rose-600 hover:bg-rose-700" onClick={confirmDeleteTenant}>
                  Yes, Delete Tenant
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "TenantsView.tsx"), "w", encoding="utf-8") as f:
    f.write(tenants_view)


# 3. DIDSVIEW.TSX (Requirement 6: DID Inventory Management & Trunk-wise Tenant Assignment)
dids_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Hash, Plus, Link2, Unlink, Search, CheckCircle2 } from 'lucide-react';

interface DidsViewProps {
  token: string;
}

export const DidsView: React.FC<DidsViewProps> = ({ token }) => {
  const [dids, setDids] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [trunks, setTrunks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const [showAddModal, setShowAddModal] = useState(false);
  const [addForm, setAddForm] = useState({ did_number: '', trunk_id: '', destination_type: 'extension', destination: '' });

  const [didToAssign, setDidToAssign] = useState<any>(null);
  const [selectedTenantId, setSelectedTenantId] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [dData, tData, sData] = await Promise.all([
        apiService.getDids(token),
        apiService.getTenants(token),
        apiService.getTrunks(token)
      ]);
      setDids(dData);
      setTenants(tData);
      setTrunks(sData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const handleAddDid = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createDid(token, addForm);
      setShowAddModal(false);
      setAddForm({ did_number: '', trunk_id: '', destination_type: 'extension', destination: '' });
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to add DID');
    }
  };

  const handleAssignDid = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!didToAssign || !selectedTenantId) return;
    try {
      await apiService.assignDid(token, didToAssign.id, selectedTenantId);
      setDidToAssign(null);
      setSelectedTenantId('');
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to assign DID');
    }
  };

  const handleUnassignDid = async (didId: string) => {
    try {
      await apiService.unassignDid(token, didId);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to unassign DID');
    }
  };

  const filtered = dids.filter(d => d.did_number.includes(search));

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Telephony Inventory</div>
          <h1 className="page-title">DID Number Inventory</h1>
          <p className="page-sub">Manage global DID phone numbers provider-wise and allocate free numbers to tenants</p>
        </div>
        <div>
          <button className="btn-primary" onClick={() => setShowAddModal(true)}>
            <Plus size={16} /> Add DID to Inventory
          </button>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', gap: '12px' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
            <input
              className="form-control"
              style={{ paddingLeft: '36px', height: '38px', fontSize: '12px' }}
              placeholder="Search DID numbers..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>DID Number</th>
                <th>Provider SIP Trunk / Gateway</th>
                <th>Assigned Tenant</th>
                <th>Destination Target</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="text-center py-4">Loading DIDs...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-4 text-muted">No DIDs in inventory</td></tr>
              ) : (
                filtered.map(d => (
                  <tr key={d.id}>
                    <td><strong style={{ fontSize: '13px', color: '#111827' }}>{d.did_number}</strong></td>
                    <td><span className="terrix-badge grey">{d.trunk_name || 'Global Provider'}</span></td>
                    <td>
                      {d.tenant_name ? (
                        <span className="terrix-badge orange">{d.tenant_name} ({d.tenant_domain})</span>
                      ) : (
                        <span className="terrix-badge green"><CheckCircle2 size={10} style={{ marginRight: '4px' }} /> FREE / UNALLOCATED</span>
                      )}
                    </td>
                    <td>{d.destination_type}: {d.destination || 'Default Route'}</td>
                    <td><span className="terrix-badge green">ACTIVE</span></td>
                    <td className="text-right">
                      {d.tenant_id ? (
                        <button className="btn-secondary text-amber-600" style={{ padding: '4px 8px', fontSize: '11px' }} onClick={() => handleUnassignDid(d.id)}>
                          <Unlink size={13} style={{ marginRight: '4px' }} /> Unassign
                        </button>
                      ) : (
                        <button className="btn-primary" style={{ padding: '4px 10px', fontSize: '11px' }} onClick={() => setDidToAssign(d)}>
                          <Link2 size={13} style={{ marginRight: '4px' }} /> Assign to Tenant
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ADD DID MODAL */}
      {showAddModal && (
        <div className="modal-backdrop">
          <div className="terrix-modal">
            <div className="modal-head">
              <div className="modal-icon"><Hash size={20} /></div>
              <div>
                <h3>Add DID Number to Inventory</h3>
                <p>Import DID from carrier SIP trunk into global pool</p>
              </div>
              <button className="modal-close" onClick={() => setShowAddModal(false)}>×</button>
            </div>
            <form onSubmit={handleAddDid}>
              <div className="modal-body">
                <div className="form-group mb-3">
                  <label className="form-label">DID Phone Number</label>
                  <input required className="form-control" value={addForm.did_number} onChange={e => setAddForm({...addForm, did_number: e.target.value})} placeholder="e.g. +18005550199" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Provider SIP Trunk / Gateway</label>
                  <select className="form-control" value={addForm.trunk_id} onChange={e => setAddForm({...addForm, trunk_id: e.target.value})}>
                    <option value="">-- Select Host SIP Trunk --</option>
                    {trunks.map(t => <option key={t.id} value={t.id}>{t.name} ({t.host})</option>)}
                  </select>
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Add DID</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ASSIGN DID MODAL */}
      {didToAssign && (
        <div className="modal-backdrop">
          <div className="terrix-modal" style={{ maxWidth: '440px' }}>
            <div className="modal-head">
              <div className="modal-icon"><Link2 size={20} /></div>
              <div>
                <h3>Assign DID to Tenant</h3>
                <p>Assign DID <strong>{didToAssign.did_number}</strong> to a customer domain</p>
              </div>
              <button className="modal-close" onClick={() => setDidToAssign(null)}>×</button>
            </div>
            <form onSubmit={handleAssignDid}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Target Tenant</label>
                  <select required className="form-control" value={selectedTenantId} onChange={e => setSelectedTenantId(e.target.value)}>
                    <option value="">-- Select Tenant --</option>
                    {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                  </select>
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setDidToAssign(null)}>Cancel</button>
                <button type="submit" className="btn-primary">Assign Number</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "DidsView.tsx"), "w", encoding="utf-8") as f:
    f.write(dids_view)


# 4. IVRVIEW.TSX (Requirement 8: IVR Flow Designer)
ivr_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { GitBranch, Plus, Mic, Volume2 } from 'lucide-react';

interface IvrViewProps {
  token: string;
}

export const IvrView: React.FC<IvrViewProps> = ({ token }) => {
  const [ivrs, setIvrs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ name: '', greeting_audio: 'welcome_prompt.wav', direct_extension_dial: true, timeout: 10 });

  const loadIvrs = async () => {
    try {
      setLoading(true);
      const data = await apiService.getIvrs(token);
      setIvrs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIvrs();
  }, [token]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createIvr(token, formData);
      setShowModal(false);
      setFormData({ name: '', greeting_audio: 'welcome_prompt.wav', direct_extension_dial: true, timeout: 10 });
      loadIvrs();
    } catch (err: any) {
      alert(err.message || 'Failed to create IVR');
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Auto-Attendant Engine</div>
          <h1 className="page-title">IVR Flow Designer</h1>
          <p className="page-sub">Design multi-level interactive voice response menus and DTMF key actions per tenant</p>
        </div>
        <div>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} /> Create IVR Flow
          </button>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>IVR Menu Name</th>
                <th>Greeting Audio Prompt</th>
                <th>Direct Extension Dial</th>
                <th>Digit Timeout</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="text-center py-4">Loading IVR flows...</td></tr>
              ) : ivrs.length === 0 ? (
                <tr><td colSpan={5} className="text-center py-4 text-muted">No IVR menus designed yet</td></tr>
              ) : (
                ivrs.map(i => (
                  <tr key={i.id}>
                    <td><strong style={{ color: '#111827' }}>{i.name}</strong></td>
                    <td><span className="terrix-badge grey"><Volume2 size={10} style={{ marginRight: '4px' }} /> {i.greeting_audio}</span></td>
                    <td>{i.direct_extension_dial ? <span className="terrix-badge green">ENABLED</span> : <span className="terrix-badge grey">DISABLED</span>}</td>
                    <td>{i.timeout} seconds</td>
                    <td><span className="terrix-badge green">ACTIVE</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-backdrop">
          <div className="terrix-modal">
            <div className="modal-head">
              <div className="modal-icon"><GitBranch size={20} /></div>
              <div>
                <h3>Create IVR Menu Flow</h3>
                <p>Configure audio prompt & DTMF keypad routing rules</p>
              </div>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-group mb-3">
                  <label className="form-label">IVR Flow Name</label>
                  <input required className="form-control" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Main Company Welcome IVR" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Greeting Audio File</label>
                  <input className="form-control" value={formData.greeting_audio} onChange={e => setFormData({...formData, greeting_audio: e.target.value})} placeholder="welcome_prompt.wav" />
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save IVR Flow</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "IvrView.tsx"), "w", encoding="utf-8") as f:
    f.write(ivr_view)


# 5. HUNTGROUPSVIEW.TSX (Requirement 10: Per Tenant Hunt Groups)
hunt_groups_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { PhoneForwarded, Plus } from 'lucide-react';

interface HuntGroupsViewProps {
  token: string;
}

export const HuntGroupsView: React.FC<HuntGroupsViewProps> = ({ token }) => {
  const [huntGroups, setHuntGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ name: '', extension_number: '', strategy: 'sequential', members: '1001, 1002', timeout: 20 });

  const loadHuntGroups = async () => {
    try {
      setLoading(true);
      const data = await apiService.getHuntGroups(token);
      setHuntGroups(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHuntGroups();
  }, [token]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createHuntGroup(token, formData);
      setShowModal(false);
      setFormData({ name: '', extension_number: '', strategy: 'sequential', members: '1001, 1002', timeout: 20 });
      loadHuntGroups();
    } catch (err: any) {
      alert(err.message || 'Failed to create hunt group');
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Call Distribution</div>
          <h1 className="page-title">Hunt Groups</h1>
          <p className="page-sub">Configure sequential, simultaneous & circular hunt groups per tenant</p>
        </div>
        <div>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} /> Create Hunt Group
          </button>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Hunt Group Name</th>
                <th>Extension Number</th>
                <th>Ring Strategy</th>
                <th>Member Extensions</th>
                <th>Timeout</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="text-center py-4">Loading hunt groups...</td></tr>
              ) : huntGroups.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-4 text-muted">No hunt groups created</td></tr>
              ) : (
                huntGroups.map(h => (
                  <tr key={h.id}>
                    <td><strong style={{ color: '#111827' }}>{h.name}</strong></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{h.extension_number}</code></td>
                    <td><span className="terrix-badge grey">{h.strategy.toUpperCase()}</span></td>
                    <td>{h.members}</td>
                    <td>{h.timeout}s</td>
                    <td><span className="terrix-badge green">ACTIVE</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-backdrop">
          <div className="terrix-modal">
            <div className="modal-head">
              <div className="modal-icon"><PhoneForwarded size={20} /></div>
              <div>
                <h3>Create Hunt Group</h3>
                <p>Ring extension sequences when receiving calls</p>
              </div>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-group mb-3">
                  <label className="form-label">Hunt Group Name</label>
                  <input required className="form-control" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Sales Team Hunt Group" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Virtual Extension Number</label>
                  <input required className="form-control" value={formData.extension_number} onChange={e => setFormData({...formData, extension_number: e.target.value})} placeholder="e.g. 8001" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Ring Strategy</label>
                  <select className="form-control" value={formData.strategy} onChange={e => setFormData({...formData, strategy: e.target.value})}>
                    <option value="sequential">Sequential (One by one)</option>
                    <option value="simultaneous">Simultaneous (Ring all)</option>
                    <option value="circular">Circular (Round-robin)</option>
                  </select>
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Member Extensions (Comma separated)</label>
                  <input required className="form-control" value={formData.members} onChange={e => setFormData({...formData, members: e.target.value})} placeholder="e.g. 1001, 1002, 1003" />
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Hunt Group</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "HuntGroupsView.tsx"), "w", encoding="utf-8") as f:
    f.write(hunt_groups_view)


# 6. EXTENSIONSVIEW.TSX (Requirement 1, 7, 11, 12: Reset Password, Voicemail-to-Email, Call Forwarding, Follow Me)
extensions_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { Extension } from '../types';
import { Phone, Plus, RefreshCw, KeyRound, Settings, Search, CheckCircle2 } from 'lucide-react';

interface ExtensionsViewProps {
  token: string;
}

export const ExtensionsView: React.FC<ExtensionsViewProps> = ({ token }) => {
  const [extensions, setExtensions] = useState<Extension[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Requirement 1: Password Reset Modal State
  const [resetTarget, setResetTarget] = useState<any>(null);
  const [resetForm, setResetForm] = useState({ new_sip_password: '', new_voicemail_pin: '' });

  // Requirement 7, 11, 12: Extension Settings Modal State (Voicemail-to-Email, Call Forwarding, Follow Me)
  const [settingsTarget, setSettingsTarget] = useState<any>(null);
  const [settingsForm, setSettingsForm] = useState({
    voicemail_email: '',
    voicemail_to_email: false,
    follow_me_enabled: false,
    follow_me_destination: '',
    follow_me_timeout: 20,
    call_forward_enabled: false,
    call_forward_type: 'always',
    call_forward_destination: ''
  });

  const [createForm, setCreateForm] = useState({
    extension_number: '',
    display_name: '',
    email: '',
    sip_password: 'Password123!',
    voicemail_pin: '1234',
    tenant_id: '',
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [extData, tenData] = await Promise.all([
        apiService.getExtensions(token),
        apiService.getTenants(token)
      ]);
      setExtensions(extData);
      setTenants(tenData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.createExtension(token, createForm);
      setShowCreateModal(false);
      setCreateForm({ extension_number: '', display_name: '', email: '', sip_password: 'Password123!', voicemail_pin: '1234', tenant_id: '' });
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to create extension');
    }
  };

  // Requirement 1: Handle Reset Password
  const handleResetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetTarget) return;
    try {
      await apiService.resetExtensionPassword(token, resetTarget.id, resetForm);
      alert('Extension credentials reset successfully!');
      setResetTarget(null);
      setResetForm({ new_sip_password: '', new_voicemail_pin: '' });
    } catch (err: any) {
      alert(err.message || 'Failed to reset credentials');
    }
  };

  // Requirement 7, 11, 12: Handle Extension Settings
  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!settingsTarget) return;
    try {
      await apiService.updateExtensionSettings(token, settingsTarget.id, settingsForm);
      alert('Extension settings updated successfully!');
      setSettingsTarget(null);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to update settings');
    }
  };

  const openSettings = (ext: any) => {
    setSettingsTarget(ext);
    setSettingsForm({
      voicemail_email: ext.voicemail_email || ext.email || '',
      voicemail_to_email: ext.voicemail_to_email || false,
      follow_me_enabled: ext.follow_me_enabled || false,
      follow_me_destination: ext.follow_me_destination || '',
      follow_me_timeout: ext.follow_me_timeout || 20,
      call_forward_enabled: ext.call_forward_enabled || false,
      call_forward_type: ext.call_forward_type || 'always',
      call_forward_destination: ext.call_forward_destination || ''
    });
  };

  const filtered = extensions.filter(e =>
    e.extension_number.includes(search) ||
    e.display_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">SIP Endpoints</div>
          <h1 className="page-title">Extensions Directory</h1>
          <p className="page-sub">SIP endpoints, voicemail-to-email, call forwarding & follow-me routing</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-primary" onClick={() => setShowCreateModal(true)}><Plus size={16} /> Add Extension</button>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
            <input
              className="form-control"
              style={{ paddingLeft: '36px', height: '38px', fontSize: '12px' }}
              placeholder="Search extensions..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Ext #</th>
                <th>Display Name</th>
                <th>Tenant Domain</th>
                <th>Voicemail Email</th>
                <th>Call Forwarding</th>
                <th>Follow Me</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="text-center py-4">Loading extensions...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-4 text-muted">No extensions found</td></tr>
              ) : (
                filtered.map(e => (
                  <tr key={e.id}>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '12px', fontWeight: 700 }}>{e.extension_number}</code></td>
                    <td><div style={{ fontWeight: 700, color: '#111827' }}>{e.display_name}</div></td>
                    <td><span className="terrix-badge orange">{(e as any).tenant_domain || 'Global'}</span></td>
                    <td>
                      {(e as any).voicemail_to_email ? (
                        <span className="terrix-badge green">{(e as any).voicemail_email || e.email}</span>
                      ) : (
                        <span className="terrix-badge grey">Disabled</span>
                      )}
                    </td>
                    <td>
                      {(e as any).call_forward_enabled ? (
                        <span className="terrix-badge green">{(e as any).call_forward_type}: {(e as any).call_forward_destination}</span>
                      ) : (
                        <span className="terrix-badge grey">Off</span>
                      )}
                    </td>
                    <td>
                      {(e as any).follow_me_enabled ? (
                        <span className="terrix-badge green">Active ({(e as any).follow_me_destination})</span>
                      ) : (
                        <span className="terrix-badge grey">Off</span>
                      )}
                    </td>
                    <td className="text-right">
                      {/* Requirement 1: Reset Password Button */}
                      <button className="btn-secondary text-amber-600" style={{ padding: '4px 8px', fontSize: '11px', marginRight: '6px' }} onClick={() => setResetTarget(e)}>
                        <KeyRound size={13} style={{ marginRight: '4px' }} /> Reset Password
                      </button>

                      {/* Requirement 7, 11, 12: Config Button */}
                      <button className="btn-primary" style={{ padding: '4px 10px', fontSize: '11px' }} onClick={() => openSettings(e)}>
                        <Settings size={13} style={{ marginRight: '4px' }} /> Features
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CREATE EXTENSION MODAL */}
      {showCreateModal && (
        <div className="modal-backdrop">
          <div className="terrix-modal">
            <div className="modal-head">
              <div className="modal-icon"><Phone size={20} /></div>
              <div>
                <h3>Create New Extension</h3>
                <p>Provision a SIP extension for IP phones & softphones</p>
              </div>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-group mb-3">
                  <label className="form-label">Target Tenant</label>
                  <select required className="form-control" value={createForm.tenant_id} onChange={e => setCreateForm({...createForm, tenant_id: e.target.value})}>
                    <option value="">-- Select Tenant --</option>
                    {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                  </select>
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Extension Number</label>
                  <input required className="form-control" value={createForm.extension_number} onChange={e => setCreateForm({...createForm, extension_number: e.target.value})} placeholder="e.g. 1001" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Display Name</label>
                  <input required className="form-control" value={createForm.display_name} onChange={e => setCreateForm({...createForm, display_name: e.target.value})} placeholder="e.g. John Doe" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">SIP Secret Password</label>
                  <input required type="password" className="form-control" value={createForm.sip_password} onChange={e => setCreateForm({...createForm, sip_password: e.target.value})} />
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Create Extension</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* REQUIREMENT 1: RESET PASSWORD MODAL */}
      {resetTarget && (
        <div className="modal-backdrop">
          <div className="terrix-modal" style={{ maxWidth: '440px' }}>
            <div className="modal-head">
              <div className="modal-icon"><KeyRound size={20} /></div>
              <div>
                <h3>Reset Credentials</h3>
                <p>Update SIP Password / PIN for extension <strong>{resetTarget.extension_number}</strong></p>
              </div>
              <button className="modal-close" onClick={() => setResetTarget(null)}>×</button>
            </div>
            <form onSubmit={handleResetPasswordSubmit}>
              <div className="modal-body">
                <div className="form-group mb-3">
                  <label className="form-label">New SIP Password</label>
                  <input className="form-control" type="password" value={resetForm.new_sip_password} onChange={e => setResetForm({...resetForm, new_sip_password: e.target.value})} placeholder="Min 6 characters" />
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">New Voicemail PIN</label>
                  <input className="form-control" value={resetForm.new_voicemail_pin} onChange={e => setResetForm({...resetForm, new_voicemail_pin: e.target.value})} placeholder="e.g. 1234" />
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setResetTarget(null)}>Cancel</button>
                <button type="submit" className="btn-primary">Update Password</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* REQUIREMENT 7, 11, 12: EXTENSION FEATURES SETTINGS MODAL */}
      {settingsTarget && (
        <div className="modal-backdrop">
          <div className="terrix-modal">
            <div className="modal-head">
              <div className="modal-icon"><Settings size={20} /></div>
              <div>
                <h3>Extension Features & Routing</h3>
                <p>Configure Voicemail-to-Email, Call Forwarding & Follow Me for Ext <strong>{settingsTarget.extension_number}</strong></p>
              </div>
              <button className="modal-close" onClick={() => setSettingsTarget(null)}>×</button>
            </div>
            <form onSubmit={handleSaveSettings}>
              <div className="modal-body">
                {/* REQUIREMENT 7: VOICEMAIL-TO-EMAIL */}
                <div className="p-3.5 mb-4 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="font-extrabold text-xs text-slate-800 mb-2 flex items-center gap-2">
                    <span>Voicemail-to-Email Routing</span>
                  </div>
                  <div className="flex items-center gap-3 mb-2">
                    <input type="checkbox" id="vmToEmail" checked={settingsForm.voicemail_to_email} onChange={e => setSettingsForm({...settingsForm, voicemail_to_email: e.target.checked})} />
                    <label htmlFor="vmToEmail" className="text-xs font-bold text-slate-700 cursor-pointer">Route Voicemail Audio Recordings to Email</label>
                  </div>
                  {settingsForm.voicemail_to_email && (
                    <input className="form-control" type="email" value={settingsForm.voicemail_email} onChange={e => setSettingsForm({...settingsForm, voicemail_email: e.target.value})} placeholder="Destination email address" />
                  )}
                </div>

                {/* REQUIREMENT 11: CALL FORWARDING */}
                <div className="p-3.5 mb-4 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="font-extrabold text-xs text-slate-800 mb-2">Call Forwarding Options</div>
                  <div className="flex items-center gap-3 mb-2">
                    <input type="checkbox" id="cfEnabled" checked={settingsForm.call_forward_enabled} onChange={e => setSettingsForm({...settingsForm, call_forward_enabled: e.target.checked})} />
                    <label htmlFor="cfEnabled" className="text-xs font-bold text-slate-700 cursor-pointer">Enable Call Forwarding</label>
                  </div>
                  {settingsForm.call_forward_enabled && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                      <div>
                        <label className="form-label">Condition</label>
                        <select className="form-control" value={settingsForm.call_forward_type} onChange={e => setSettingsForm({...settingsForm, call_forward_type: e.target.value})}>
                          <option value="always">Always Forward</option>
                          <option value="busy">Forward When Busy</option>
                          <option value="no_answer">Forward When No Answer</option>
                        </select>
                      </div>
                      <div>
                        <label className="form-label">Forward Destination Phone #</label>
                        <input className="form-control" value={settingsForm.call_forward_destination} onChange={e => setSettingsForm({...settingsForm, call_forward_destination: e.target.value})} placeholder="e.g. +14155550123" />
                      </div>
                    </div>
                  )}
                </div>

                {/* REQUIREMENT 12: FOLLOW ME */}
                <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="font-extrabold text-xs text-slate-800 mb-2">Follow Me Backup Routing</div>
                  <div className="flex items-center gap-3 mb-2">
                    <input type="checkbox" id="fmEnabled" checked={settingsForm.follow_me_enabled} onChange={e => setSettingsForm({...settingsForm, follow_me_enabled: e.target.checked})} />
                    <label htmlFor="fmEnabled" className="text-xs font-bold text-slate-700 cursor-pointer">Enable Follow Me Backup Ring</label>
                  </div>
                  {settingsForm.follow_me_enabled && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                      <div>
                        <label className="form-label">Backup Ring Number</label>
                        <input className="form-control" value={settingsForm.follow_me_destination} onChange={e => setSettingsForm({...settingsForm, follow_me_destination: e.target.value})} placeholder="e.g. +14155550999" />
                      </div>
                      <div>
                        <label className="form-label">Primary Timeout (seconds)</label>
                        <input type="number" className="form-control" value={settingsForm.follow_me_timeout} onChange={e => setSettingsForm({...settingsForm, follow_me_timeout: parseInt(e.target.value) || 20})} />
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setSettingsTarget(null)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Extension Features</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "ExtensionsView.tsx"), "w", encoding="utf-8") as f:
    f.write(extensions_view)


# 7. UPDATE SIDEBAR.TSX & APP.TSX TO ADD DIDS, IVR FLOW, HUNT GROUPS NAVIGATION
sidebar_tsx = '''import React from 'react';
import { TerrixLogo } from './TerrixLogo';

interface SidebarProps {
  collapsed: boolean;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  activeTab,
  setActiveTab,
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
        <button className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
          <i className="bi bi-grid"></i><span className="nav-text">Dashboard</span>
        </button>

        <div className="nav-label">Telephony Control</div>
        <button className={`nav-item ${activeTab === 'extensions' ? 'active' : ''}`} onClick={() => setActiveTab('extensions')}>
          <i className="bi bi-telephone"></i><span className="nav-text">Extensions</span>
        </button>

        <button className={`nav-item ${activeTab === 'dids' ? 'active' : ''}`} onClick={() => setActiveTab('dids')}>
          <i className="bi bi-hash"></i><span className="nav-text">DID Inventory</span>
        </button>

        <button className={`nav-item ${activeTab === 'trunks' ? 'active' : ''}`} onClick={() => setActiveTab('trunks')}>
          <i className="bi bi-diagram-3"></i><span className="nav-text">SIP Trunks</span>
        </button>

        <button className={`nav-item ${activeTab === 'gateways' ? 'active' : ''}`} onClick={() => setActiveTab('gateways')}>
          <i className="bi bi-hdd-network"></i><span className="nav-text">Gateways</span>
        </button>

        <button className={`nav-item ${activeTab === 'routing' ? 'active' : ''}`} onClick={() => setActiveTab('routing')}>
          <i className="bi bi-sign-turn-right"></i><span className="nav-text">Call Routing</span>
        </button>

        <button className={`nav-item ${activeTab === 'queues' ? 'active' : ''}`} onClick={() => setActiveTab('queues')}>
          <i className="bi bi-people"></i><span className="nav-text">Call Queues</span>
        </button>

        <button className={`nav-item ${activeTab === 'ivr' ? 'active' : ''}`} onClick={() => setActiveTab('ivr')}>
          <i className="bi bi-diagram-2"></i><span className="nav-text">IVR Flow Designer</span>
        </button>

        <button className={`nav-item ${activeTab === 'huntgroups' ? 'active' : ''}`} onClick={() => setActiveTab('huntgroups')}>
          <i className="bi bi-telephone-forward"></i><span className="nav-text">Hunt Groups</span>
        </button>

        <div className="nav-label">Administration</div>
        <button className={`nav-item ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>
          <i className="bi bi-person-badge"></i><span className="nav-text">Users & Admins</span>
        </button>

        <button className={`nav-item ${activeTab === 'tenants' ? 'active' : ''}`} onClick={() => setActiveTab('tenants')}>
          <i className="bi bi-building"></i><span className="nav-text">Tenants</span>
        </button>

        <button className={`nav-item ${activeTab === 'auth' ? 'active' : ''}`} onClick={() => setActiveTab('auth')}>
          <i className="bi bi-shield-check"></i><span className="nav-text">Auth Controls</span>
        </button>
      </div>
    </aside>
  );
};
'''

with open(os.path.join(base_comp, "Sidebar.tsx"), "w", encoding="utf-8") as f:
    f.write(sidebar_tsx)


# 8. UPDATE APP.TSX
app_tsx = '''import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { LoginScreen } from './components/LoginScreen';
import { DashboardView } from './components/DashboardView';
import { AuthView } from './components/AuthView';
import { TenantsView } from './components/TenantsView';
import { ExtensionsView } from './components/ExtensionsView';
import { UsersView } from './components/UsersView';
import { TrunksView } from './components/TrunksView';
import { GatewaysView } from './components/GatewaysView';
import { RoutingView } from './components/RoutingView';
import { QueuesView } from './components/QueuesView';
import { DidsView } from './components/DidsView';
import { IvrView } from './components/IvrView';
import { HuntGroupsView } from './components/HuntGroupsView';
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

          {activeTab === 'auth' && <AuthView onLoginSuccess={handleLoginSuccess} user={user} />}
          {activeTab === 'tenants' && <TenantsView token={token} />}
          {activeTab === 'users' && <UsersView token={token} currentUser={user} />}
          {activeTab === 'extensions' && <ExtensionsView token={token} />}
          {activeTab === 'dids' && <DidsView token={token} />}
          {activeTab === 'trunks' && <TrunksView token={token} />}
          {activeTab === 'gateways' && <GatewaysView token={token} />}
          {activeTab === 'routing' && <RoutingView token={token} />}
          {activeTab === 'queues' && <QueuesView token={token} />}
          {activeTab === 'ivr' && <IvrView token={token} />}
          {activeTab === 'huntgroups' && <HuntGroupsView token={token} />}
        </div>
      </main>
    </div>
  );
};

export default App;
'''

with open(os.path.join(base_src, "App.tsx"), "w", encoding="utf-8") as f:
    f.write(app_tsx)

print("Frontend features successfully built.")
