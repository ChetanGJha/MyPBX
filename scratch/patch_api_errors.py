with open('c:/PROJECTS/Fullstack PBX/frontend/src/services/api.ts', 'r', encoding='utf-8') as f:
    code = f.read()

# Helper function to parse error detail into human-readable string
parser_fn = '''
export function parseErrorDetail(errData: any, fallback: string): string {
  if (!errData) return fallback;
  const detail = errData.detail || errData.message;
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d: any) => {
      const field = d.loc ? d.loc.filter((x: string) => x !== 'body').join('.') : '';
      return field ? `${field}: ${d.msg}` : (d.msg || JSON.stringify(d));
    }).join('; ');
  }
  if (typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  return String(detail);
}
'''

if 'export function parseErrorDetail' not in code:
    code = parser_fn + '\n' + code

# Update createExtension
old_create_ext = '''    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create extension');
    }'''

new_create_ext = '''    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to create extension' }));
      throw new Error(parseErrorDetail(err, 'Failed to create extension'));
    }'''

code = code.replace(old_create_ext, new_create_ext)

# Update resetExtensionPassword
old_reset = '''    if (!res.ok) throw new Error('Failed to reset password');'''
new_reset = '''    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to reset password' }));
      throw new Error(parseErrorDetail(err, 'Failed to reset password'));
    }'''

code = code.replace(old_reset, new_reset)

with open('c:/PROJECTS/Fullstack PBX/frontend/src/services/api.ts', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated api.ts with parseErrorDetail helper.")
