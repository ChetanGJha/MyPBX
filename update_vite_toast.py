import sys, os
sys.stdout.reconfigure(encoding='utf-8')

base_frontend = r"c:\PROJECTS\Fullstack PBX\frontend"

# 1. Update vite.config.ts
vite_config_path = os.path.join(base_frontend, "vite.config.ts")
vite_content = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
"""
with open(vite_config_path, "w", encoding="utf-8") as f:
    f.write(vite_content)
print("Updated vite.config.ts")

# 2. Update ToastProvider.tsx (Fix modal text alignment)
toast_path = os.path.join(base_frontend, "src", "components", "ToastProvider.tsx")
with open(toast_path, "r", encoding="utf-8") as f:
    toast_text = f.read()

# Replace textAlign: 'center' on the message body with 'left'
toast_text_updated = toast_text.replace(
    """            {/* Message Body */}
            <div style={{ padding: '0 28px 24px' }}>
              <div
                style={{
                  fontSize: '13.5px',
                  color: '#334155',
                  lineHeight: '1.6',
                  textAlign: 'center',
                  background: ackModal.type === 'error' ? '#FFF5F5' : '#F8FAFC',
                  border: `1px solid ${ackModal.type === 'error' ? '#FED7D7' : '#E2E8F0'}`,
                  borderRadius: '12px',
                  padding: '14px 18px',
                  wordBreak: 'break-word',
                  fontFamily: ackModal.type === 'error' ? 'monospace' : 'inherit',
                }}
              >
                {ackModal.message}
              </div>
            </div>""",
    """            {/* Message Body */}
            <div style={{ padding: '0 28px 24px' }}>
              <div
                style={{
                  fontSize: '13.5px',
                  color: '#334155',
                  lineHeight: '1.6',
                  textAlign: 'left',
                  background: ackModal.type === 'error' ? '#FFF5F5' : '#F8FAFC',
                  border: `1px solid ${ackModal.type === 'error' ? '#FED7D7' : '#E2E8F0'}`,
                  borderRadius: '12px',
                  padding: '14px 18px',
                  wordBreak: 'break-word',
                  whiteSpace: 'pre-wrap',
                  fontFamily: ackModal.type === 'error' ? 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace' : 'inherit',
                }}
              >
                {ackModal.message}
              </div>
            </div>"""
)

with open(toast_path, "w", encoding="utf-8") as f:
    f.write(toast_text_updated)
print("Updated ToastProvider.tsx")
