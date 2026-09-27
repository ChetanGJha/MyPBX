import os, re

# 1. Update backend users.py
backend_users_path = r'c:\PROJECTS\Fullstack PBX\PBX\src\api\v1\users.py'
with open(backend_users_path, 'r', encoding='utf-8') as f:
    b_content = f.read()

# Replace the list_users function signature and target_tenant resolution
old_list_users = """@router.get("", response_model=List[UserResponse])
async def list_users(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    \"\"\"
    List users. Super Admins can list all or filter by tenant.
    Tenant Admins only see users within their own tenant.
    \"\"\"
    target_tenant = tenant_id

    if current_user.role != "SUPER_ADMIN":
        target_tenant = current_user.tenant_id
        if not target_tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User is not assigned to a tenant."
            )"""

new_list_users = """@router.get("", response_model=List[UserResponse])
async def list_users(
    tenant_id: Optional[str] = Query(None, description="Optional tenant UUID"),
    current_user: CurrentUser = Depends(get_current_user)
):
    \"\"\"
    List users. Super Admins can list all or filter by tenant.
    Tenant Admins only see users within their own tenant.
    \"\"\"
    target_tenant = None
    if tenant_id and str(tenant_id).lower() not in ("undefined", "null", "", "none"):
        try:
            target_tenant = str(UUID(str(tenant_id)))
        except (ValueError, TypeError):
            target_tenant = None

    if current_user.role != "SUPER_ADMIN":
        target_tenant = current_user.tenant_id
        if not target_tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User is not assigned to a tenant."
            )"""

if "tenant_id: Optional[UUID] = None" in b_content:
    b_content = b_content.replace(old_list_users, new_list_users)
    with open(backend_users_path, 'w', encoding='utf-8') as f:
        f.write(b_content)
    print("Updated backend users.py list_users")
else:
    print("backend users.py already updated or signature differs")

# 2. Update frontend api.ts getUsers
api_path = r'c:\PROJECTS\Fullstack PBX\frontend\src\services\api.ts'
with open(api_path, 'r', encoding='utf-8') as f:
    api_content = f.read()

old_get_users = """  async getUsers(token: string, tenantId?: string): Promise<User[]> {
    const url = tenantId ? `${API_BASE_URL}/api/v1/users?tenant_id=${tenantId}` : `${API_BASE_URL}/api/v1/users`;
    const res = await fetch(url, { headers: getHeaders(token) });
    if (!res.ok) throw new Error('Failed to fetch users');
    return res.json();
  },"""

new_get_users = """  async getUsers(token: string, tenantId?: string): Promise<User[]> {
    const hasValidTenant = tenantId && tenantId !== 'undefined' && tenantId !== 'null' && tenantId.trim().length > 0;
    const url = hasValidTenant ? `${API_BASE_URL}/api/v1/users?tenant_id=${tenantId}` : `${API_BASE_URL}/api/v1/users`;
    const res = await fetch(url, { headers: getHeaders(token) });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(parseErrorDetail(err, 'Failed to fetch users'));
    }
    return res.json();
  },"""

if "if (!res.ok) throw new Error('Failed to fetch users');" in api_content:
    api_content = api_content.replace(old_get_users, new_get_users)
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(api_content)
    print("Updated frontend api.ts getUsers")

# 3. Update frontend UsersView.tsx
users_view_path = r'c:\PROJECTS\Fullstack PBX\frontend\src\components\UsersView.tsx'
with open(users_view_path, 'r', encoding='utf-8') as f:
    uv_content = f.read()

old_fetch_data = """      const tenantFilter = tenantScoped && currentUser?.tenant_id ? currentUser.tenant_id : undefined;
      const [uList, tList] = await Promise.all([
        apiService.getUsers(token, tenantFilter),
        currentUser?.role === 'SUPER_ADMIN' ? apiService.getTenants(token) : Promise.resolve([]),
      ]);
      setUsersList(uList);
      setTenants(tList);
      if (tenantScoped && currentUser?.tenant_id) {
        setTenantId(currentUser.tenant_id);
      } else if (tList.length > 0 && !tenantId) {
        setTenantId(tList[0].id);
      }"""

new_fetch_data = """      const tenantFilter = (tenantScoped && currentUser?.tenant_id && currentUser.tenant_id !== 'undefined' && currentUser.tenant_id !== 'null')
        ? currentUser.tenant_id
        : undefined;
      const [uRes, tRes] = await Promise.allSettled([
        apiService.getUsers(token, tenantFilter),
        currentUser?.role === 'SUPER_ADMIN' ? apiService.getTenants(token) : Promise.resolve([]),
      ]);
      if (uRes.status === 'fulfilled') {
        setUsersList(uRes.value);
      } else {
        setError(uRes.reason?.message || 'Failed to fetch users');
      }
      if (tRes.status === 'fulfilled') {
        setTenants(tRes.value);
        if (tenantScoped && currentUser?.tenant_id) {
          setTenantId(currentUser.tenant_id);
        } else if (tRes.value.length > 0 && !tenantId) {
          setTenantId(tRes.value[0].id);
        }
      }"""

if "const [uList, tList] = await Promise.all([" in uv_content:
    uv_content = uv_content.replace(old_fetch_data, new_fetch_data)
    with open(users_view_path, 'w', encoding='utf-8') as f:
        f.write(uv_content)
    print("Updated UsersView.tsx fetchData")
