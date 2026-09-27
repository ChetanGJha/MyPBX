import sys

# 1. Update types.ts
types_path = 'c:/PROJECTS/Fullstack PBX/frontend/src/types.ts'
with open(types_path, 'r', encoding='utf-8') as f:
    types_content = f.read()

if 'allowed_modules?: string[];' not in types_content:
    types_content = types_content.replace(
        'sip_domain?: string;\n}',
        'sip_domain?: string;\n  allowed_modules?: string[];\n}'
    )
    with open(types_path, 'w', encoding='utf-8') as f:
        f.write(types_content)
    print("Updated types.ts with allowed_modules in User interface.")
else:
    print("types.ts already contains allowed_modules.")

# 2. Update api.ts
api_path = 'c:/PROJECTS/Fullstack PBX/frontend/src/services/api.ts'
with open(api_path, 'r', encoding='utf-8') as f:
    api_content = f.read()

new_api_methods = '''
  // ─── Call Forwarding ────────────────────────────────────────────────────────
  async getCallForwardingAll(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/call-forwarding/all`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to fetch call forwarding rules');
    return res.json();
  },

  async getExtensionForwarding(token: string, extensionId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/forwarding`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to fetch extension forwarding');
    return res.json();
  },

  async updateExtensionForwarding(token: string, extensionId: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/forwarding`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update extension forwarding');
    return res.json();
  },

  // ─── Voicemail Boxes ────────────────────────────────────────────────────────
  async getVoicemailBoxesAll(token: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/voicemail-boxes/all`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to fetch voicemail boxes');
    return res.json();
  },

  async getExtensionVoicemail(token: string, extensionId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/voicemail`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to fetch extension voicemail');
    return res.json();
  },

  async updateExtensionVoicemail(token: string, extensionId: string, payload: any) {
    const res = await fetch(`${API_BASE_URL}/api/v1/extensions/${extensionId}/voicemail`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update extension voicemail');
    return res.json();
  },

  // ─── Sub-Admin Permissions ──────────────────────────────────────────────────
  async updateUserPermissions(token: string, userId: string, allowed_modules: string[]) {
    const res = await fetch(`${API_BASE_URL}/api/v1/users/${userId}/permissions`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ allowed_modules }),
    });
    if (!res.ok) throw new Error('Failed to update user permissions');
    return res.json();
  },
'''

if 'getCallForwardingAll' not in api_content:
    # insert before the closing '};'
    last_brace_idx = api_content.rfind('};')
    if last_brace_idx != -1:
        api_content = api_content[:last_brace_idx] + new_api_methods + '\n};\n'
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(api_content)
        print("Updated api.ts with call forwarding, voicemail, and sub-admin permission methods.")
    else:
        print("Could not find closing brace in api.ts!")
else:
    print("api.ts already contains call forwarding methods.")
