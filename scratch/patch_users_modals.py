with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/UsersView.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add useToast import
if "import { useToast } from './ToastProvider';" not in text:
    text = "import { useToast } from './ToastProvider';\n" + text

# Add hook call in component body
old_body_start = "export const UsersView: React.FC<UsersViewProps> = ({ token, currentUser, tenantScoped = false }) => {"
new_body_start = """export const UsersView: React.FC<UsersViewProps> = ({ token, currentUser, tenantScoped = false }) => {
  const { showSuccessModal, showErrorModal } = useToast();"""

text = text.replace(old_body_start, new_body_start)

# Update handleCreate
old_create = """      setShowModal(false);
      setUsername('');
      setEmail('');
      setPassword('');
      setFirstName('');
      setLastName('');
      setSelectedModules(['extensions', 'reports']);
      fetchData();
    } catch (err: any) {
      setError(err.message);
    } finally {"""

new_create = """      setShowModal(false);
      showSuccessModal(
        'User Account Provisioned',
        `User account "${username}" (${email}) has been successfully created with role ${role}.`
      );
      setUsername('');
      setEmail('');
      setPassword('');
      setFirstName('');
      setLastName('');
      setSelectedModules(['extensions', 'reports']);
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
      showErrorModal('Failed to Create User', msg);
    } finally {"""

text = text.replace(old_create, new_create)

# Update handleSavePermissions
old_save_perm = """      await apiService.updateUserPermissions(token, permModalUser.id, editModules);
      setPermModalUser(null);
      fetchData();
    } catch (err: any) {
      setError(err.message);
    } finally {"""

new_save_perm = """      await apiService.updateUserPermissions(token, permModalUser.id, editModules);
      showSuccessModal(
        'Sub-Admin Permissions Saved',
        `Module permissions for ${permModalUser.username} have been updated successfully.`
      );
      setPermModalUser(null);
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
      showErrorModal('Failed to Update Permissions', msg);
    } finally {"""

text = text.replace(old_save_perm, new_save_perm)

# Update handleDelete
old_del = """    try {
      await apiService.deleteUser(token, id);
      fetchData();
    } catch (err: any) {
      setError(err.message);
    }"""

new_del = """    try {
      await apiService.deleteUser(token, id);
      showSuccessModal('User Deactivated', 'The user account has been deactivated successfully.');
      fetchData();
    } catch (err: any) {
      const msg = typeof err === 'string' ? err : err.message || JSON.stringify(err);
      setError(msg);
      showErrorModal('Failed to Deactivate User', msg);
    }"""

text = text.replace(old_del, new_del)

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/UsersView.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated UsersView.tsx with acknowledgement modals.")
