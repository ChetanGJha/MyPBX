for path in [
    'c:/PROJECTS/Fullstack PBX/PBX/src/api/v1/gateways.py',
    'c:/PROJECTS/PBX/src/api/v1/gateways.py'
]:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    old_list = '''@router.get("")
async def list_gateways(current_user: CurrentUser = Depends(get_current_user)):
    query = """
        SELECT g.id, g.name, g.proxy, g.username, g.realm, g.from_domain, g.codecs,
               g.register, g.enabled, g.created_at::text, t.name as tenant_name
        FROM gateways g
        LEFT JOIN tenants t ON g.tenant_id = t.id
        WHERE g.deleted_at IS NULL
        ORDER BY g.name ASC
    """
    rows = await execute_query(query)
    return [dict(r) for r in rows]'''

    new_list = '''@router.get("")
async def list_gateways(current_user: CurrentUser = Depends(get_current_user)):
    query = """
        SELECT DISTINCT g.id, g.name, g.proxy, g.username, g.realm, g.from_domain, g.codecs,
               g.register, g.enabled, g.created_at::text, t.name as tenant_name
        FROM gateways g
        LEFT JOIN tenants t ON g.tenant_id = t.id
        LEFT JOIN tenant_gateways tg ON g.id = tg.gateway_id
        WHERE g.deleted_at IS NULL
    """
    params = {}
    if not current_user.is_super_admin:
        if current_user.tenant_id:
            query += " AND (g.tenant_id = CAST(:t_id AS uuid) OR tg.tenant_id = CAST(:t_id AS uuid))"
            params["t_id"] = current_user.tenant_id
        else:
            return []

    query += " ORDER BY g.name ASC"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]'''

    if old_list in code:
        code = code.replace(old_list, new_list)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"Updated list_gateways in {path}")
    else:
        print(f"Could not find old list_gateways in {path}")

print("Gateways update done.")
