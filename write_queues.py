import sys
sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. QueuesView.tsx - multi-select extensions for members
# ============================================================
queues_content = r"""import type { User } from '../types';
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
"""

with open(r'c:\PROJECTS\Fullstack PBX\frontend\src\components\QueuesView.tsx', 'w', encoding='utf-8') as f:
    f.write(queues_content)
print("Written QueuesView.tsx")
