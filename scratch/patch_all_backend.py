import os, json, re

print("Starting backend updates for Fullstack PBX...")

# 1. Update auth.py
auth_path = 'c:/PROJECTS/Fullstack PBX/PBX/src/api/v1/auth.py'
with open(auth_path, 'r', encoding='utf-8') as f:
    auth_code = f.read()

# Replace query in login
auth_code = re.sub(
    r'(SELECT u\.id, u\.tenant_id, u\.username, u\.email, u\.password_hash, u\.is_active,\s+u\.first_name, u\.last_name,)\s+(r\.name as role_name)',
    r"\1 COALESCE(u.allowed_modules, '[]'::jsonb) as allowed_modules, \2",
    auth_code
)

# Replace user dict in login
auth_code = auth_code.replace(
    '"sip_domain": user.get("sip_domain")',
    '"sip_domain": user.get("sip_domain"),\n            "allowed_modules": user.get("allowed_modules") or []'
)

# Replace query in /me
auth_code = re.sub(
    r'(SELECT u\.id, u\.tenant_id, u\.username, u\.email, u\.first_name, u\.last_name, u\.is_active,\s+)(u\.created_at, r\.name as role_name)',
    r"\1COALESCE(u.allowed_modules, '[]'::jsonb) as allowed_modules, \2",
    auth_code
)

auth_code = auth_code.replace(
    '"role": user.get("role_name"),',
    '"role": user.get("role_name"),\n        "allowed_modules": user.get("allowed_modules") or [],'
)

with open(auth_path, 'w', encoding='utf-8') as f:
    f.write(auth_code)
print("Updated auth.py successfully.")

# 2. Update users.py
users_path = 'c:/PROJECTS/Fullstack PBX/PBX/src/api/v1/users.py'
with open(users_path, 'r', encoding='utf-8') as f:
    users_code = f.read()

# Add json import if not present
if 'import json' not in users_code:
    users_code = 'import json\n' + users_code

# Update UserCreate
users_code = users_code.replace(
    'role: str = Field("AGENT", description="Role: TENANT_ADMIN, SUPERVISOR, AGENT")',
    'role: str = Field("AGENT", description="Role: TENANT_ADMIN, SUB_ADMIN, SUPERVISOR, AGENT")\n    allowed_modules: Optional[List[str]] = Field(default_factory=list)'
)

# Update UserResponse
users_code = users_code.replace(
    'role: str\n    is_active: bool',
    'role: str\n    allowed_modules: Optional[List[str]] = []\n    is_active: bool'
)

# Update list_users query
users_code = users_code.replace(
    "COALESCE(r.name, 'AGENT') as role,",
    "COALESCE(u.allowed_modules, '[]'::jsonb) as allowed_modules,\n               COALESCE(r.name, 'AGENT') as role,"
)

# Update create_user insert query
old_insert = """            INSERT INTO users (tenant_id, username, email, password_hash, first_name, last_name)
            VALUES (:t_id, :username, :email, :pwd_hash, :fn, :ln)"""

new_insert = """            INSERT INTO users (tenant_id, username, email, password_hash, first_name, last_name, allowed_modules)
            VALUES (:t_id, :username, :email, :pwd_hash, :fn, :ln, CAST(:allowed_modules AS jsonb))"""

users_code = users_code.replace(old_insert, new_insert)

old_params = """"fn": payload.first_name,
                "ln": payload.last_name"""

new_params = """"fn": payload.first_name,
                "ln": payload.last_name,
                "allowed_modules": json.dumps(payload.allowed_modules or [])"""

users_code = users_code.replace(old_params, new_params)

# Update create_user return
old_create_ret = """"role": target_role,
        "is_active": True,"""

new_create_ret = """"role": target_role,
        "allowed_modules": payload.allowed_modules or [],
        "is_active": True,"""

users_code = users_code.replace(old_create_ret, new_create_ret)

# Add Permissions update endpoint
perm_update_endpoint = '''
class UserPermissionsUpdate(BaseModel):
    allowed_modules: List[str] = Field(default_factory=list)

@router.put("/{user_id}/permissions")
async def update_user_permissions(
    user_id: UUID,
    payload: UserPermissionsUpdate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    """
    Update module permissions for a sub-administrator.
    """
    user = await execute_query_one(
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
    )
    return {"status": "success", "user_id": str(user_id), "allowed_modules": payload.allowed_modules}
'''

