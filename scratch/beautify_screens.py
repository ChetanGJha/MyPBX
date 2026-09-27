import os

base_comp = r"C:\PROJECTS\Fullstack PBX\frontend\src\components"

# 1. BEAUTIFIED TRUNKSVIEW.TSX
trunks_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Network, Plus, Search, Server, ShieldCheck, Activity, Trash2, CheckCircle2, XCircle } from 'lucide-react';

interface TrunksViewProps {
  token: string;
}

export const TrunksView: React.FC<TrunksViewProps> = ({ token }) => {
  const [trunks, setTrunks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
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

  const filtered = trunks.filter(t => 
    t.name.toLowerCase().includes(search.toLowerCase()) || 
    t.host.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Telephony Infrastructure</div>
          <h1 className="page-title">SIP Trunks</h1>
          <p className="page-sub">Configure carrier SIP trunk connections, proxies and gateway routes</p>
        </div>
        <div>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} /> Add SIP Trunk
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Total Trunks</span>
            <div style={{ background: '#FFF0EC', padding: '6px', borderRadius: '8px', color: 'var(--orange)' }}><Network size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{trunks.length}</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Registered</span>
            <div style={{ background: '#ECFDF5', padding: '6px', borderRadius: '8px', color: '#047857' }}><CheckCircle2 size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{trunks.filter(t => t.register).length}</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Active Channels</span>
            <div style={{ background: '#EFF6FF', padding: '6px', borderRadius: '8px', color: '#2563EB' }}><Activity size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{trunks.filter(t => t.enabled).length * 30}</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Security (SRTP)</span>
            <div style={{ background: '#F3E8FF', padding: '6px', borderRadius: '8px', color: '#9333EA' }}><ShieldCheck size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{trunks.filter(t => t.srtp).length} Enabled</div>
        </div>
      </div>

      {error && <div className="alert alert-danger mb-4">{error}</div>}

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
            <input 
              className="form-control"
              style={{ paddingLeft: '36px', height: '38px', fontSize: '12px' }}
              placeholder="Search SIP trunks by name or host..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Trunk Name</th>
                <th>SIP Host / Proxy</th>
                <th>Port</th>
                <th>Transport</th>
                <th>Auth Username</th>
                <th>Priority</th>
                <th>Registration</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="text-center py-4">Loading SIP trunks...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-4 text-muted">No SIP trunks match your search</td></tr>
              ) : (
                filtered.map((t) => (
                  <tr key={t.id}>
                    <td>
                      <div style={{ fontWeight: 700, color: '#111827' }}>{t.name}</div>
                    </td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{t.host}</code></td>
                    <td>{t.port}</td>
                    <td><span className="terrix-badge grey">{t.transport}</span></td>
                    <td>{t.username || <span style={{ color: '#9CA3AF' }}>IP Auth</span>}</td>
                    <td><span style={{ fontWeight: 700 }}>P{t.priority}</span></td>
                    <td>
                      {t.register ? (
                        <span className="terrix-badge green"><CheckCircle2 size={10} style={{ marginRight: '4px' }} /> REGISTERED</span>
                      ) : (
                        <span className="terrix-badge grey">STATIC IP</span>
                      )}
                    </td>
                    <td>
                      {t.enabled ? (
                        <span className="terrix-badge green">ACTIVE</span>
                      ) : (
                        <span className="terrix-badge orange">DISABLED</span>
                      )}
                    </td>
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
              <div className="modal-icon"><Server size={20} /></div>
              <div>
                <h3>Create New SIP Trunk</h3>
                <p>Configure carrier proxy settings, port & auth credentials</p>
              </div>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="form-group">
                    <label className="form-label">Trunk Name</label>
                    <input required className="form-control" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Twilio Primary Gateway" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">SIP Host / Proxy</label>
                    <input required className="form-control" value={formData.host} onChange={e => setFormData({...formData, host: e.target.value})} placeholder="e.g. sip.twilio.com" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">SIP Port</label>
                    <input type="number" className="form-control" value={formData.port} onChange={e => setFormData({...formData, port: parseInt(e.target.value) || 5060})} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Transport Protocol</label>
                    <select className="form-control" value={formData.transport} onChange={e => setFormData({...formData, transport: e.target.value})}>
                      <option value="UDP">UDP (Standard)</option>
                      <option value="TCP">TCP</option>
                      <option value="TLS">TLS (Encrypted)</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Auth Username</label>
                    <input className="form-control" value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} placeholder="Optional for IP authentication" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Auth Password</label>
                    <input type="password" className="form-control" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} placeholder="Optional" />
                  </div>
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Trunk</button>
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

# 2. BEAUTIFIED GATEWAYSVIEW.TSX
gateways_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Cpu, Plus, Link, CheckCircle2, Server, Layers, ShieldCheck } from 'lucide-react';

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
      alert('Gateway assigned to tenant successfully!');
      loadData();
    } catch (err: any) {
      alert(err.message || 'Assignment failed');
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">FreeSWITCH Sofia Core</div>
          <h1 className="page-title">Sofia Gateways & Assignments</h1>
          <p className="page-sub">Assign gateway channels and specify inbound/outbound priority rules per tenant</p>
        </div>
        <div>
          <button className="btn-primary" onClick={() => setShowAssignModal(true)}>
            <Link size={16} /> Assign Gateway to Tenant
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Sofia Gateways</span>
            <div style={{ background: '#FFF0EC', padding: '6px', borderRadius: '8px', color: 'var(--orange)' }}><Cpu size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{gateways.length}</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Registered Engine</span>
            <div style={{ background: '#ECFDF5', padding: '6px', borderRadius: '8px', color: '#047857' }}><CheckCircle2 size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{gateways.filter(g => g.register).length}</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Tenant Mappings</span>
            <div style={{ background: '#EFF6FF', padding: '6px', borderRadius: '8px', color: '#2563EB' }}><Layers size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{tenants.length} Tenants</div>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Gateway Name</th>
                <th>SIP Proxy</th>
                <th>Assigned Tenant</th>
                <th>Supported Codecs</th>
                <th>Registration</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="text-center py-4">Loading Sofia Gateways...</td></tr>
              ) : gateways.length === 0 ? (
                <tr><td colSpan={6} className="text-center py-4 text-muted">No gateways configured in FreeSWITCH</td></tr>
              ) : (
                gateways.map((g) => (
                  <tr key={g.id}>
                    <td><div style={{ fontWeight: 700, color: '#111827' }}>{g.name}</div></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{g.proxy}</code></td>
                    <td>
                      {g.tenant_name ? (
                        <span className="terrix-badge orange">{g.tenant_name}</span>
                      ) : (
                        <span className="terrix-badge grey">GLOBAL GATEWAY</span>
                      )}
                    </td>
                    <td>{g.codecs}</td>
                    <td>
                      {g.register ? (
                        <span className="terrix-badge green">REGISTERED</span>
                      ) : (
                        <span className="terrix-badge grey">INBOUND ONLY</span>
                      )}
                    </td>
                    <td><span className="terrix-badge green">ONLINE</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showAssignModal && (
        <div className="modal-backdrop">
          <div className="terrix-modal">
            <div className="modal-head">
              <div className="modal-icon"><Link size={20} /></div>
              <div>
                <h3>Assign Gateway to Tenant</h3>
                <p>Set call direction, caller ID policies and priority bounds</p>
              </div>
              <button className="modal-close" onClick={() => setShowAssignModal(false)}>×</button>
            </div>
            <form onSubmit={handleAssign}>
              <div className="modal-body">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="form-group">
                    <label className="form-label">Target Tenant</label>
                    <select required className="form-control" value={assignForm.tenant_id} onChange={e => setAssignForm({...assignForm, tenant_id: e.target.value})}>
                      <option value="">-- Select Tenant --</option>
                      {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Sofia Gateway</label>
                    <select required className="form-control" value={assignForm.gateway_id} onChange={e => setAssignForm({...assignForm, gateway_id: e.target.value})}>
                      <option value="">-- Select Gateway --</option>
                      {gateways.map(g => <option key={g.id} value={g.id}>{g.name} ({g.proxy})</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Call Direction</label>
                    <select className="form-control" value={assignForm.direction} onChange={e => setAssignForm({...assignForm, direction: e.target.value})}>
                      <option value="inbound_outbound">Inbound & Outbound</option>
                      <option value="inbound_only">Inbound Only</option>
                      <option value="outbound_only">Outbound Only</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Priority Level (1 = Highest)</label>
                    <input type="number" className="form-control" value={assignForm.priority} onChange={e => setAssignForm({...assignForm, priority: parseInt(e.target.value) || 1})} />
                  </div>
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowAssignModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Assignment</button>
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

# 3. BEAUTIFIED ROUTINGVIEW.TSX
routing_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Route, Plus, Search, ArrowUpRight, ArrowDownLeft, PhoneCall } from 'lucide-react';

interface RoutingViewProps {
  token: string;
}

export const RoutingView: React.FC<RoutingViewProps> = ({ token }) => {
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

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

  const filtered = routes.filter(r => 
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    (r.did_number && r.did_number.includes(search))
  );

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Dialplan Engine</div>
          <h1 className="page-title">Call Routing & DIDs</h1>
          <p className="page-sub">Manage inbound DID number routing and outbound pattern matching rules</p>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Inbound DIDs</span>
            <div style={{ background: '#ECFDF5', padding: '6px', borderRadius: '8px', color: '#047857' }}><ArrowDownLeft size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{routes.filter(r => r.route_type === 'inbound_did').length}</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Outbound Rules</span>
            <div style={{ background: '#FFF0EC', padding: '6px', borderRadius: '8px', color: 'var(--orange)' }}><ArrowUpRight size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{routes.filter(r => r.route_type === 'outbound').length}</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Total Active Routes</span>
            <div style={{ background: '#EFF6FF', padding: '6px', borderRadius: '8px', color: '#2563EB' }}><PhoneCall size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{routes.length}</div>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
            <input 
              className="form-control"
              style={{ paddingLeft: '36px', height: '38px', fontSize: '12px' }}
              placeholder="Search routes by name or DID number..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Route Name</th>
                <th>DID / Pattern</th>
                <th>Route Type</th>
                <th>Destination Type</th>
                <th>Target Destination</th>
                <th>Priority</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="text-center py-4">Loading call routes...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-4 text-muted">No routing rules match your search</td></tr>
              ) : (
                filtered.map((r) => (
                  <tr key={r.id}>
                    <td><div style={{ fontWeight: 700, color: '#111827' }}>{r.name}</div></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{r.did_number || r.regex_pattern || '*'}</code></td>
                    <td>
                      {r.route_type === 'inbound_did' ? (
                        <span className="terrix-badge green">INBOUND</span>
                      ) : (
                        <span className="terrix-badge orange">OUTBOUND</span>
                      )}
                    </td>
                    <td><span className="terrix-badge grey">{r.destination_type.toUpperCase()}</span></td>
                    <td><strong style={{ color: '#111827' }}>{r.destination}</strong></td>
                    <td><span style={{ fontWeight: 700 }}>P{r.priority}</span></td>
                    <td><span className="terrix-badge green">ENABLED</span></td>
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

# 4. BEAUTIFIED QUEUESVIEW.TSX
queues_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Users, Clock, PhoneIncoming, Headphones, CheckCircle2 } from 'lucide-react';

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
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">ACR Queue Engine</div>
          <h1 className="page-title">Call Queues</h1>
          <p className="page-sub">FreeSWITCH mod_callcenter agent queues, distribution strategies and wait timers</p>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Active Queues</span>
            <div style={{ background: '#FFF0EC', padding: '6px', borderRadius: '8px', color: 'var(--orange)' }}><Users size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>{queues.length}</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Active Agents</span>
            <div style={{ background: '#ECFDF5', padding: '6px', borderRadius: '8px', color: '#047857' }}><Headphones size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>8 Ready</div>
        </div>

        <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Avg Wait Time</span>
            <div style={{ background: '#EFF6FF', padding: '6px', borderRadius: '8px', color: '#2563EB' }}><Clock size={18} /></div>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#111827' }}>12s</div>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Queue Name</th>
                <th>Extension</th>
                <th>Distribution Strategy</th>
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
                    <td><div style={{ fontWeight: 700, color: '#111827' }}>{q.name}</div></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{q.queue_number}</code></td>
                    <td><span className="terrix-badge grey">{q.strategy.toUpperCase()}</span></td>
                    <td>{q.agent_timeout}s</td>
                    <td>{q.max_wait_time}s</td>
                    <td>{q.agents || 'All Extensions'}</td>
                    <td><span className="terrix-badge green">ACTIVE</span></td>
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

print("Beautified views created successfully.")
