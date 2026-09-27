import os

hunt_path = r'c:\PROJECTS\Fullstack PBX\PBX\src\api\v1\hunt_groups.py'
with open(hunt_path, 'r', encoding='utf-8') as f:
    content = f.read()

update_code = '''
class HuntGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    extension_number: Optional[str] = None
    strategy: Optional[str] = None
    members: Optional[str] = None
    timeout: Optional[int] = None

@router.put("/{hunt_group_id}")
async def update_hunt_group(
    hunt_group_id: UUID,
    payload: HuntGroupUpdate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    existing = await execute_query_one("SELECT * FROM hunt_groups WHERE id = :id AND deleted_at IS NULL", {"id": hunt_group_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Hunt group not found")
    if not current_user.is_super_admin and str(existing.get("tenant_id")) != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    query = """
        UPDATE hunt_groups
        SET name = COALESCE(:name, name),
            extension_number = COALESCE(:extension_number, extension_number),
            strategy = COALESCE(:strategy, strategy),
            members = COALESCE(:members, members),
            timeout = COALESCE(:timeout, timeout),
            updated_at = NOW()
        WHERE id = :id
        RETURNING id, name, extension_number, strategy, members, timeout, created_at::text
    """
    data = payload.dict(exclude_unset=True)
    data["id"] = hunt_group_id
    for k in ["name", "extension_number", "strategy", "members", "timeout"]:
        if k not in data:
            data[k] = None
    row = await execute_query_one(query, data)
    return dict(row)

@router.delete("/{hunt_group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hunt_group(
    hunt_group_id: UUID,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    existing = await execute_query_one("SELECT * FROM hunt_groups WHERE id = :id AND deleted_at IS NULL", {"id": hunt_group_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Hunt group not found")
    if not current_user.is_super_admin and str(existing.get("tenant_id")) != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await execute_query("UPDATE hunt_groups SET deleted_at = NOW() WHERE id = :id", {"id": hunt_group_id})
'''

if 'update_hunt_group' not in content:
    with open(hunt_path, 'a', encoding='utf-8') as f:
        f.write('\n' + update_code)
    print('Added update/delete endpoints to hunt_groups.py')
else:
    print('hunt_groups.py already has update/delete endpoints')