if 'update_user_permissions' not in users_code:
    users_code += '\n' + perm_update_endpoint

with open(users_path, 'w', encoding='utf-8') as f:
    f.write(users_code)
print("Updated users.py successfully.")

# 3. Update extensions.py with forwarding & voicemail endpoints
ext_path = 'c:/PROJECTS/Fullstack PBX/PBX/src/api/v1/extensions.py'
with open(ext_path, 'r', encoding='utf-8') as f:
    ext_code = f.read()

forwarding_and_vm_code = '''
# ─── CALL FORWARDING & FOLLOW-ME ENDPOINTS ───────────────────────────────────

class CallForwardingUpdate(BaseModel):
    forward_always_enabled: bool = False
    forward_always_destination: Optional[str] = None
    forward_busy_enabled: bool = False
    forward_busy_destination: Optional[str] = None
    forward_no_answer_enabled: bool = False
    forward_no_answer_destination: Optional[str] = None
    forward_no_answer_timeout: int = 20

@router.get("/call-forwarding/all")
async def get_all_call_forwarding(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get call forwarding rules for all extensions in the current tenant.
    """
    tenant_filter = "WHERE e.deleted_at IS NULL"
    params = {}
    if not current_user.is_super_admin:
        if not current_user.tenant_id:
            raise HTTPException(status_code=403, detail="No tenant context")
        tenant_filter += " AND e.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = current_user.tenant_id

    query = f"""
        SELECT e.id as extension_id, e.extension_number, e.display_name,
               COALESCE(cf.forward_always_enabled, false) as forward_always_enabled,
               cf.forward_always_destination,
               COALESCE(cf.forward_busy_enabled, false) as forward_busy_enabled,
               cf.forward_busy_destination,
               COALESCE(cf.forward_no_answer_enabled, false) as forward_no_answer_enabled,
               cf.forward_no_answer_destination,
               COALESCE(cf.forward_no_answer_timeout, 20) as forward_no_answer_timeout,
               cf.updated_at::text as updated_at
        FROM extensions e
        LEFT JOIN call_forwarding cf ON e.id = cf.extension_id
        {tenant_filter}
        ORDER BY e.extension_number ASC
    """
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.get("/{extension_id}/forwarding")
async def get_extension_forwarding(
    extension_id: UUID,
    current_user: CurrentUser = Depends(get_current_user)
):
    row = await execute_query_one(
        "SELECT * FROM call_forwarding WHERE extension_id = :ext_id",
        {"ext_id": extension_id}
    )
    if not row:
        return {
            "extension_id": str(extension_id),
            "forward_always_enabled": False,
            "forward_always_destination": None,
            "forward_busy_enabled": False,
            "forward_busy_destination": None,
            "forward_no_answer_enabled": False,
            "forward_no_answer_destination": None,
            "forward_no_answer_timeout": 20
        }
    return dict(row)

@router.put("/{extension_id}/forwarding")
async def update_extension_forwarding(
    extension_id: UUID,
    payload: CallForwardingUpdate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN", "AGENT"]))
):
    query = """
        INSERT INTO call_forwarding (
            extension_id, forward_always_enabled, forward_always_destination,
            forward_busy_enabled, forward_busy_destination,
            forward_no_answer_enabled, forward_no_answer_destination,
            forward_no_answer_timeout, updated_at
        ) VALUES (
            :ext_id, :fae, :fad, :fbe, :fbd, :fne, :fnd, :fnt, NOW()
        )
        ON CONFLICT (extension_id) DO UPDATE SET
            forward_always_enabled = EXCLUDED.forward_always_enabled,
            forward_always_destination = EXCLUDED.forward_always_destination,
            forward_busy_enabled = EXCLUDED.forward_busy_enabled,
            forward_busy_destination = EXCLUDED.forward_busy_destination,
            forward_no_answer_enabled = EXCLUDED.forward_no_answer_enabled,
            forward_no_answer_destination = EXCLUDED.forward_no_answer_destination,
            forward_no_answer_timeout = EXCLUDED.forward_no_answer_timeout,
            updated_at = NOW()
        RETURNING *
    """
    row = await execute_query_one(query, {
        "ext_id": extension_id,
        "fae": payload.forward_always_enabled,
        "fad": payload.forward_always_destination,
        "fbe": payload.forward_busy_enabled,
        "fbd": payload.forward_busy_destination,
        "fne": payload.forward_no_answer_enabled,
        "fnd": payload.forward_no_answer_destination,
        "fnt": payload.forward_no_answer_timeout,
    })
    return dict(row)

# ─── VOICEMAIL BOXES ENDPOINTS ────────────────────────────────────────────────

class VoicemailBoxUpdate(BaseModel):
    mailbox: Optional[str] = None
    password: Optional[str] = None
    email_notification: bool = True
    email_attach_file: bool = True
    email_address: Optional[str] = None
    delete_after_email: bool = False
    greeting_path: Optional[str] = None

@router.get("/voicemail-boxes/all")
async def get_all_voicemail_boxes(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get voicemail boxes for all extensions in the current tenant.
    """
    tenant_filter = "WHERE e.deleted_at IS NULL"
    params = {}
    if not current_user.is_super_admin:
        if not current_user.tenant_id:
            raise HTTPException(status_code=403, detail="No tenant context")
        tenant_filter += " AND e.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = current_user.tenant_id

    query = f"""
        SELECT e.id as extension_id, e.extension_number, e.display_name, e.email as extension_email,
               vb.id as voicemail_box_id,
               COALESCE(vb.mailbox, e.extension_number) as mailbox,
               COALESCE(vb.email_notification, true) as email_notification,
               COALESCE(vb.email_attach_file, true) as email_attach_file,
               COALESCE(vb.email_address, e.email) as email_address,
               COALESCE(vb.delete_after_email, false) as delete_after_email,
               vb.greeting_path,
               vb.created_at::text as created_at
        FROM extensions e
        LEFT JOIN voicemail_boxes vb ON e.id = vb.extension_id
        {tenant_filter}
        ORDER BY e.extension_number ASC
    """
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.get("/{extension_id}/voicemail")
async def get_extension_voicemail(
    extension_id: UUID,
    current_user: CurrentUser = Depends(get_current_user)
):
    row = await execute_query_one(
        "SELECT * FROM voicemail_boxes WHERE extension_id = :ext_id",
        {"ext_id": extension_id}
    )
    if not row:
        ext = await execute_query_one("SELECT extension_number, email FROM extensions WHERE id = :ext_id", {"ext_id": extension_id})
        mailbox_num = ext["extension_number"] if ext else ""
        return {
            "extension_id": str(extension_id),
            "mailbox": mailbox_num,
            "password": "1234",
            "email_notification": True,
            "email_attach_file": True,
            "email_address": ext.get("email") if ext else None,
            "delete_after_email": False,
            "greeting_path": None
        }
    return dict(row)

@router.put("/{extension_id}/voicemail")
async def update_extension_voicemail(
    extension_id: UUID,
    payload: VoicemailBoxUpdate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN", "AGENT"]))
):
    ext = await execute_query_one("SELECT tenant_id, extension_number, email FROM extensions WHERE id = :ext_id", {"ext_id": extension_id})
    if not ext:
        raise HTTPException(status_code=404, detail="Extension not found")

    tenant_id = ext["tenant_id"]
    mailbox = payload.mailbox or ext["extension_number"]
    email_addr = payload.email_address or ext.get("email")

    query = """
        INSERT INTO voicemail_boxes (
            tenant_id, extension_id, mailbox, password,
            email_notification, email_attach_file, email_address,
            delete_after_email, greeting_path
        ) VALUES (
            :t_id, :ext_id, :mb, :pwd, :en, :ea, :em, :da, :gp
        )
        ON CONFLICT (tenant_id, mailbox) DO UPDATE SET
            password = COALESCE(EXCLUDED.password, voicemail_boxes.password),
            email_notification = EXCLUDED.email_notification,
            email_attach_file = EXCLUDED.email_attach_file,
            email_address = EXCLUDED.email_address,
            delete_after_email = EXCLUDED.delete_after_email,
            greeting_path = EXCLUDED.greeting_path
        RETURNING *
    """
    row = await execute_query_one(query, {
        "t_id": tenant_id,
        "ext_id": extension_id,
        "mb": mailbox,
        "pwd": payload.password or "1234",
        "en": payload.email_notification,
        "ea": payload.email_attach_file,
        "em": email_addr,
        "da": payload.delete_after_email,
        "gp": payload.greeting_path
    })
    return dict(row)
'''

if 'get_all_call_forwarding' not in ext_code:
    ext_code += '\n' + forwarding_and_vm_code

with open(ext_path, 'w', encoding='utf-8') as f:
    f.write(ext_code)
print("Updated extensions.py with call forwarding and voicemail endpoints.")
