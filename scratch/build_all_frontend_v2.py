import os

base_comp = r"C:\PROJECTS\Fullstack PBX\frontend\src\components"
base_src = r"C:\PROJECTS\Fullstack PBX\frontend\src"

# 1. REPORTSVIEW.TSX (Requirement 8: Date Range Filters & Reports)
reports_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { FileText, Calendar, Filter, PhoneIncoming, PhoneOutgoing, PhoneCall, Disc, Volume2 } from 'lucide-react';

interface ReportsViewProps {
  token: string;
}

export const ReportsView: React.FC<ReportsViewProps> = ({ token }) => {
  const [activeTab, setActiveTab] = useState<'cdr' | 'internal' | 'outbound' | 'recordings'>('cdr');
  const [tenants, setTenants] = useState<any[]>([]);
  const [selectedTenant, setSelectedTenant] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState<any[]>([]);

  const loadTenants = async () => {
    try {
      const data = await apiService.getTenants(token);
      setTenants(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadTenants();
  }, [token]);

  const loadReport = async () => {
    try {
      setLoading(true);
      if (activeTab === 'cdr') {
        const data = await apiService.getCdrReport(token, selectedTenant, startDate, endDate);
        setReportData(data);
      } else if (activeTab === 'internal') {
        const data = await apiService.getInternalReport(token, selectedTenant, startDate, endDate);
        setReportData(data);
      } else if (activeTab === 'outbound') {
        const data = await apiService.getOutboundReport(token, selectedTenant, startDate, endDate);
        setReportData(data);
      } else if (activeTab === 'recordings') {
        const data = await apiService.getRecordingsReport(token, selectedTenant);
        setReportData(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
  }, [token, activeTab, selectedTenant, startDate, endDate]);

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Analytics & Telemetry</div>
          <h1 className="page-title">Reports & Call Detail Records</h1>
          <p className="page-sub">Tenant-wise call logs, extension-to-extension summary, outbound analytics & voice recordings</p>
        </div>
      </div>

      {/* FILTER TOOLBAR */}
      <div style={{ background: '#FFFFFF', padding: '18px 20px', borderRadius: '12px', border: '1px solid var(--border)', marginBottom: '20px', display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={16} style={{ color: '#9CA3AF' }} />
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>Tenant Filter:</span>
          <select className="form-control" style={{ height: '36px', fontSize: '12px', minWidth: '180px' }} value={selectedTenant} onChange={e => setSelectedTenant(e.target.value)}>
            <option value="">-- All Tenants --</option>
            {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Calendar size={16} style={{ color: '#9CA3AF' }} />
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>From:</span>
          <input type="date" className="form-control" style={{ height: '36px', fontSize: '12px' }} value={startDate} onChange={e => setStartDate(e.target.value)} />
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#6B7280', textTransform: 'uppercase' }}>To:</span>
          <input type="date" className="form-control" style={{ height: '36px', fontSize: '12px' }} value={endDate} onChange={e => setEndDate(e.target.value)} />
        </div>

        <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '11px' }} onClick={() => { setSelectedTenant(''); setStartDate(''); setEndDate(''); }}>
          Reset Filters
        </button>
      </div>

      {/* REPORT TYPE TABS */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <button className={`btn-secondary ${activeTab === 'cdr' ? 'bg-[#FFF0EC] text-[#FF5430] font-bold border-[#FF5430]' : ''}`} onClick={() => setActiveTab('cdr')}>
          <FileText size={14} style={{ marginRight: '6px' }} /> Call Detail Records (CDR)
        </button>
        <button className={`btn-secondary ${activeTab === 'internal' ? 'bg-[#FFF0EC] text-[#FF5430] font-bold border-[#FF5430]' : ''}`} onClick={() => setActiveTab('internal')}>
          <PhoneCall size={14} style={{ marginRight: '6px' }} /> Internal Calls Summary
        </button>
        <button className={`btn-secondary ${activeTab === 'outbound' ? 'bg-[#FFF0EC] text-[#FF5430] font-bold border-[#FF5430]' : ''}`} onClick={() => setActiveTab('outbound')}>
          <PhoneOutgoing size={14} style={{ marginRight: '6px' }} /> Outbound Calls Analytics
        </button>
        <button className={`btn-secondary ${activeTab === 'recordings' ? 'bg-[#FFF0EC] text-[#FF5430] font-bold border-[#FF5430]' : ''}`} onClick={() => setActiveTab('recordings')}>
          <Disc size={14} style={{ marginRight: '6px' }} /> Voice Recordings
        </button>
      </div>

      {/* DATA TABLE */}
      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div className="data-table-wrap">
          {activeTab === 'cdr' && (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Start Time</th>
                  <th>Caller ID / Number</th>
                  <th>Destination Number</th>
                  <th>Direction</th>
                  <th>Duration</th>
                  <th>Bill Sec</th>
                  <th>Tenant</th>
                  <th>Hangup Cause</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={8} className="text-center py-4">Loading CDR records...</td></tr>
                ) : reportData.length === 0 ? (
                  <tr><td colSpan={8} className="text-center py-4 text-muted">No call detail records found for selected filters</td></tr>
                ) : (
                  reportData.map(r => (
                    <tr key={r.id}>
                      <td>{r.start_stamp}</td>
                      <td><strong>{r.caller_id_number}</strong> ({r.caller_id_name || 'N/A'})</td>
                      <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{r.destination_number}</code></td>
                      <td><span className="terrix-badge grey">{r.direction || 'inbound'}</span></td>
                      <td>{r.duration}s</td>
                      <td>{r.billsec}s</td>
                      <td><span className="terrix-badge orange">{r.tenant_name || 'Global'}</span></td>
                      <td><span className="terrix-badge green">{r.hangup_cause || 'NORMAL_CLEARING'}</span></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}

          {activeTab === 'internal' && (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Source Extension</th>
                  <th>Target Extension</th>
                  <th>Total Calls</th>
                  <th>Total Duration (Sec)</th>
                  <th>Avg Duration (Sec)</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={5} className="text-center py-4">Loading internal call report...</td></tr>
                ) : reportData.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-4 text-muted">No internal call records found</td></tr>
                ) : (
                  reportData.map((r, i) => (
                    <tr key={i}>
                      <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{r.caller_id_number}</code></td>
                      <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{r.destination_number}</code></td>
                      <td><strong>{r.total_calls}</strong></td>
                      <td>{r.total_duration_sec}s</td>
                      <td>{r.avg_duration_sec}s</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}

          {activeTab === 'outbound' && (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Start Time</th>
                  <th>Originating Extension</th>
                  <th>Outbound Destination</th>
                  <th>Billable Sec</th>
                  <th>Tenant</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={5} className="text-center py-4">Loading outbound call report...</td></tr>
                ) : reportData.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-4 text-muted">No outbound call records found</td></tr>
                ) : (
                  reportData.map((r, i) => (
                    <tr key={i}>
                      <td>{r.start_stamp}</td>
                      <td><strong>{r.caller_id_number}</strong></td>
                      <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{r.destination_number}</code></td>
                      <td>{r.billsec}s</td>
                      <td><span className="terrix-badge orange">{r.tenant_name || 'Global'}</span></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}

          {activeTab === 'recordings' && (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Recorded At</th>
                  <th>File Name</th>
                  <th>File Size</th>
                  <th>Tenant</th>
                  <th>Audio Playback</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={5} className="text-center py-4">Loading voice recordings...</td></tr>
                ) : reportData.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-4 text-muted">No voice recordings found</td></tr>
                ) : (
                  reportData.map(r => (
                    <tr key={r.id}>
                      <td>{r.created_at}</td>
                      <td><strong>{r.file_name}</strong></td>
                      <td>{(r.file_size / 1024).toFixed(1)} KB</td>
                      <td><span className="terrix-badge orange">{r.tenant_name || 'Global'}</span></td>
                      <td>
                        <button className="btn-secondary" style={{ padding: '4px 8px', fontSize: '11px' }} onClick={() => alert(`Playing ${r.file_name}`)}>
                          <Volume2 size={13} style={{ marginRight: '4px' }} /> Play Recording
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
'''

with open(os.path.join(base_comp, "ReportsView.tsx"), "w", encoding="utf-8") as f:
    f.write(reports_view)


# 2. AUDIOVIEW.TSX (Requirement 7: Voice Files Management)
audio_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Mic, Upload, Volume2 } from 'lucide-react';

interface AudioViewProps {
  token: string;
}

export const AudioView: React.FC<AudioViewProps> = ({ token }) => {
  const [audioFiles, setAudioFiles] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [category, setCategory] = useState('ivr_greeting');
  const [tenantId, setTenantId] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [aData, tData] = await Promise.allSettled([
        apiService.getAudioFiles(token),
        apiService.getTenants(token)
      ]);
      if (aData.status === 'fulfilled') setAudioFiles(aData.value);
      if (tData.status === 'fulfilled') setTenants(tData.value);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      alert('Please select an audio file to upload');
      return;
    }
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('category', category);
    if (tenantId) formData.append('tenant_id', tenantId);

    try {
      await apiService.uploadAudioFile(token, formData);
      setShowModal(false);
      setSelectedFile(null);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to upload audio file');
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Audio Asset Library</div>
          <h1 className="page-title">Voice Prompts & Greetings</h1>
          <p className="page-sub">Upload custom WAV/MP3 audio prompts for IVRs, greetings and music-on-hold</p>
        </div>
        <div>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <Upload size={16} /> Upload Audio Prompt
          </button>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Audio File Name</th>
                <th>Category</th>
                <th>File Path</th>
                <th>Uploaded At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="text-center py-4">Loading audio files...</td></tr>
              ) : audioFiles.length === 0 ? (
                <tr><td colSpan={5} className="text-center py-4 text-muted">No custom audio prompts uploaded</td></tr>
              ) : (
                audioFiles.map(a => (
                  <tr key={a.id}>
                    <td><strong style={{ color: '#111827' }}>{a.file_name}</strong></td>
                    <td><span className="terrix-badge grey">{a.category.toUpperCase()}</span></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{a.file_path}</code></td>
                    <td>{a.created_at}</td>
                    <td>
                      <button className="btn-secondary" style={{ padding: '4px 8px', fontSize: '11px' }} onClick={() => alert(`Playing ${a.file_name}`)}>
                        <Volume2 size={13} style={{ marginRight: '4px' }} /> Test Audio
                      </button>
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
              <div className="modal-icon"><Mic size={20} /></div>
              <div>
                <h3>Upload Voice Prompt</h3>
                <p>Select a WAV or MP3 audio recording file</p>
              </div>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleUpload}>
              <div className="modal-body">
                <div className="form-group mb-3">
                  <label className="form-label">Target Tenant (Optional)</label>
                  <select className="form-control" value={tenantId} onChange={e => setTenantId(e.target.value)}>
                    <option value="">-- Global / Select Tenant --</option>
                    {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                  </select>
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Category</label>
                  <select className="form-control" value={category} onChange={e => setCategory(e.target.value)}>
                    <option value="ivr_greeting">IVR Welcome Prompt</option>
                    <option value="voicemail_greeting">Voicemail Greeting</option>
                    <option value="music_on_hold">Music On Hold</option>
                  </select>
                </div>
                <div className="form-group mb-3">
                  <label className="form-label">Audio File (.wav / .mp3)</label>
                  <input required type="file" accept="audio/*" className="form-control" onChange={e => setSelectedFile(e.target.files ? e.target.files[0] : null)} />
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Upload Audio</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "AudioView.tsx"), "w", encoding="utf-8") as f:
    f.write(audio_view)

# 3. ROUTINGVIEW.TSX (Requirement 4: Dynamic Call Routing CRUD)
routing_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Route as RouteIcon, Plus, Search, ArrowUpRight, ArrowDownLeft, PhoneCall, Trash2 } from 'lucide-react';

interface RoutingViewProps {
  token: string;
}

export const RoutingView: React.FC<RoutingViewProps> = ({ token }) => {
  const [routes, setRoutes] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [trunks, setTrunks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    did_number: '',
    route_type: 'inbound_did',
    destination_type: 'queue',
    destination: '7001',
    priority: 1,
    gateway_id: '',
    tenant_id: ''
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [rData, tData, sData] = await Promise.allSettled([
        apiService.getRoutes(token),
        apiService.getTenants(token),
        apiService.getTrunks(token)
      ]);
      if (rData.status === 'fulfilled') setRoutes(rData.value);
      if (tData.status === 'fulfilled') setTenants(tData.value);
      if (sData.status === 'fulfilled') setTrunks(sData.value);
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
      const payload: any = { ...formData };
      if (!payload.gateway_id) delete payload.gateway_id;
      if (!payload.tenant_id) delete payload.tenant_id;
      await apiService.createRoute(token, payload);
      setShowModal(false);
      setFormData({ name: '', did_number: '', route_type: 'inbound_did', destination_type: 'queue', destination: '7001', priority: 1, gateway_id: '', tenant_id: '' });
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to create route');
    }
  };

  const handleDelete = async (routeId: string) => {
    if (!window.confirm('Are you sure you want to delete this routing rule?')) return;
    try {
      await apiService.deleteRoute(token, routeId);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to delete route');
    }
  };

  const filtered = routes.filter(r =>
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    (r.did_number && r.did_number.includes(search))
  );

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">Dialplan Engine</div>
          <h1 className="page-title">Call Routing Rules</h1>
          <p className="page-sub">Configure tenant-wise inbound DID routing and outbound pattern matching linked with mod_xml_curl</p>
        </div>
        <div>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} /> Add Routing Rule
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
              placeholder="Search routes..."
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
                <th>Type</th>
                <th>Destination Type</th>
                <th>Target Destination</th>
                <th>Priority</th>
                <th>Tenant</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="text-center py-4">Loading call routes...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-4 text-muted">No routing rules match your search</td></tr>
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
                    <td><span className="terrix-badge orange">{r.tenant_name || 'Global'}</span></td>
                    <td className="text-right">
                      <button className="btn-secondary text-rose-600" style={{ padding: '4px 8px', fontSize: '11px' }} onClick={() => handleDelete(r.id)}>
                        <Trash2 size={13} />
                      </button>
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
              <div className="modal-icon"><RouteIcon size={20} /></div>
              <div>
                <h3>Create Routing Rule</h3>
                <p>Add tenant-wise inbound DID or outbound dialplan rule</p>
              </div>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="form-group">
                    <label className="form-label">Route Name</label>
                    <input required className="form-control" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Sales DID Route" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Target Tenant (Optional)</label>
                    <select className="form-control" value={formData.tenant_id} onChange={e => setFormData({...formData, tenant_id: e.target.value})}>
                      <option value="">-- Global / Select Tenant --</option>
                      {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Route Type</label>
                    <select className="form-control" value={formData.route_type} onChange={e => setFormData({...formData, route_type: e.target.value})}>
                      <option value="inbound_did">Inbound DID Route</option>
                      <option value="outbound">Outbound Dialplan Rule</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">DID Number / Regex Pattern</label>
                    <input className="form-control" value={formData.did_number} onChange={e => setFormData({...formData, did_number: e.target.value})} placeholder="e.g. +18005550199" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Destination Type</label>
                    <select className="form-control" value={formData.destination_type} onChange={e => setFormData({...formData, destination_type: e.target.value})}>
                      <option value="queue">Call Queue</option>
                      <option value="extension">Extension</option>
                      <option value="ivr">IVR Menu Flow</option>
                      <option value="voicemail">Voicemail Box</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Destination Target</label>
                    <input required className="form-control" value={formData.destination} onChange={e => setFormData({...formData, destination: e.target.value})} placeholder="e.g. 7001 or 1001" />
                  </div>
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Routing Rule</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "RoutingView.tsx"), "w", encoding="utf-8") as f:
    f.write(routing_view)


# 4. QUEUESVIEW.TSX (Requirement 5: Super Admin Queues Edit/Modify)
queues_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Users, Plus, Edit2, Trash2 } from 'lucide-react';

interface QueuesViewProps {
  token: string;
}

export const QueuesView: React.FC<QueuesViewProps> = ({ token }) => {
  const [queues, setQueues] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [editingQueue, setEditingQueue] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    queue_number: '',
    strategy: 'round_robin',
    agent_timeout: 30,
    wrap_up_time: 10,
    max_wait_time: 300,
    agents: '1001, 1002',
    tenant_id: ''
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [qData, tData] = await Promise.allSettled([
        apiService.getQueues(token),
        apiService.getTenants(token)
      ]);
      if (qData.status === 'fulfilled') setQueues(qData.value);
      if (tData.status === 'fulfilled') setTenants(tData.value);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const handleOpenCreate = () => {
    setEditingQueue(null);
    setFormData({ name: '', queue_number: '', strategy: 'round_robin', agent_timeout: 30, wrap_up_time: 10, max_wait_time: 300, agents: '1001, 1002', tenant_id: '' });
    setShowModal(true);
  };

  const handleOpenEdit = (q: any) => {
    setEditingQueue(q);
    setFormData({
      name: q.name,
      queue_number: q.queue_number,
      strategy: q.strategy,
      agent_timeout: q.agent_timeout,
      wrap_up_time: q.wrap_up_time || 10,
      max_wait_time: q.max_wait_time || 300,
      agents: q.agents || '',
      tenant_id: q.tenant_id || ''
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = { ...formData };
      if (!payload.tenant_id) delete payload.tenant_id;

      if (editingQueue) {
        await apiService.updateQueue(token, editingQueue.id, payload);
      } else {
        await apiService.createQueue(token, payload);
      }
      setShowModal(false);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to save call queue');
    }
  };

  const handleDelete = async (queueId: string) => {
    if (!window.confirm('Are you sure you want to delete this queue?')) return;
    try {
      await apiService.deleteQueue(token, queueId);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to delete queue');
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">ACR Queue Engine</div>
          <h1 className="page-title">Call Queues</h1>
          <p className="page-sub">FreeSWITCH mod_callcenter agent queues, distribution strategies and wait timers</p>
        </div>
        <div>
          <button className="btn-primary" onClick={handleOpenCreate}>
            <Plus size={16} /> Create Call Queue
          </button>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Queue Name</th>
                <th>Extension</th>
                <th>Strategy</th>
                <th>Agent Timeout</th>
                <th>Max Wait Time</th>
                <th>Agents</th>
                <th>Tenant</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="text-center py-4">Loading call queues...</td></tr>
              ) : queues.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-4 text-muted">No call queues configured</td></tr>
              ) : (
                queues.map((q) => (
                  <tr key={q.id}>
                    <td><div style={{ fontWeight: 700, color: '#111827' }}>{q.name}</div></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{q.queue_number}</code></td>
                    <td><span className="terrix-badge grey">{q.strategy.toUpperCase()}</span></td>
                    <td>{q.agent_timeout}s</td>
                    <td>{q.max_wait_time}s</td>
                    <td>{q.agents || 'All Extensions'}</td>
                    <td><span className="terrix-badge orange">{q.tenant_name || 'Global'}</span></td>
                    <td className="text-right">
                      <button className="btn-secondary text-amber-600" style={{ padding: '4px 8px', fontSize: '11px', marginRight: '6px' }} onClick={() => handleOpenEdit(q)}>
                        <Edit2 size={13} style={{ marginRight: '4px' }} /> Edit
                      </button>
                      <button className="btn-secondary text-rose-600" style={{ padding: '4px 8px', fontSize: '11px' }} onClick={() => handleDelete(q.id)}>
                        <Trash2 size={13} />
                      </button>
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
              <div className="modal-icon"><Users size={20} /></div>
              <div>
                <h3>{editingQueue ? 'Edit Call Queue' : 'Create Call Queue'}</h3>
                <p>Configure mod_callcenter agent distribution strategy</p>
              </div>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="form-group">
                    <label className="form-label">Queue Name</label>
                    <input required className="form-control" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Support Escalations" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Virtual Extension Number</label>
                    <input required className="form-control" value={formData.queue_number} onChange={e => setFormData({...formData, queue_number: e.target.value})} placeholder="e.g. 7001" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Target Tenant (Optional)</label>
                    <select className="form-control" value={formData.tenant_id} onChange={e => setFormData({...formData, tenant_id: e.target.value})}>
                      <option value="">-- Global / Select Tenant --</option>
                      {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Distribution Strategy</label>
                    <select className="form-control" value={formData.strategy} onChange={e => setFormData({...formData, strategy: e.target.value})}>
                      <option value="round_robin">Round Robin</option>
                      <option value="longest_idle_agent">Longest Idle Agent</option>
                      <option value="ring_all">Ring All Agents</option>
                      <option value="top_down">Top Down Priority</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Agent Timeout (seconds)</label>
                    <input type="number" className="form-control" value={formData.agent_timeout} onChange={e => setFormData({...formData, agent_timeout: parseInt(e.target.value) || 30})} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Max Queue Wait Time (seconds)</label>
                    <input type="number" className="form-control" value={formData.max_wait_time} onChange={e => setFormData({...formData, max_wait_time: parseInt(e.target.value) || 300})} />
                  </div>
                  <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                    <label className="form-label">Assigned Member Extensions (Comma separated)</label>
                    <input className="form-control" value={formData.agents} onChange={e => setFormData({...formData, agents: e.target.value})} placeholder="e.g. 1001, 1002, 1003" />
                  </div>
                </div>
              </div>
              <div className="modal-foot">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Call Queue</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
'''

with open(os.path.join(base_comp, "QueuesView.tsx"), "w", encoding="utf-8") as f:
    f.write(queues_view)


# 5. GATEWAYSVIEW.TSX (Requirement 3: Show SIP Trunk Name)
gateways_view = '''import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Cpu, Link, CheckCircle2, Layers } from 'lucide-react';

interface GatewaysViewProps {
  token: string;
}

export const GatewaysView: React.FC<GatewaysViewProps> = ({ token }) => {
  const [gateways, setGateways] = useState<any[]>([]);
  const [trunks, setTrunks] = useState<any[]>([]);
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
      const [gData, tData, sData] = await Promise.allSettled([
        apiService.getGateways(token),
        apiService.getTenants(token),
        apiService.getTrunks(token)
      ]);
      if (gData.status === 'fulfilled') setGateways(gData.value);
      if (tData.status === 'fulfilled') setTenants(tData.value);
      if (sData.status === 'fulfilled') setTrunks(sData.value);
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
      alert('SIP Trunk / Gateway assigned to tenant successfully!');
      loadData();
    } catch (err: any) {
      alert(err.message || 'Assignment failed');
    }
  };

  // Combine Sofia Gateways and Carrier SIP Trunks into unified selector list
  const availableTrunksAndGateways = [
    ...trunks.map(t => ({ id: t.id, name: `${t.name} (${t.host}) [SIP Trunk]` })),
    ...gateways.map(g => ({ id: g.id, name: `${g.name} (${g.proxy}) [Sofia Gateway]` }))
  ];

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">FreeSWITCH Sofia Core</div>
          <h1 className="page-title">SIP Trunks & Gateway Assignments</h1>
          <p className="page-sub">Assign carrier SIP trunks to tenants and specify inbound/outbound priority rules</p>
        </div>
        <div>
          <button className="btn-primary" onClick={() => setShowAssignModal(true)}>
            <Link size={16} /> Assign SIP Trunk to Tenant
          </button>
        </div>
      </div>

      <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid var(--border)', overflow: 'hidden' }}>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Gateway / Trunk Name</th>
                <th>SIP Proxy / Host</th>
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
                <tr><td colSpan={6} className="text-center py-4 text-muted">No gateways configured</td></tr>
              ) : (
                gateways.map((g) => (
                  <tr key={g.id}>
                    <td><div style={{ fontWeight: 700, color: '#111827' }}>{g.name}</div></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{g.proxy}</code></td>
                    <td>
                      {g.tenant_name ? (
                        <span className="terrix-badge orange">{g.tenant_name}</span>
                      ) : (
                        <span className="terrix-badge grey">GLOBAL TRUNK</span>
                      )}
                    </td>
                    <td>{g.codecs}</td>
                    <td>
                      {g.register ? (
                        <span className="terrix-badge green">REGISTERED</span>
                      ) : (
                        <span className="terrix-badge grey">STATIC IP</span>
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
                <h3>Assign SIP Trunk / Gateway to Tenant</h3>
                <p>Select provider SIP Trunk and configure tenant routing bounds</p>
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

                  {/* Requirement 3: Shows SIP Trunk Name from SIP Trunks Section */}
                  <div className="form-group">
                    <label className="form-label">SIP Trunk Provider / Gateway</label>
                    <select required className="form-control" value={assignForm.gateway_id} onChange={e => setAssignForm({...assignForm, gateway_id: e.target.value})}>
                      <option value="">-- Select SIP Trunk Provider --</option>
                      {availableTrunksAndGateways.map(item => (
                        <option key={item.id} value={item.id}>{item.name}</option>
                      ))}
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


# 6. UPDATE SERVICES/API.TS WITH REPORTS & AUDIO ENDPOINTS
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
      return { healthy: false, ready: false, database: 'disconnected', redis: 'disconnected' };
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
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Invalid token');
    return res.json() as Promise<User>;
  },

  // Tenants
  async getTenants(token: string): Promise<Tenant[]> {
    const res = await fetch(`${API_BASE_URL}/api/v1/tenants`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch tenants');
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
    if (!res.ok) throw new Error('Failed to update status');
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
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch extensions');
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

  async resetExtensionPassword(token: string, extensionId: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/reset-password`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to reset password');
    return res.json();
  },

  async updateExtensionSettings(token: string, extensionId: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/settings`, {
      method: 'PUT',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  // DIDs
  async getDids(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/dids`, { headers: getHeaders(token) });
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
    if (!res.ok) throw new Error('Failed to assign DID');
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

  // Routing Rules CRUD
  async getRoutes(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/routing`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch routes');
    return res.json();
  },

  async createRoute(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/routing`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create route');
    }
    return res.json();
  },

  async deleteRoute(token: string, routeId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/routing/${routeId}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to delete route');
  },

  // Queues CRUD
  async getQueues(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/queues`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch queues');
    return res.json();
  },

  async createQueue(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/queues`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create queue');
    }
    return res.json();
  },

  async updateQueue(token: string, queueId: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/queues/${queueId}`, {
      method: 'PUT',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update queue');
    return res.json();
  },

  async deleteQueue(token: string, queueId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/queues/${queueId}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to delete queue');
  },

  // Reports Endpoints
  async getCdrReport(token: string, tenantId?: string, startDate?: string, endDate?: string) {
    let url = `${API_BASE_URL}/api/v1/reports/cdr?call_type=all`;
    if (tenantId) url += `&tenant_id=${tenantId}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    const res = await fetch(url, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch CDR report');
    return res.json();
  },

  async getInternalReport(token: string, tenantId?: string, startDate?: string, endDate?: string) {
    let url = `${API_BASE_URL}/api/v1/reports/internal?`;
    if (tenantId) url += `&tenant_id=${tenantId}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    const res = await fetch(url, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch internal report');
    return res.json();
  },

  async getOutboundReport(token: string, tenantId?: string, startDate?: string, endDate?: string) {
    let url = `${API_BASE_URL}/api/v1/reports/outbound?`;
    if (tenantId) url += `&tenant_id=${tenantId}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    const res = await fetch(url, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch outbound report');
    return res.json();
  },

  async getRecordingsReport(token: string, tenantId?: string) {
    let url = `${API_BASE_URL}/api/v1/reports/recordings?`;
    if (tenantId) url += `&tenant_id=${tenantId}`;
    const res = await fetch(url, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch recordings');
    return res.json();
  },

  // Audio Files Endpoints
  async getAudioFiles(token: string, tenantId?: string) {
    let url = `${API_BASE_URL}/api/v1/audio?`;
    if (tenantId) url += `&tenant_id=${tenantId}`;
    const res = await fetch(url, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch audio files');
    return res.json();
  },

  async uploadAudioFile(token: string, formData: FormData) {
    const res = await fetch(`${API_BASE_URL}/api/v1/audio/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload audio file');
    return res.json();
  },

  // Hunt Groups, IVR, Trunks, Gateways, Users
  async getHuntGroups(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/hunt-groups`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch hunt groups');
    return res.json();
  },
  async createHuntGroup(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/hunt-groups`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to create hunt group');
    return res.json();
  },
  async getIvrs(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/ivr`, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch IVRs');
    return res.json();
  },
  async createIvr(token: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/ivr`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to create IVR');
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
    if (!res.ok) throw new Error('Failed to create trunk');
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
    if (!res.ok) throw new Error('Failed to assign gateway');
    return res.json();
  },
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
    if (!res.ok) throw new Error('Failed to create user');
    return res.json();
  },
  async deleteUser(token: string, userId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to delete user');
  },
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

with open(os.path.join(base_src, "services", "api.ts"), "w", encoding="utf-8") as f:
    f.write(api_ts)

# 7. SIDEBAR.TSX & APP.TSX WITH REPORTS & AUDIO TABS
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

        <button className={`nav-item ${activeTab === 'audio' ? 'active' : ''}`} onClick={() => setActiveTab('audio')}>
          <i className="bi bi-[#FF5430] bi-mic"></i><span className="nav-text">Audio Prompts</span>
        </button>

        <button className={`nav-item ${activeTab === 'huntgroups' ? 'active' : ''}`} onClick={() => setActiveTab('huntgroups')}>
          <i className="bi bi-telephone-forward"></i><span className="nav-text">Hunt Groups</span>
        </button>

        <div className="nav-label">Reports & Analytics</div>
        <button className={`nav-item ${activeTab === 'reports' ? 'active' : ''}`} onClick={() => setActiveTab('reports')}>
          <i className="bi bi-bar-chart-line"></i><span className="nav-text">Reports & CDR</span>
        </button>

        <div className="nav-label">Administration</div>
        <button className={`nav-item ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>
          <i className="bi bi-person-badge"></i><span className="nav-text">Users & Admins</span>
        </button>

        <button className={`nav-item ${activeTab === 'tenants' ? 'active' : ''}`} onClick={() => setActiveTab('tenants')}>
          <i className="bi bi-building"></i><span className="nav-text">Tenants</span>
        </button>
      </div>
    </aside>
  );
};
'''

with open(os.path.join(base_comp, "Sidebar.tsx"), "w", encoding="utf-8") as f:
    f.write(sidebar_tsx)


# 8. APP.TSX
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
import { ReportsView } from './components/ReportsView';
import { AudioView } from './components/AudioView';
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
          {activeTab === 'audio' && <AudioView token={token} />}
          {activeTab === 'huntgroups' && <HuntGroupsView token={token} />}
          {activeTab === 'reports' && <ReportsView token={token} />}
        </div>
      </main>
    </div>
  );
};

export default App;
'''

with open(os.path.join(base_src, "App.tsx"), "w", encoding="utf-8") as f:
    f.write(app_tsx)

print("Frontend features built successfully.")
