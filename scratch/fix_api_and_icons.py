import os

# 1. ADD deleteUser & testXmlCurl TO API.TS
api_path = r"C:\PROJECTS\Fullstack PBX\frontend\src\services\api.ts"
with open(api_path, "r", encoding="utf-8") as f:
    c = f.read()

extra_methods = '''
  async deleteUser(token: string, userId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`, {
      method: 'DELETE',
      headers: getHeaders(token),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete user');
    }
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
'''

c = c.replace("};", extra_methods + "\n};")
with open(api_path, "w", encoding="utf-8") as f:
    f.write(c)

# 2. CLEAN UNUSED ICONS IN EXTENSIONSVIEW & IVRVIEW
ext_path = r"C:\PROJECTS\Fullstack PBX\frontend\src\components\ExtensionsView.tsx"
with open(ext_path, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("import { Phone, Plus, RefreshCw, KeyRound, Settings, Search, CheckCircle2 } from 'lucide-react';", "import { Phone, Plus, KeyRound, Settings, Search } from 'lucide-react';")
with open(ext_path, "w", encoding="utf-8") as f:
    f.write(c)

ivr_path = r"C:\PROJECTS\Fullstack PBX\frontend\src\components\IvrView.tsx"
with open(ivr_path, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("import { GitBranch, Plus, Mic, Volume2 } from 'lucide-react';", "import { GitBranch, Plus, Volume2 } from 'lucide-react';")
with open(ivr_path, "w", encoding="utf-8") as f:
    f.write(c)

print("api.ts and icon imports cleaned.")
