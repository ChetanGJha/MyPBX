import re

def update_file(path, transformer):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = transformer(content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated {path}")

# 1. CallForwardingView.tsx
def patch_cf(c):
    if "import { useToast } from './ToastProvider';" not in c:
        c = "import { useToast } from './ToastProvider';\n" + c
    c = c.replace(
        "export const CallForwardingView: React.FC<CallForwardingViewProps> = ({ token }) => {",
        "export const CallForwardingView: React.FC<CallForwardingViewProps> = ({ token }) => {\n  const { showSuccessModal, showErrorModal } = useToast();"
    )
    c = c.replace(
        "setSuccessMsg(`Call forwarding for ext/${editingRule.extension_number} updated.`);\n      setTimeout(() => setSuccessMsg(null), 4000);",
        "showSuccessModal('Forwarding Settings Updated', `Call forwarding rules for ext/${editingRule.extension_number} have been updated.`);"
    )
    c = c.replace(
        "} catch (err: any) {\n      setError(err.message);\n    } finally {",
        "} catch (err: any) {\n      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);\n      setError(msg);\n      showErrorModal('Update Failed', msg);\n    } finally {"
    )
    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/CallForwardingView.tsx', patch_cf)

# 2. VoicemailView.tsx
def patch_vm(c):
    if "import { useToast } from './ToastProvider';" not in c:
        c = "import { useToast } from './ToastProvider';\n" + c
    c = c.replace(
        "export const VoicemailView: React.FC<VoicemailViewProps> = ({ token }) => {",
        "export const VoicemailView: React.FC<VoicemailViewProps> = ({ token }) => {\n  const { showSuccessModal, showErrorModal } = useToast();"
    )
    c = c.replace(
        "setSuccessMsg(`Voicemail box for extension ${editingBox.extension_number} updated.`);\n      setTimeout(() => setSuccessMsg(null), 4000);",
        "showSuccessModal('Voicemail Configured', `Voicemail box for ext/${editingBox.extension_number} has been updated.`);"
    )
    c = c.replace(
        "} catch (err: any) {\n      setError(err.message);\n    } finally {\n      setSaving(false);",
        "} catch (err: any) {\n      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);\n      setError(msg);\n      showErrorModal('Configuration Failed', msg);\n    } finally {\n      setSaving(false);"
    )
    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/VoicemailView.tsx', patch_vm)

# 3. AudioView.tsx
def patch_audio(c):
    if "import { useToast } from './ToastProvider';" not in c:
        c = "import { useToast } from './ToastProvider';\n" + c
    c = c.replace(
        "export const AudioView: React.FC<AudioViewProps> = ({ token }) => {",
        "export const AudioView: React.FC<AudioViewProps> = ({ token }) => {\n  const { showSuccessModal, showErrorModal } = useToast();"
    )
    old_audio_succ = "setShowModal(false);\n      setSelectedFile(null);\n      loadData();"
    new_audio_succ = """setShowModal(false);
      showSuccessModal('Audio File Uploaded', `Audio prompt "${selectedFile?.name}" has been uploaded.`);
      setSelectedFile(null);
      loadData();"""
    c = c.replace(old_audio_succ, new_audio_succ)

    old_audio_err = "} catch (e: any) {\n      alert('Upload failed: ' + e.message);"
    new_audio_err = "} catch (e: any) {\n      const msg = typeof e === 'string' ? e : e.message || JSON.stringify(e);\n      showErrorModal('Upload Failed', msg);"
    c = c.replace(old_audio_err, new_audio_err)
    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/AudioView.tsx', patch_audio)

# 4. QueuesView.tsx
def patch_queues(c):
    if "import { useToast } from './ToastProvider';" not in c:
        c = "import { useToast } from './ToastProvider';\n" + c
    c = c.replace(
        "export const QueuesView: React.FC<QueuesViewProps> = ({ token }) => {",
        "export const QueuesView: React.FC<QueuesViewProps> = ({ token }) => {\n  const { showSuccessModal, showErrorModal } = useToast();"
    )
    old_q_succ = "setShowModal(false);\n      loadData();"
    new_q_succ = """setShowModal(false);
      showSuccessModal('Call Queue Saved', `Queue "${name}" (ext/${queueNumber}) has been saved.`);
      loadData();"""
    c = c.replace(old_q_succ, new_q_succ)

    old_q_del = "await apiService.deleteQueue(token, queueId);\n      loadData();"
    new_q_del = """await apiService.deleteQueue(token, queueId);
      showSuccessModal('Queue Deleted', 'Call queue has been removed.');
      loadData();"""
    c = c.replace(old_q_del, new_q_del)

    old_q_err = "} catch (e: any) {\n      alert('Error saving queue: ' + e.message);"
    new_q_err = "} catch (e: any) {\n      const msg = typeof e === 'string' ? e : e.message || JSON.stringify(e);\n      showErrorModal('Failed to Save Queue', msg);"
    c = c.replace(old_q_err, new_q_err)
    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/QueuesView.tsx', patch_queues)

# 5. HuntGroupsView.tsx
def patch_hunt(c):
    if "import { useToast } from './ToastProvider';" not in c:
        c = "import { useToast } from './ToastProvider';\n" + c
    c = c.replace(
        "export const HuntGroupsView: React.FC<HuntGroupsViewProps> = ({ token }) => {",
        "export const HuntGroupsView: React.FC<HuntGroupsViewProps> = ({ token }) => {\n  const { showSuccessModal, showErrorModal } = useToast();"
    )
    old_h_succ = "setShowModal(false);\n      loadData();"
    new_h_succ = """setShowModal(false);
      showSuccessModal('Hunt Group Created', `Hunt group "${name}" (ext/${extNumber}) configured.`);
      loadData();"""
    c = c.replace(old_h_succ, new_h_succ)

    old_h_err = "} catch (e: any) {\n      alert('Error creating hunt group: ' + e.message);"
    new_h_err = "} catch (e: any) {\n      const msg = typeof e === 'string' ? e : e.message || JSON.stringify(e);\n      showErrorModal('Failed to Create Hunt Group', msg);"
    c = c.replace(old_h_err, new_h_err)
    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/HuntGroupsView.tsx', patch_hunt)

# 6. RoutingView.tsx
def patch_routing(c):
    if "import { useToast } from './ToastProvider';" not in c:
        c = "import { useToast } from './ToastProvider';\n" + c
    c = c.replace(
        "export const RoutingView: React.FC<RoutingViewProps> = ({ token }) => {",
        "export const RoutingView: React.FC<RoutingViewProps> = ({ token }) => {\n  const { showSuccessModal, showErrorModal } = useToast();"
    )
    old_r_succ = "setShowModal(false);\n      loadData();"
    new_r_succ = """setShowModal(false);
      showSuccessModal('Route Created', `Routing rule "${name}" has been created.`);
      loadData();"""
    c = c.replace(old_r_succ, new_r_succ)

    old_r_del = "await apiService.deleteRoute(token, routeId);\n      loadData();"
    new_r_del = """await apiService.deleteRoute(token, routeId);
      showSuccessModal('Route Deleted', 'Routing rule removed.');
      loadData();"""
    c = c.replace(old_r_del, new_r_del)

    old_r_err = "} catch (e: any) {\n      alert('Error creating route: ' + e.message);"
    new_r_err = "} catch (e: any) {\n      const msg = typeof e === 'string' ? e : e.message || JSON.stringify(e);\n      showErrorModal('Failed to Create Route', msg);"
    c = c.replace(old_r_err, new_r_err)
    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/RoutingView.tsx', patch_routing)

# 7. DidsView.tsx
def patch_dids(c):
    if "import { useToast } from './ToastProvider';" not in c:
        c = "import { useToast } from './ToastProvider';\n" + c
    c = c.replace(
        "export const DidsView: React.FC<DidsViewProps> = ({ token }) => {",
        "export const DidsView: React.FC<DidsViewProps> = ({ token }) => {\n  const { showSuccessModal, showErrorModal } = useToast();"
    )
    c = c.replace(
        "setShowAddModal(false);\n      setDidNumber('');\n      loadData();",
        "setShowAddModal(false);\n      setDidNumber('');\n      showSuccessModal('DID Added', `Telephone number ${didNumber} added to inventory.`);\n      loadData();"
    )
    c = c.replace(
        "setShowAssignModal(false);\n      loadData();",
        "setShowAssignModal(false);\n      showSuccessModal('DID Assigned', 'DID number allocated to tenant successfully.');\n      loadData();"
    )
    c = c.replace(
        "await apiService.unassignDid(token, didId);\n      loadData();",
        "await apiService.unassignDid(token, didId);\n      showSuccessModal('DID Unassigned', 'DID returned to unallocated pool.');\n      loadData();"
    )
    c = c.replace(
        "} catch (e: any) {\n      alert('Error: ' + e.message);",
        "} catch (e: any) {\n      const msg = typeof e === 'string' ? e : e.message || JSON.stringify(e);\n      showErrorModal('DID Action Failed', msg);"
    )
    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/DidsView.tsx', patch_dids)

# 8. TrunksView.tsx
def patch_trunks(c):
    if "import { useToast } from './ToastProvider';" not in c:
        c = "import { useToast } from './ToastProvider';\n" + c
    c = c.replace(
        "export const TrunksView: React.FC<TrunksViewProps> = ({ token }) => {",
        "export const TrunksView: React.FC<TrunksViewProps> = ({ token }) => {\n  const { showSuccessModal, showErrorModal } = useToast();"
    )
    c = c.replace(
        "setShowModal(false);\n      loadData();",
        "setShowModal(false);\n      showSuccessModal('SIP Trunk Saved', `Trunk \"${name}\" (${host}:${port}) registered.`);\n      loadData();"
    )
    c = c.replace(
        "} catch (e: any) {\n      alert('Error creating trunk: ' + e.message);",
        "} catch (e: any) {\n      const msg = typeof e === 'string' ? e : e.message || JSON.stringify(e);\n      showErrorModal('Failed to Save Trunk', msg);"
    )
    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/TrunksView.tsx', patch_trunks)

# 9. IvrView.tsx
def patch_ivr(c):
    c = c.replace(
        "const { toastError } = useToast();",
        "const { showSuccessModal, showErrorModal, toastError } = useToast();"
    )
    # IVR creation
    old_ivr_create = "setShowCreateModal(false);\n      setNewName('');\n      setNewDesc('');\n      loadData();"
    new_ivr_create = """setShowCreateModal(false);
      showSuccessModal('IVR Flow Created', `IVR menu "${newName}" has been created.`);
      setNewName('');
      setNewDesc('');
      loadData();"""
    c = c.replace(old_ivr_create, new_ivr_create)

    # Node save
    old_node_save = "await apiService.upsertIvrNode(token, activeIvr.id, payload);\n      await loadNodes(activeIvr.id);\n      setShowNodeModal(false);"
    new_node_save = """await apiService.upsertIvrNode(token, activeIvr.id, payload);
      await loadNodes(activeIvr.id);
      showSuccessModal('DTMF Action Saved', `Action for Key ${nodeKey} has been configured.`);
      setShowNodeModal(false);"""
    c = c.replace(old_node_save, new_node_save)

    # IVR delete
    old_ivr_del = "await apiService.deleteIvr(token, activeIvr.id);\n      setActiveIvr(null);\n      setNodes([]);\n      loadData();"
    new_ivr_del = """await apiService.deleteIvr(token, activeIvr.id);
      showSuccessModal('IVR Flow Deleted', 'The IVR menu has been deleted.');
      setActiveIvr(null);
      setNodes([]);
      loadData();"""
    c = c.replace(old_ivr_del, new_ivr_del)

    return c

update_file('c:/PROJECTS/Fullstack PBX/frontend/src/components/IvrView.tsx', patch_ivr)

print("All components patched with acknowledgement modals!")
