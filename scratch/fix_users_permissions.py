for path in [
    'c:/PROJECTS/Fullstack PBX/PBX/src/api/v1/users.py',
    'c:/PROJECTS/PBX/src/api/v1/users.py'
]:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Fix delete_user tenant check
    old_del = '''    if current_user.role != "SUPER_ADMIN" and user["tenant_id"] != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete user from another tenant.")'''

    new_del = '''    target_tenant_str = str(user["tenant_id"]) if user.get("tenant_id") else None
    current_tenant_str = str(current_user.tenant_id) if current_user.tenant_id else None
    if current_user.role != "SUPER_ADMIN" and target_tenant_str != current_tenant_str:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete user from another tenant.")'''

    code = code.replace(old_del, new_del)

    # Fix update_user_permissions tenant check & CAST
    old_perm = '''    user = await execute_query_one(
        "SELECT id, tenant_id FROM users WHERE id = :u_id AND deleted_at IS NULL",
        {"u_id": user_id}
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if current_user.role != "SUPER_ADMIN" and user["tenant_id"] != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit user from another tenant.")

    await execute_query(
        "UPDATE users SET allowed_modules = CAST(:modules AS jsonb), updated_at = NOW() WHERE id = :u_id",
        {"u_id": user_id, "modules": json.dumps(payload.allowed_modules)}
    )'''

    new_perm = '''    user = await execute_query_one(
        "SELECT id, tenant_id FROM users WHERE id = CAST(:u_id AS uuid) AND deleted_at IS NULL",
        {"u_id": user_id}
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    target_tenant_str = str(user["tenant_id"]) if user.get("tenant_id") else None
    current_tenant_str = str(current_user.tenant_id) if current_user.tenant_id else None
    if current_user.role != "SUPER_ADMIN" and target_tenant_str != current_tenant_str:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit user from another tenant.")

    await execute_query(
        "UPDATE users SET allowed_modules = CAST(:modules AS jsonb), updated_at = NOW() WHERE id = CAST(:u_id AS uuid)",
        {"u_id": user_id, "modules": json.dumps(payload.allowed_modules)}
    )'''

    code = code.replace(old_perm, new_perm)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"Patched {path}")

print("Both users.py patched successfully!")
