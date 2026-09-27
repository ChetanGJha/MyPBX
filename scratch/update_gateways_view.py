import os

path = r"C:\PROJECTS\Fullstack PBX\frontend\src\components\GatewaysView.tsx"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

old_load = """  const loadData = async () => {
    try {
      setLoading(true);
      const [gData, tData] = await Promise.all([
        apiService.getGateways(token),
        apiService.getTenants(token)
      ]);
      setGateways(gData);
      setTenants(tData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };"""

new_load = """  const loadData = async () => {
    try {
      setLoading(true);
      const [gRes, tRes] = await Promise.allSettled([
        apiService.getGateways(token),
        apiService.getTenants(token)
      ]);
      if (gRes.status === 'fulfilled') setGateways(gRes.value);
      if (tRes.status === 'fulfilled') setTenants(tRes.value);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };"""

if old_load in c:
    c = c.replace(old_load, new_load)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("GatewaysView loadData updated successfully.")
else:
    print("Pattern not found, checking contents...")
