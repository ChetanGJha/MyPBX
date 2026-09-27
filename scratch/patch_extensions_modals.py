with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/ExtensionsView.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add useToast import
if "import { useToast } from './ToastProvider';" not in text:
    text = "import { useToast } from './ToastProvider';\n" + text

# Add hook call in component body
old_body_start = "export const ExtensionsView: React.FC<ExtensionsViewProps> = ({ token, user }) => {"
new_body_start = """export const ExtensionsView: React.FC<ExtensionsViewProps> = ({ token, user }) => {
  const { showSuccessModal, showErrorModal } = useToast();"""

text = text.replace(old_body_start, new_body_start)

# Update fetchData error formatting
old_fetch_err = "    } catch (err: any) {\n      setError(err.message);\n    }"
new_fetch_err = """    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
    }"""
text = text.replace(old_fetch_err, new_fetch_err)

# Update handleCreate
old_create = """    try {
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
      setError(err.message);
    } finally {
      setLoading(false);
    }"""

new_create = """    try {
      const cleanEmail = email && email.trim() !== '' ? email.trim() : undefined;
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
        `Extension ext/${extNumber} (${displayName}) has been created and registered in FreeSWITCH.`
      );
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
      showErrorModal('Provisioning Failed', msg);
    } finally {
      setLoading(false);
    }"""
text = text.replace(old_create, new_create)

# Update handleResetPassword
old_reset = """    try {
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
      setError(err.message);
    } finally {
      setLoading(false);
    }"""

new_reset = """    try {
      await apiService.resetExtensionPassword(token, selectedExtId, {
        new_sip_password: newSipPwd || undefined,
        new_voicemail_pin: newVmPin || undefined,
      });
      setShowResetModal(false);
      setSelectedExtId(null);
      setNewSipPwd('');
      setNewVmPin('');
      showSuccessModal(
        'Credentials Updated Successfully',
        `SIP password and voicemail PIN have been updated for extension ext/${selectedExtId}.`
      );
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
      showErrorModal('Password Reset Failed', msg);
    } finally {
      setLoading(false);
    }"""
text = text.replace(old_reset, new_reset)

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/ExtensionsView.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated ExtensionsView.tsx with acknowledgement modals.")
