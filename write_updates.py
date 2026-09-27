import sys, os
sys.stdout.reconfigure(encoding='utf-8')
with open(r'c:\\PROJECTS\\Fullstack PBX\\frontend\\src\\components\\RoutingView.tsx', 'w', encoding='utf-8') as f: f.write(r'''import type { User } from '../types';
import { useToast } from './ToastProvider';
import React, { useState, useEffect, useMemo } from 'react';
import { apiService, getApiBaseUrl } from '../services/api';
import { Route as RouteIcon, Plus, Search, Trash2 } from 'lucide-react';

interface RoutingViewProps {
  token: string;
  user?: User | null;
}

export const RoutingView: React.FC<RoutingViewProps> = ({ token, user }) => {
  const { showSuccessModal, showErrorModal } = useToast();
  const [routes, setRoutes] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [extensions, setExtensions] = useState<any[]>([]);
  const [queues, setQueues] = useState<any[]>([]);
  const [ivrs, setIvrs] = useState<any[]>([]);
  const [dids, setDids] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    did_number: '',
    route_type: 'inbound_did',
    destination_type: 'queue',
    destination: '',
    priority: 1,
    gateway_id: '',
    tenant_id: user?.tenant_id || ''
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [rData, tData, extData, qData, ivrData, didData] = await Promise.allSettled([
        apiService.getRoutingRules(token),
        apiService.getTenants(token),
        apiService.getExtensions(token),
        apiService.getQueues(token),
        apiService.getIvrs(token),
        apiService.getDids(token),
      ]);
      if (rData.status === 'fulfilled') setRoutes(rData.value);
      if (tData.status === 'fulfilled') setTenants(tData.value);
      if (extData.status === 'fulfilled') setExtensions(extData.value);
      if (qData.status === 'fulfilled') setQueues(qData.value);
      if (ivrData.status === 'fulfilled') setIvrs(ivrData.value);
      if (didData.status === 'fulfilled') setDids(didData.value);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadData(); }, [token]);

  const assignedDids = useMemo(() => {
    if (user?.role === 'SUPER_ADMIN') return dids;
    return dids.filter((d:any) => d.tenant_id === user?.tenant_id || !d.tenant_id);
  }, [dids, user]);

  const destinationOptions = useMemo(() => {
    switch (formData.destination_type) {
      case 'extension':
        return extensions.map(e=>({value:e.extension_number,label:`ext/${e.extension_number} — ${e.display_name||e.extension_number}`}));
      case 'queue':
        return queues.map(q=>({value:q.queue_number,label:`${q.queue_number} — ${q.name}`}));
      case 'ivr':
        return ivrs.map(i=>({value:i.name,label:i.name}));
      case 'voicemail':
        return extensions.map(e=>({value:e.extension_number,label:`ext/${e.extension_number} — ${e.display_name||e.extension_number}`}));
      default: return [];
    }
  }, [formData.destination_type, extensions, queues, ivrs]);

  const handleDestTypeChange = (newType:string)=>{
    let def='';
    if(newType==='queue') def=queues[0]?.queue_number||'';
    else if(newType==='extension') def=extensions[0]?.extension_number||'';
    else if(newType==='ivr') def=ivrs[0]?.name||'';
    else if(newType==='voicemail') def=extensions[0]?.extension_number||'';
    setFormData({...formData,destination_type:newType,destination:def});
  };

  const handleCreate = async (e:React.FormEvent)=>{
    e.preventDefault();
    try {
      const payload:any={...formData};
      if(user?.role!=='SUPER_ADMIN' && user?.tenant_id) payload.tenant_id=user.tenant_id;
      else if(!payload.tenant_id) delete payload.tenant_id;
      if(!payload.gateway_id) delete payload.gateway_id;
      const name=payload.name;
      await apiService.createRoute(token,payload);
      setShowModal(false);
      setFormData({name:'',did_number:'',route_type:'inbound_did',destination_type:'queue',destination:'',priority:1,gateway_id:'',tenant_id:user?.tenant_id||''});
      showSuccessModal('Routing Rule Configured',`Routing rule "${name}" has been configured.`);
      loadData();
    } catch(err:any){ showErrorModal('Failed to Create Route', err.message||'Failed'); }
  };

  const handleDelete = async (routeId:string)=>{ if(!window.confirm('Delete?'))return; try{await apiService.deleteRoute(token,routeId);showSuccessModal('Deleted','');loadData();}catch(err:any){showErrorModal('Delete error',err.message||'');}};

  const filtered=routes.filter(r=> r.name.toLowerCase().includes(search.toLowerCase()) || (r.did_number && r.did_number.includes(search)) );

  return (
    <div>
      <div className="page-head"><div><div className="eyebrow">Dialplan Engine</div><h1 className="page-title">Call Routing Rules</h1><p className="page-sub">Configure tenant-wise inbound DID routing and outbound pattern matching</p></div><div><button className="btn-primary" onClick={()=>setShowModal(true)}><Plus size={16}/> Add Routing Rule</button></div></div>
      <div style={{background:'#FFFFFF',borderRadius:'12px',border:'1px solid var(--border)',overflow:'hidden'}}>
        <div style={{padding:'16px 20px',borderBottom:'1px solid var(--border)',display:'flex',gap:'12px'}}>
          <div style={{position:'relative',width:'280px'}}><Search size={16} style={{position:'absolute',left:'12px',top:'50%',transform:'translateY(-50%)',color:'#9CA3AF'}}/>
            <input className="form-control" style={{paddingLeft:'36px',height:'38px',fontSize:'12px'}} placeholder="Search routes..." value={search} onChange={e=>setSearch(e.target.value)} />
          </div>
        </div>
        <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Route Name</th><th>DID / Pattern</th><th>Type</th><th>Destination Type</th><th>Target Destination</th><th>Priority</th><th>Tenant</th><th className="text-right">Actions</th></tr></thead><tbody>{loading? <tr><td colSpan={8} className="text-center py-4">Loading...</td></tr> : filtered.length===0 ? <tr><td colSpan={8} className="text-center py-4 text-muted">No routing rules</td></tr> : filtered.map(r=>(<tr key={r.id}><td><div style={{fontWeight:700,color:'#111827'}}>{r.name}</div></td><td><code className="code-box" style={{padding:'4px 8px',fontSize:'11px'}}>{r.did_number||r.regex_pattern||'*'}</code></td><td>{r.route_type==='inbound_did'?<span className="terrix-badge green">INBOUND</span>:<span className="terrix-badge orange">OUTBOUND</span>}</td><td><span className="terrix-badge grey">{r.destination_type?.toUpperCase()}</span></td><td><strong style={{color:'#111827'}}>{r.destination}</strong></td><td><span style={{fontWeight:700}}>P{r.priority}</span></td><td><span className="terrix-badge orange">{r.tenant_name||'Global'}</span></td><td className="text-right"><button className="btn-secondary text-rose-600" style={{padding:'4px 8px',fontSize:'11px'}} onClick={()=>handleDelete(r.id)}><Trash2 size={13}/></button></td></tr>))}</tbody></table></div>
      </div>
      {showModal && (
        <div className="modal-backdrop"><div className="terrix-modal" style={{maxWidth:'580px'}}><div className="modal-head"><div className="modal-icon"><RouteIcon size={20}/></div><div><h3>Create Routing Rule</h3><p>Add tenant-wise inbound DID or outbound dialplan rule</p></div><button className="modal-close" onClick={()=>setShowModal(false)}>×</button></div>
          <form onSubmit={handleCreate}><div className="modal-body"><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'16px'}}>
            <div className="form-group"><label className="form-label required">Route Name</label><input required className="form-control" value={formData.name} onChange={e=>setFormData({...formData,name:e.target.value})} placeholder="e.g. Sales DID Inbound"/></div>
            <div className="form-group"><label className="form-label">Route Type</label><select className="form-control" value={formData.route_type} onChange={e=>setFormData({...formData,route_type:e.target.value})}><option value="inbound_did">Inbound DID Route</option><option value="outbound">Outbound Dialplan Rule</option></select></div>
            <div className="form-group"><label className="form-label">{formData.route_type==='inbound_did'?'DID Number (Assigned to Tenant)':'Regex / Match Pattern'}</label>{formData.route_type==='inbound_did'?(
              <select className="form-control" value={formData.did_number} onChange={e=>setFormData({...formData,did_number:e.target.value})}>
                <option value="">-- Select Assigned DID --</option>
                {assignedDids.map((d:any)=>(<option key={d.id} value={d.did_number}>{d.did_number}{d.tenant_name?` (${d.tenant_name})`:' (Unassigned)'}</option>))}
                {assignedDids.length===0 && <option disabled value="">No DIDs assigned</option>}
              </select>
            ):(<input className="form-control" value={formData.did_number} onChange={e=>setFormData({...formData,did_number:e.target.value})} placeholder="e.g. ^91\d{10}$"/>)}</div>
            <div className="form-group"><label className="form-label">Destination Type</label><select className="form-control" value={formData.destination_type} onChange={e=>handleDestTypeChange(e.target.value)}><option value="queue">Call Queue</option><option value="extension">Extension</option><option value="ivr">IVR Menu Flow</option><option value="voicemail">Voicemail Box</option></select></div>
            <div className="form-group" style={{gridColumn:'1 / -1'}}><label className="form-label required">Destination Target<small style={{color:'#6B7280',fontWeight:400,marginLeft:'8px'}}>({formData.destination_type==='queue'?`${queues.length} queue(s)`:formData.destination_type==='ivr'?`${ivrs.length} IVR flow(s)`:`${extensions.length} extension(s)`} available)</small></label>{destinationOptions.length>0?(<select required className="form-control" value={formData.destination} onChange={e=>setFormData({...formData,destination:e.target.value})}> <option value="">-- Select {formData.destination_type==='queue'?'Call Queue':formData.destination_type==='ivr'?'IVR Flow':'Extension'} --</option>{destinationOptions.map(opt=>(<option key={opt.value} value={opt.value}>{opt.label}</option>))}</select>) : (<input required className="form-control" value={formData.destination} onChange={e=>setFormData({...formData,destination:e.target.value})} placeholder="e.g. 7001 or 1001"/>)} </div>
            {user?.role==='SUPER_ADMIN' && (<div className="form-group" style={{gridColumn:'1 / -1'}}><label className="form-label">Target Tenant (Optional)</label><select className="form-control" value={formData.tenant_id} onChange={e=>setFormData({...formData,tenant_id:e.target.value})}><option value="">-- Global / Select Tenant --</option>{tenants.map(t=>(<option key={t.id} value={t.id}>{t.name} ({t.domain})</option>))}</select></div>)
          </div></div><div className="modal-foot"><button type="button" className="btn-secondary" onClick={()=>setShowModal(false)}>Cancel</button><button type="submit" className="btn-primary">Save Routing Rule</button></div></form></div></div>
      )}
    </div>
  );
};
''')
with open(r'c:\\PROJECTS\\Fullstack PBX\\frontend\\src\\components\\QueuesView.tsx', 'w', encoding='utf-8') as f: f.write(r'''import type { User } from '../types';
import { useToast } from './ToastProvider';
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Users, Plus, Edit2, Trash2 } from 'lucide-react';

interface QueuesViewProps {
  token: string;
  user?: User | null;
}

export const QueuesView: React.FC<QueuesViewProps> = ({ token, user }) => {
  const { showSuccessModal, showErrorModal } = useToast();
  const [queues, setQueues] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [extensions, setExtensions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [editingQueue, setEditingQueue] = useState<any>(null);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    queue_number: '',
    strategy: 'round_robin',
    agent_timeout: 30,
    wrap_up_time: 10,
    max_wait_time: 300,
    tenant_id: ''
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [qData, tData, extData] = await Promise.allSettled([
        apiService.getQueues(token),
        apiService.getTenants(token),
        apiService.getExtensions(token),
      ]);
      if (qData.status === 'fulfilled') setQueues(qData.value);
      if (tData.status === 'fulfilled') setTenants(tData.value);
      if (extData.status === 'fulfilled') setExtensions(extData.value);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const toggleAgent = (extNum: string) => {
    setSelectedAgents(prev =>
      prev.includes(extNum) ? prev.filter(a => a !== extNum) : [...prev, extNum]
    );
  };

  const openCreateModal = () => {
    setEditingQueue(null);
    setSelectedAgents(extensions.slice(0, 2).map(e => e.extension_number));
    setFormData({ name: '', queue_number: '', strategy: 'round_robin', agent_timeout: 30, wrap_up_time: 10, max_wait_time: 300, tenant_id: user?.tenant_id || '' });
    setShowModal(true);
  };

  const handleOpenEdit = (q: any) => {
    setEditingQueue(q);
    const agentList = q.agents ? q.agents.split(',').map((s: string) => s.trim()).filter(Boolean) : [];
    setSelectedAgents(agentList);
    setFormData({
      name: q.name,
      queue_number: q.queue_number,
      strategy: q.strategy || 'round_robin',
      agent_timeout: q.agent_timeout || 30,
      wrap_up_time: q.wrap_up_time || 10,
      max_wait_time: q.max_wait_time || 300,
      tenant_id: q.tenant_id || user?.tenant_id || '',
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        ...formData,
        agents: selectedAgents.join(', '),
      };
      if (user?.role !== 'SUPER_ADMIN' && user?.tenant_id) payload.tenant_id = user.tenant_id;
      else if (!payload.tenant_id) delete payload.tenant_id;

      if (editingQueue) {
        await apiService.updateQueue(token, editingQueue.id, payload);
        showSuccessModal('Call Queue Updated', `Queue "${payload.name}" has been updated.`);
      } else {
        await apiService.createQueue(token, payload);
        showSuccessModal('Call Queue Saved', `Queue "${payload.name}" (ext/${payload.queue_number}) has been configured.`);
      }
      setShowModal(false);
      setEditingQueue(null);
      loadData();
    } catch (err: any) {
      showErrorModal('Failed to Save Queue', err.message || 'Failed to save call queue');
    }
  };

  const handleDelete = async (queueId: string) => {
    if (!window.confirm('Are you sure you want to delete this queue?')) return;
    try {
      await apiService.deleteQueue(token, queueId);
      showSuccessModal('Queue Deleted', 'Call queue has been removed.');
      loadData();
    } catch (err: any) {
      showErrorModal('Failed to Delete Queue', err.message || 'Failed to delete queue');
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="eyebrow">mod_callcenter</div>
          <h1 className="page-title">Call Queues</h1>
          <p className="page-sub">Configure ACD queues, ring strategies, and agent member lists</p>
        </div>
        <div>
          <button className="btn-primary" onClick={openCreateModal}>
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
                <th>Max Wait</th>
                <th>Members</th>
                <th>Tenant</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="text-center py-4">Loading queues...</td></tr>
              ) : queues.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-4 text-muted">No call queues configured</td></tr>
              ) : (
                queues.map(q => (
                  <tr key={q.id}>
                    <td><div style={{ fontWeight: 700, color: '#111827' }}>{q.name}</div></td>
                    <td><code className="code-box" style={{ padding: '4px 8px', fontSize: '11px' }}>{q.queue_number}</code></td>
                    <td><span className="terrix-badge grey">{q.strategy?.toUpperCase()}</span></td>
                    <td>{q.agent_timeout}s</td>
                    <td>{q.max_wait_time}s</td>
                    <td>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '200px' }}>
                        {q.agents ? q.agents.split(',').map((a: string) => (
                          <span key={a.trim()} className="terrix-badge grey" style={{ fontSize: '10px' }}>ext/{a.trim()}</span>
                        )) : <span style={{ color: '#9CA3AF', fontSize: '12px' }}>All Extensions</span>}
                      </div>
                    </td>
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
          <div className="terrix-modal" style={{ maxWidth: '620px' }}>
            <div className="modal-head">
              <div className="modal-icon"><Users size={20} /></div>
              <div><h3>{editingQueue ? 'Edit Call Queue' : 'Create Call Queue'}</h3><p>Configure mod_callcenter agent distribution strategy</p></div>
              <button className="modal-close" onClick={() => setShowModal(false)}>x</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="form-group">
                    <label className="form-label required">Queue Name</label>
                    <input required className="form-control" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Support Escalations" />
                  </div>
                  <div className="form-group">
                    <label className="form-label required">Virtual Extension Number</label>
                    <input required className="form-control" value={formData.queue_number} onChange={e => setFormData({...formData, queue_number: e.target.value})} placeholder="e.g. 7001" />
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
                  <div className="form-group">
                    <label className="form-label">Wrap Up Time (seconds)</label>
                    <input type="number" className="form-control" value={formData.wrap_up_time} onChange={e => setFormData({...formData, wrap_up_time: parseInt(e.target.value) || 10})} />
                  </div>

                  {user?.role === 'SUPER_ADMIN' && (
                    <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                      <label className="form-label">Target Tenant (Optional)</label>
                      <select className="form-control" value={formData.tenant_id} onChange={e => setFormData({...formData, tenant_id: e.target.value})}>
                        <option value="">-- Global / Select Tenant --</option>
                        {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                      </select>
                    </div>
                  )}

                  {/* Multi-select Extensions */}
                  <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                    <label className="form-label">
                      Agent Member Extensions
                      <small style={{ color: '#6B7280', fontWeight: 400, marginLeft: '8px' }}>
                        ({selectedAgents.length} selected of {extensions.length})
                      </small>
                    </label>
                    {extensions.length > 0 ? (
                      <div style={{
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        maxHeight: '200px',
                        overflowY: 'auto',
                        background: '#F9FAFB',
                        padding: '8px',
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                        gap: '6px',
                      }}>
                        {extensions.map(ext => {
                          const selected = selectedAgents.includes(ext.extension_number);
                          return (
                            <label key={ext.extension_number} style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '8px 10px',
                              borderRadius: '6px',
                              cursor: 'pointer',
                              background: selected ? '#FFF3E0' : '#FFFFFF',
                              border: `1px solid ${selected ? '#FF9800' : '#E5E7EB'}`,
                              transition: 'all 0.15s ease',
                              userSelect: 'none',
                            }}>
                              <input
                                type="checkbox"
                                checked={selected}
                                onChange={() => toggleAgent(ext.extension_number)}
                                style={{ accentColor: '#FF5722', width: '14px', height: '14px' }}
                              />
                              <div>
                                <div style={{ fontWeight: 600, fontSize: '12px', color: '#111827' }}>ext/{ext.extension_number}</div>
                                <div style={{ fontSize: '11px', color: '#6B7280' }}>{ext.display_name || ext.extension_number}</div>
                              </div>
                            </label>
                          );
                        })}
                      </div>
                    ) : (
                      <div style={{ padding: '12px', background: '#FEF9C3', borderRadius: '8px', fontSize: '13px', color: '#92400E', border: '1px solid #FDE68A' }}>
                        No extensions found. Please provision extensions first.
                      </div>
                    )}
                    {selectedAgents.length > 0 && (
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#374151' }}>
                        Selected: {selectedAgents.map(a => `ext/${a}`).join(', ')}
                      </div>
                    )}
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
''')
with open(r'c:\\PROJECTS\\Fullstack PBX\\frontend\\src\\components\\HuntGroupsView.tsx', 'w', encoding='utf-8') as f: f.write(r'''import type { User } from '../types';
import { useToast } from './ToastProvider';
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { PhoneForwarded, Plus } from 'lucide-react';

interface HuntGroupsViewProps { token: string; user?: User | null; }
export const HuntGroupsView: React.FC<HuntGroupsViewProps> = ({ token, user }) => {
  const { showSuccessModal, showErrorModal } = useToast();
  const [huntGroups, setHuntGroups] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [extensions, setExtensions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState<any>(null);
  const [selectedMembers, setSelectedMembers] = useState<string[]>([]);
  const [formData, setFormData] = useState({ name:'', extension_number:'', strategy:'sequential', timeout:20, tenant_id: user?.tenant_id || '' });

  const loadData = async () => {
    try { setLoading(true);
      const [hgData, tData, extData] = await Promise.allSettled([
        apiService.getHuntGroups(token),
        apiService.getTenants(token),
        apiService.getExtensions(token),
      ]);
      if (hgData.status==='fulfilled') setHuntGroups(hgData.value);
      if (tData.status==='fulfilled') setTenants(tData.value);
      if (extData.status==='fulfilled') setExtensions(extData.value);
    } catch(err){ console.error(err); } finally { setLoading(false); }
  };
  useEffect(()=>{ loadData(); },[token]);

  const toggleMember = (extNum:string)=>{
    setSelectedMembers(prev=> prev.includes(extNum) ? prev.filter(m=>m!==extNum) : [...prev,extNum]);
  };

  const openCreate =()=>{ setEditingGroup(null); setSelectedMembers([]); setFormData({name:'',extension_number:'',strategy:'sequential',timeout:20,tenant_id:user?.tenant_id||''}); setShowModal(true); };
  const openEdit = (hg:any)=>{ setEditingGroup(hg); setSelectedMembers(hg.members ? hg.members.split(',').map((s:string)=>s.trim()) : []);
    setFormData({name:hg.name,extension_number:hg.extension_number,strategy:hg.strategy||'sequential',timeout:hg.timeout||20,tenant_id:hg.tenant_id||user?.tenant_id||''}); setShowModal(true); };

  const handleSubmit = async (e:React.FormEvent)=>{ e.preventDefault();
    try {
      const payload:any={...formData, members:selectedMembers.join(',')};
      if (user?.role!=='SUPER_ADMIN' && user?.tenant_id) payload.tenant_id=user.tenant_id; else if(!payload.tenant_id) delete payload.tenant_id;
      if (editingGroup) { await apiService.updateHuntGroup(token, editingGroup.id, payload); showSuccessModal('Hunt Group Updated',''); } else { await apiService.createHuntGroup(token, payload); showSuccessModal('Hunt Group Created',''); }
      setShowModal(false); loadData();
    } catch(err:any){ showErrorModal('Failed', err.message||''); }
  };

  const handleDelete = async (id:string)=>{ if(!window.confirm('Delete?'))return; try{ await apiService.deleteHuntGroup(token,id); showSuccessModal('Deleted',''); loadData(); }catch(err:any){showErrorModal('Delete error',err.message||''); } };

  return (
    <div>
      <div className="page-head"><div><div className="eyebrow">mod_huntgroup</div><h1 className="page-title">Hunt Groups</h1><p className="page-sub">Configure hunt groups and member extensions</p></div><div><button className="btn-primary" onClick={openCreate}><Plus size={16}/> Create Hunt Group</button></div></div>
      <div style={{background:'#FFFFFF',borderRadius:'12px',border:'1px solid var(--border)',overflow:'hidden'}}>
        <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Name</th><th>Extension</th><th>Strategy</th><th>Timeout</th><th>Members</th><th>Tenant</th><th className="text-right">Actions</th></tr></thead><tbody>{loading? <tr><td colSpan={7} className="text-center py-4">Loading...</td></tr> : huntGroups.length===0 ? <tr><td colSpan={7} className="text-center py-4 text-muted">No hunt groups</td></tr> : huntGroups.map(hg=>(<tr key={hg.id}><td>{hg.name}</td><td>{hg.extension_number}</td><td>{hg.strategy}</td><td>{hg.timeout}s</td><td>{hg.members}</td><td><span className="terrix-badge orange">{hg.tenant_name||'Global'}</span></td><td className="text-right"><button className="btn-secondary" style={{marginRight:'6px'}} onClick={()=>openEdit(hg)}><PhoneForwarded size={13}/> Edit</button><button className="btn-secondary text-rose-600" onClick={()=>handleDelete(hg.id)}><Trash2 size={13}/></button></td></tr>))}</tbody></table></div>
      </div>
      {showModal && (
        <div className="modal-backdrop"><div className="terrix-modal" style={{maxWidth:'580px'}}><div className="modal-head"><div className="modal-icon"><PhoneForwarded size={20}/></div><div><h3>{editingGroup?'Edit':'Create'} Hunt Group</h3></div><button className="modal-close" onClick={()=>setShowModal(false)}>×</button></div>
          <form onSubmit={handleSubmit}><div className="modal-body"><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'16px'}}>
            <div className="form-group"><label className="form-label required">Group Name</label><input required className="form-control" value={formData.name} onChange={e=>setFormData({...formData,name:e.target.value})}/></div>
            <div className="form-group"><label className="form-label required">Extension</label><input required className="form-control" value={formData.extension_number} onChange={e=>setFormData({...formData,extension_number:e.target.value})}/></div>
            <div className="form-group"><label className="form-label">Strategy</label><select className="form-control" value={formData.strategy} onChange={e=>setFormData({...formData,strategy:e.target.value})}><option value="sequential">Sequential</option><option value="round_robin">Round Robin</option></select></div>
            <div className="form-group"><label className="form-label">Timeout (s)</label><input type="number" className="form-control" value={formData.timeout} onChange={e=>setFormData({...formData,timeout:parseInt(e.target.value)||20})}/></div>
            <div className="form-group" style={{gridColumn:'1 / -1'}}><label className="form-label required">Member Extensions</label>
              <div style={{border:'1px solid #D1D5DB',borderRadius:'8px',maxHeight:'200px',overflowY:'auto',background:'#F9FAFB',padding:'8px'}}>
                {extensions.map(ext=>{
                  const sel=selectedMembers.includes(ext.extension_number);
                  return (<label key={ext.extension_number} style={{display:'flex',alignItems:'center',gap:'8px',padding:'6px',background:sel?'#FFF3E0':'#FFFFFF',border:`1px solid ${sel?'#FF9800':'#E5E7EB'}`}}>
                    <input type="checkbox" checked={sel} onChange={()=>toggleMember(ext.extension_number)} style={{accentColor:'#FF5722'}}/> <span>ext/{ext.extension_number} {ext.display_name||''}</span>
                  </label>);
                })}
              </div>
            </div>
            {user?.role==='SUPER_ADMIN' && (<div className="form-group" style={{gridColumn:'1 / -1'}}><label className="form-label">Target Tenant (Optional)</label><select className="form-control" value={formData.tenant_id} onChange={e=>setFormData({...formData,tenant_id:e.target.value})}><option value="">-- Global / Select Tenant --</option>{tenants.map(t=>(<option key={t.id} value={t.id}>{t.name} ({t.domain})</option>))}</select></div>)}
          </div></div><div className="modal-foot"><button type="button" className="btn-secondary" onClick={()=>setShowModal(false)}>Cancel</button><button type="submit" className="btn-primary">Save</button></div></form></div></div>
      )}
    </div>
  );
};
''')
with open(r'c:\\PROJECTS\\Fullstack PBX\\frontend\\src\\components\\AudioView.tsx', 'w', encoding='utf-8') as f: f.write(r'''import type { User } from '../types';
import { useToast } from './ToastProvider';
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { Mic, Upload, Play, Pause } from 'lucide-react';

interface AudioViewProps {
  token: string;
  user?: User | null;
}

export const AudioView: React.FC<AudioViewProps> = ({ token, user }) => {
  const { showSuccessModal, showErrorModal } = useToast();
  const [audioFiles, setAudioFiles] = useState<any[]>([]);
  const [tenants, setTenants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [category, setCategory] = useState('ivr_greeting');
  const [tenantId, setTenantId] = useState(user?.tenant_id || '');

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

  const [playingId, setPlayingId] = useState<string | null>(null);
  const [audioPlayer, setAudioPlayer] = useState<HTMLAudioElement | null>(null);

  const handlePlayAudio = (a: any) => {
    if (playingId === a.id && audioPlayer) {
      audioPlayer.pause();
      setPlayingId(null);
      return;
    }
    if (audioPlayer) {
      audioPlayer.pause();
    }
    try {
      const audioUrl = `${getApiBaseUrl()}/api/v1/audio/${a.id || a.file_name}/stream`;
      const player = new Audio(audioUrl);
      player.onended = () => setPlayingId(null);
      player.onerror = () => {
        setPlayingId(null);
        showErrorModal('Audio Playback Error', `Failed to stream audio file: ${a.file_name}`);
      };
      player.play().then(() => {
        setAudioPlayer(player);
        setPlayingId(a.id);
        showSuccessModal('Audio Playing', `Now playing: ${a.file_name} (${a.category.toUpperCase()})`);
      }).catch(err => {
        setPlayingId(null);
        showErrorModal('Playback Blocked', err.message || 'Browser blocked audio autoplay');
      });
    } catch (err: any) {
      showErrorModal('Audio Error', err.message);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      showErrorModal('Upload Warning', 'Please select an audio file to upload');
      return;
    }
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('category', category);
    const tid = (user?.role !== 'SUPER_ADMIN' && user?.tenant_id) ? user.tenant_id : tenantId;
      if (tid) formData.append('tenant_id', tid);

    try {
      await apiService.uploadAudioFile(token, formData);
      setShowModal(false);
      showSuccessModal('Audio File Uploaded', `Audio prompt "${selectedFile?.name}" has been uploaded.`);
      setSelectedFile(null);
      loadData();
    } catch (err: any) {
      showErrorModal('Upload Failed', err.message || 'Failed to upload audio file');
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
                      <button
                        className={playingId === a.id ? "btn-primary" : "btn-secondary"}
                        style={{ padding: '5px 12px', fontSize: '11px', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                        onClick={() => handlePlayAudio(a)}
                      >
                        {playingId === a.id ? (
                          <>
                            <Pause size={13} /> Stop Playing
                          </>
                        ) : (
                          <>
                            <Play size={13} /> Play Audio
                          </>
                        )}
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
                {user?.role === 'SUPER_ADMIN' && (
                  <div className="form-group mb-3">
                    <label className="form-label">Target Tenant (Optional)</label>
                    <select className="form-control" value={tenantId} onChange={e => setTenantId(e.target.value)}>
                      <option value="">-- Global / Select Tenant --</option>
                      {tenants.map(t => <option key={t.id} value={t.id}>{t.name} ({t.domain})</option>)}
                    </select>
                  </div>
                )}
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
''')
