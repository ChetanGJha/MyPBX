with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/TenantsView.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

if "import { useToast } from './ToastProvider';" not in text:
    text = "import { useToast } from './ToastProvider';\n" + text

old_body_start = "export const TenantsView: React.FC<TenantsViewProps> = ({ token }) => {"
new_body_start = """export const TenantsView: React.FC<TenantsViewProps> = ({ token }) => {
  const { showSuccessModal, showErrorModal } = useToast();"""
text = text.replace(old_body_start, new_body_start)

old_create = """      await apiService.createTenant(token, { name, domain, sip_domain: sipDomain });
      setShowModal(false);
      setName('');
      setDomain('');
      setSipDomain('');
      fetchTenants();
    } catch (err: any) {
      setModalError(err.message);
    }"""

new_create = """      await apiService.createTenant(token, { name, domain, sip_domain: sipDomain });
      setShowModal(false);
      showSuccessModal(
        'Tenant Domain Created',
        `Tenant "${name}" (${domain}) has been registered with SIP domain ${sipDomain || domain}.`
      );
      setName('');
      setDomain('');
      setSipDomain('');
      fetchTenants();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setModalError(msg);
      showErrorModal('Failed to Create Tenant', msg);
    }"""
text = text.replace(old_create, new_create)

old_del = """    try {
      await apiService.deleteTenant(token, id);
      fetchTenants();
    } catch (err: any) {
      setError(err.message);
    }"""

new_del = """    try {
      await apiService.deleteTenant(token, id);
      showSuccessModal('Tenant Deleted', 'Tenant domain has been deleted successfully.');
      fetchTenants();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
      showErrorModal('Failed to Delete Tenant', msg);
    }"""
text = text.replace(old_del, new_del)

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/TenantsView.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated TenantsView.tsx with acknowledgement modals.")
