import re

# 1. Fix ToastProvider.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/ToastProvider.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('ShieldAlert, ', '').replace(', ShieldAlert', '')
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/ToastProvider.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed ToastProvider.tsx")

# 2. Fix CallForwardingView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/CallForwardingView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'const \[successMsg, setSuccessMsg\] = useState<string \| null>\(null\);', '', c)
c = re.sub(r'\{successMsg && \([\s\S]*?\}\)', '', c)
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/CallForwardingView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed CallForwardingView.tsx")

# 3. Fix VoicemailView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/VoicemailView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'const \[successMsg, setSuccessMsg\] = useState<string \| null>\(null\);', '', c)
c = re.sub(r'\{successMsg && \([\s\S]*?\}\)', '', c)
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/VoicemailView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed VoicemailView.tsx")

# 4. Fix QueuesView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/QueuesView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('`Queue "${name}" (ext/${queueNumber}) has been saved.`', '`Queue "${formData.name}" (ext/${formData.queue_number}) has been saved.`')
c = c.replace("alert(err.message || 'Failed to save call queue');", "showErrorModal('Failed to Save Queue', err.message || 'Failed to save call queue');")
c = c.replace("alert(err.message || 'Failed to delete queue');", "showErrorModal('Failed to Delete Queue', err.message || 'Failed to delete queue');")
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/QueuesView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed QueuesView.tsx")

# 5. Fix HuntGroupsView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/HuntGroupsView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
old_hg = """      await apiService.createHuntGroup(token, payload);
      setShowModal(false);
      setFormData({ name: '', extension_number: '', strategy: 'sequential', members: '1001, 1002', timeout: 20, tenant_id: '' });
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to create hunt group');
    }"""
new_hg = """      await apiService.createHuntGroup(token, payload);
      setShowModal(false);
      showSuccessModal('Hunt Group Created', `Hunt group "${formData.name}" (ext/${formData.extension_number}) configured.`);
      setFormData({ name: '', extension_number: '', strategy: 'sequential', members: '1001, 1002', timeout: 20, tenant_id: '' });
      loadData();
    } catch (err: any) {
      showErrorModal('Failed to Create Hunt Group', err.message || 'Failed to create hunt group');
    }"""
c = c.replace(old_hg, new_hg)
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/HuntGroupsView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed HuntGroupsView.tsx")

# 6. Fix RoutingView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/RoutingView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("alert(err.message || 'Failed to create route');", "showErrorModal('Failed to Create Route', err.message || 'Failed to create route');")
c = c.replace("alert(err.message || 'Failed to delete route');", "showErrorModal('Failed to Delete Route', err.message || 'Failed to delete route');")
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/RoutingView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed RoutingView.tsx")

# 7. Fix DidsView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/DidsView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("alert(err.message || 'Failed to add DID');", "showErrorModal('Failed to Add DID', err.message || 'Failed to add DID');")
c = c.replace("alert(err.message || 'Failed to assign DID');", "showErrorModal('Failed to Assign DID', err.message || 'Failed to assign DID');")
c = c.replace("alert(err.message || 'Failed to unassign DID');", "showErrorModal('Failed to Unassign DID', err.message || 'Failed to unassign DID');")
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/DidsView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed DidsView.tsx")

# 8. Fix TrunksView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/TrunksView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
old_tr = """      await apiService.createTrunk(token, formData);
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
    }"""
new_tr = """      await apiService.createTrunk(token, formData);
      setShowModal(false);
      showSuccessModal('SIP Trunk Registered', `SIP trunk "${formData.name}" (${formData.host}:${formData.port}) created successfully.`);
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
      showErrorModal('Failed to Create Trunk', err.message || 'Failed to create SIP trunk');
    }"""
c = c.replace(old_tr, new_tr)
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/TrunksView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed TrunksView.tsx")

# 9. Fix AudioView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/AudioView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("alert('Please select an audio file to upload');", "showErrorModal('Upload Warning', 'Please select an audio file to upload');")
c = c.replace("alert(err.message || 'Failed to upload audio file');", "showErrorModal('Upload Failed', err.message || 'Failed to upload audio file');")
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/AudioView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed AudioView.tsx")

# 10. Fix ExtensionsView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/ExtensionsView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()

old_ext_create = """  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    try {
      await apiService.createExtension(token, {
        tenant_id: tenantId || undefined,
        extension_number: extNumber,
        display_name: displayName,
        email,
        sip_password: sipPassword,
        voicemail_pin: voicemailPin,
      });
      setShowModal(false);
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };"""

