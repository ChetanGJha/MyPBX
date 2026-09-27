with open('c:/PROJECTS/Fullstack PBX/frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    c = f.read()

# Add dids and gateways state
old_state = '''  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [extensions, setExtensions] = useState<Extension[]>([]);'''

new_state = '''  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [extensions, setExtensions] = useState<Extension[]>([]);
  const [dids, setDids] = useState<any[]>([]);
  const [gateways, setGateways] = useState<any[]>([]);'''

c = c.replace(old_state, new_state)

# Update data fetch
old_fetch = '''  // Fetch counts when token changes
  useEffect(() => {
    if (token) {
      apiService.getTenants(token).then(setTenants).catch(() => {});
      apiService.getExtensions(token).then(setExtensions).catch(() => {});
    }
  }, [token]);'''

new_fetch = '''  // Fetch counts when token changes
  useEffect(() => {
    if (token) {
      if (user?.role === 'SUPER_ADMIN') {
        apiService.getTenants(token).then(setTenants).catch(() => {});
      }
      apiService.getExtensions(token).then(setExtensions).catch(() => {});
      apiService.getDids(token).then(setDids).catch(() => {});
      apiService.getGateways(token).then(setGateways).catch(() => {});
    }
  }, [token, user?.role]);'''

c = c.replace(old_fetch, new_fetch)

# Update DashboardView call
old_dash = '''            {activeTab === 'dashboard' && (
              <DashboardView
                status={status}
                user={user}
                tenantCount={tenants.length}
                extensionCount={extensions.length}
                setActiveTab={handleSetTab}
              />
            )}'''

new_dash = '''            {activeTab === 'dashboard' && (
              <DashboardView
                status={status}
                user={user}
                tenantCount={tenants.length}
                extensionCount={extensions.length}
                didCount={dids.length}
                gatewayCount={gateways.length}
                setActiveTab={handleSetTab}
              />
            )}'''

c = c.replace(old_dash, new_dash)

with open('c:/PROJECTS/Fullstack PBX/frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(c)

print("Updated App.tsx with dids & gateways metrics for DashboardView.")
