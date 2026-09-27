import os

api_path = r'c:\PROJECTS\Fullstack PBX\frontend\src\services\api.ts'
with open(api_path, 'r', encoding='utf-8') as f:
    content = f.read()

changes_needed = False

# 1. Add deleteAudioFile if missing
if 'deleteAudioFile' not in content:
    target = 'async uploadAudioFile(token: string, formData: FormData) {'
    replacement = '''async deleteAudioFile(token: string, fileId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/audio/${fileId}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to delete audio file');
    return true;
  },

  async uploadAudioFile(token: string, formData: FormData) {'''
    content = content.replace(target, replacement)
    changes_needed = True
    print('Added deleteAudioFile to api.ts')

# 2. Add updateHuntGroup and deleteHuntGroup if missing
if 'updateHuntGroup' not in content:
    target = 'async createHuntGroup(token: string, payload: any) {'
    replacement = '''async updateHuntGroup(token: string, id: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/hunt-groups/${id}`, {
      method: 'PUT',
      headers: getHeaders(token),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update hunt group');
    return res.json();
  },

  async deleteHuntGroup(token: string, id: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/hunt-groups/${id}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error('Failed to delete hunt group');
    return true;
  },

  async createHuntGroup(token: string, payload: any) {'''
    content = content.replace(target, replacement)
    changes_needed = True
    print('Added updateHuntGroup and deleteHuntGroup to api.ts')

if changes_needed:
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Saved api.ts')
else:
    print('api.ts already has all methods')