new_ext_create = """  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    try {
      const cleanEmail = email && email.trim() ? email.trim() : undefined;
      await apiService.createExtension(token, {
        tenant_id: tenantId || (user?.tenant_id ?? undefined),
        extension_number: extNumber,
        display_name: displayName,
        email: cleanEmail,
        sip_password: sipPassword,
        voicemail_pin: voicemailPin,
      });
      setShowModal(false);
      showSuccessModal(
        'Extension Provisioned Successfully',
        `Extension ext/${extNumber} (${displayName}) has been created and registered for SIP and WebRTC softphones.`
      );
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
      showErrorModal('Failed to Provision Extension', msg);
    } finally {
      setLoading(false);
    }
  };"""
c = c.replace(old_ext_create, new_ext_create)

old_ext_pwd = """  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !selectedExtId) return;
    setLoading(true);
    try {
      await apiService.resetExtensionPassword(token, selectedExtId, {
        new_sip_password: newSipPwd || undefined,
        new_voicemail_pin: newVmPin || undefined,
      });
      setShowResetModal(false);
      setSelectedExtId(null);
      setNewSipPwd('');
      setNewVmPin('');
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };"""

new_ext_pwd = """  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !selectedExtId) return;
    setLoading(true);
    try {
      await apiService.resetExtensionPassword(token, selectedExtId, {
        new_sip_password: newSipPwd || undefined,
        new_voicemail_pin: newVmPin || undefined,
      });
      setShowResetModal(false);
      setSelectedExtId(null);
      setNewSipPwd('');
      setNewVmPin('');
      showSuccessModal('Credentials Reset', 'SIP authentication password and voicemail PIN have been updated successfully.');
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
      showErrorModal('Password Reset Failed', msg);
    } finally {
      setLoading(false);
    }
  };"""
c = c.replace(old_ext_pwd, new_ext_pwd)

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/ExtensionsView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed ExtensionsView.tsx")

# 11. Fix IvrView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/IvrView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace any toastError with showErrorModal
c = c.replace("toastError('Failed to create IVR', err.message);", "showErrorModal('Failed to Create IVR', err.message);")
c = c.replace("toastError('Failed to save DTMF action', err.message);", "showErrorModal('Failed to Save Action', err.message);")
c = c.replace("toastError('Failed to delete DTMF action', err.message);", "showErrorModal('Failed to Delete Action', err.message);")
c = c.replace("toastError('Failed to delete IVR', err.message);", "showErrorModal('Failed to Delete IVR', err.message);")

# Add showSuccessModal in handleCreate
old_ivr_cr = """      await apiService.createIvr(token, payload);
      setShowCreateModal(false);
      setNewName('');
      setNewDesc('');
      loadData();"""

new_ivr_cr = """      await apiService.createIvr(token, payload);
      setShowCreateModal(false);
      showSuccessModal('IVR Flow Created', `Interactive Voice Response menu "${newName}" has been created.`);
      setNewName('');
      setNewDesc('');
      loadData();"""
c = c.replace(old_ivr_cr, new_ivr_cr)

# Add showSuccessModal in node save
old_ivr_nd = """      await apiService.upsertIvrNode(token, activeIvr.id, payload);
      await loadNodes(activeIvr.id);
      setShowNodeModal(false);"""
new_ivr_nd = """      await apiService.upsertIvrNode(token, activeIvr.id, payload);
      await loadNodes(activeIvr.id);
      showSuccessModal('DTMF Key Action Saved', `Action for Key ${nodeKey} has been configured.`);
      setShowNodeModal(false);"""
c = c.replace(old_ivr_nd, new_ivr_nd)

# Add showSuccessModal in IVR delete
old_ivr_dl = """    try {
      await apiService.deleteIvr(token, activeIvr.id);
      setActiveIvr(null);
      setNodes([]);
      loadData();
    } catch (err: any) {"""
new_ivr_dl = """    try {
      await apiService.deleteIvr(token, activeIvr.id);
      showSuccessModal('IVR Flow Deleted', 'The IVR menu has been deleted.');
      setActiveIvr(null);
      setNodes([]);
      loadData();
    } catch (err: any) {"""
c = c.replace(old_ivr_dl, new_ivr_dl)

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/IvrView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed IvrView.tsx")

print("All components cleanly updated!")
