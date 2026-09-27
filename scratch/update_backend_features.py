import os

base_backend = r"C:\PROJECTS\Fullstack PBX\PBX\src\api\v1"

# 1. TENANTS.PY (With safeguards and disable/enable endpoints)
tenants_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/tenants", tags=["Tenants"])

class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    domain: str = Field(..., min_length=3, max_length=100)
    sip_domain: Optional[str] = None
    timezone: str = "UTC"
    max_extensions: int = 100
    max_concurrent_calls: int = 20

class TenantStatusUpdate(BaseModel):
    enabled: bool

@router.get("")
async def list_tenants(current_user: CurrentUser = Depends(get_current_user)):
    query = """
        SELECT id, name, domain, sip_domain, timezone, enabled,
               max_extensions, max_concurrent_calls, created_at::text
        FROM tenants
        WHERE deleted_at IS NULL
        ORDER BY name ASC
    """
    rows = await execute_query(query)
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    clean_domain = payload.domain.strip().lower()
    sip_dom = payload.sip_domain.strip().lower() if payload.sip_domain else clean_domain

    # Recycler soft-deleted
    await execute_query("DELETE FROM tenants WHERE domain = :domain AND deleted_at IS NOT NULL", {"domain": clean_domain})

    existing = await execute_query_one("SELECT id FROM tenants WHERE domain = :domain AND deleted_at IS NULL", {"domain": clean_domain})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tenant domain '{clean_domain}' is already active."
        )

    query = """
        INSERT INTO tenants (name, domain, sip_domain, timezone, max_extensions, max_concurrent_calls)
        VALUES (:name, :domain, :sip_domain, :timezone, :max_extensions, :max_concurrent_calls)
        RETURNING id, name, domain, sip_domain, timezone, enabled, max_extensions, max_concurrent_calls, created_at::text
    """
    data = payload.dict()
    data["domain"] = clean_domain
    data["sip_domain"] = sip_dom
    row = await execute_query_one(query, data)
    return dict(row)

@router.put("/{tenant_id}/status")
async def toggle_tenant_status(
    tenant_id: UUID,
    payload: TenantStatusUpdate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    query = "UPDATE tenants SET enabled = :enabled, updated_at = NOW() WHERE id = CAST(:id AS uuid) RETURNING id, name, enabled"
    row = await execute_query_one(query, {"id": tenant_id, "enabled": payload.enabled})
    if not row:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return dict(row)

@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    # Requirement 2 Safeguard: Check allocated gateways, numbers/DIDs, extensions, IVRs
    ext_count = await execute_query_one("SELECT COUNT(*) as cnt FROM extensions WHERE tenant_id = CAST(:id AS uuid) AND deleted_at IS NULL", {"id": tenant_id})
    did_count = await execute_query_one("SELECT COUNT(*) as cnt FROM dids WHERE tenant_id = CAST(:id AS uuid) AND deleted_at IS NULL", {"id": tenant_id})
    gw_count = await execute_query_one("SELECT COUNT(*) as cnt FROM tenant_gateways WHERE tenant_id = CAST(:id AS uuid)", {"id": tenant_id})
    ivr_count = await execute_query_one("SELECT COUNT(*) as cnt FROM ivr_menus WHERE tenant_id = CAST(:id AS uuid)", {"id": tenant_id})

    allocated = []
    if ext_count and ext_count["cnt"] > 0: allocated.append(f"{ext_count['cnt']} Extension(s)")
    if did_count and did_count["cnt"] > 0: allocated.append(f"{did_count['cnt']} DID Number(s)")
    if gw_count and gw_count["cnt"] > 0: allocated.append(f"{gw_count['cnt']} Gateway/Trunk Assignment(s)")
    if ivr_count and ivr_count["cnt"] > 0: allocated.append(f"{ivr_count['cnt']} IVR Menu(s)")

    if allocated:
        details_str = ", ".join(allocated)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete tenant because it has allocated resources: {details_str}. Please unassign or delete allocated resources first."
        )

    await execute_query("UPDATE tenants SET deleted_at = NOW(), enabled = false WHERE id = CAST(:id AS uuid)", {"id": tenant_id})
    return None
'''

with open(os.path.join(base_backend, "tenants.py"), "w", encoding="utf-8") as f:
    f.write(tenants_py)


# 2. EXTENSIONS.PY (Reset password, Call forwarding, Follow Me, Voicemail-to-Email)
extensions_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/extensions", tags=["Extensions"])

class ExtensionCreate(BaseModel):
    extension_number: str = Field(..., min_length=2, max_length=20)
    display_name: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = None
    sip_password: str = Field(..., min_length=6)
    voicemail_pin: Optional[str] = Field("1234", min_length=4)
    tenant_id: Optional[UUID] = None

class PasswordResetPayload(BaseModel):
    new_sip_password: Optional[str] = Field(None, min_length=6)
    new_voicemail_pin: Optional[str] = Field(None, min_length=4)

class ExtensionSettingsPayload(BaseModel):
    voicemail_email: Optional[str] = None
    voicemail_to_email: bool = False
    follow_me_enabled: bool = False
    follow_me_destination: Optional[str] = None
    follow_me_timeout: int = 20
    call_forward_enabled: bool = False
    call_forward_type: str = "always"  # always, busy, no_answer
    call_forward_destination: Optional[str] = None

@router.get("")
async def list_extensions(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT e.id, e.extension_number, e.display_name, e.email, e.enabled,
               e.voicemail_email, e.voicemail_to_email, e.follow_me_enabled,
               e.follow_me_destination, e.follow_me_timeout, e.call_forward_enabled,
               e.call_forward_type, e.call_forward_destination, e.created_at::text,
               t.name as tenant_name, t.domain as tenant_domain
        FROM extensions e
        LEFT JOIN tenants t ON e.tenant_id = t.id
        WHERE e.deleted_at IS NULL
    """
    params = {}
    if target_tenant:
        query += " AND e.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    query += " ORDER BY e.extension_number ASC"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_extension(
    payload: ExtensionCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    target_tenant = payload.tenant_id if current_user.is_super_admin else current_user.tenant_id
    if not target_tenant:
        raise HTTPException(status_code=400, detail="Tenant ID is required to create extension.")

    query = """
        INSERT INTO extensions (extension_number, display_name, email, sip_password, voicemail_pin, tenant_id)
        VALUES (:extension_number, :display_name, :email, :sip_password, :voicemail_pin, CAST(:tenant_id AS uuid))
        RETURNING id, extension_number, display_name, email, enabled, created_at::text
    """
    data = payload.dict()
    data["tenant_id"] = target_tenant
    row = await execute_query_one(query, data)
    return dict(row)

@router.post("/{extension_id}/reset-password")
async def reset_extension_password(
    extension_id: UUID,
    payload: PasswordResetPayload,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):

    updates = []
    params = {"id": extension_id}
    if payload.new_sip_password:
        updates.append("sip_password = :sip_password")
        params["sip_password"] = payload.new_sip_password
    if payload.new_voicemail_pin:
        updates.append("voicemail_pin = :voicemail_pin")
        params["voicemail_pin"] = payload.new_voicemail_pin

    if not updates:
        raise HTTPException(status_code=400, detail="No new credentials provided.")

    query = f"UPDATE extensions SET {', '.join(updates)}, updated_at = NOW() WHERE id = CAST(:id AS uuid) RETURNING id, extension_number"
    row = await execute_query_one(query, params)
    if not row:
        raise HTTPException(status_code=404, detail="Extension not found")
    return {"status": "success", "message": "Credentials updated successfully"}

@router.put("/{extension_id}/settings")
async def update_extension_settings(
    extension_id: UUID,
    payload: ExtensionSettingsPayload,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    query = """
        UPDATE extensions
        SET voicemail_email = :voicemail_email,
            voicemail_to_email = :voicemail_to_email,
            follow_me_enabled = :follow_me_enabled,
            follow_me_destination = :follow_me_destination,
            follow_me_timeout = :follow_me_timeout,
            call_forward_enabled = :call_forward_enabled,
            call_forward_type = :call_forward_type,
            call_forward_destination = :call_forward_destination,
            updated_at = NOW()
        WHERE id = CAST(:id AS uuid)
        RETURNING id, extension_number, voicemail_email, voicemail_to_email, follow_me_enabled, call_forward_enabled
    """
    data = payload.dict()
    data["id"] = extension_id
    row = await execute_query_one(query, data)
    if not row:
        raise HTTPException(status_code=404, detail="Extension not found")
    return dict(row)
'''

with open(os.path.join(base_backend, "extensions.py"), "w", encoding="utf-8") as f:
    f.write(extensions_py)


# 3. DIDS.PY (DID Inventory & Trunk-wise Tenant Assignment)
dids_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/dids", tags=["DID Inventory"])

class DidCreate(BaseModel):
    did_number: str = Field(..., description="Phone number e.g. +18005550199")
    trunk_id: Optional[UUID] = Field(None, description="Host SIP Trunk / Gateway ID")
    destination_type: str = "extension"
    destination: Optional[str] = None

class DidAssign(BaseModel):
    tenant_id: UUID

@router.get("")
async def list_dids(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    query = """
        SELECT d.id, d.did_number, d.trunk_id, d.tenant_id, d.destination_type,
               d.destination, d.enabled, d.created_at::text,
               t.name as tenant_name, t.domain as tenant_domain,
               s.name as trunk_name, s.host as trunk_host
        FROM dids d
        LEFT JOIN tenants t ON d.tenant_id = t.id
        LEFT JOIN sip_trunks s ON d.trunk_id = s.id
        WHERE d.deleted_at IS NULL
    """
    params = {}
    if not current_user.is_super_admin:
        query += " AND d.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = current_user.tenant_id

    query += " ORDER BY d.did_number ASC"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_did(
    payload: DidCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    query = """
        INSERT INTO dids (did_number, trunk_id, destination_type, destination)
        VALUES (:did_number, CAST(:trunk_id AS uuid), :destination_type, :destination)
        RETURNING id, did_number, trunk_id, destination_type, destination, enabled, created_at::text
    """
    data = payload.dict()
    row = await execute_query_one(query, data)
    return dict(row)

@router.post("/{did_id}/assign")
async def assign_did_to_tenant(
    did_id: UUID,
    payload: DidAssign,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    query = """
        UPDATE dids
        SET tenant_id = CAST(:tenant_id AS uuid), updated_at = NOW()
        WHERE id = CAST(:id AS uuid)
        RETURNING id, did_number, tenant_id
    """
    row = await execute_query_one(query, {"id": did_id, "tenant_id": payload.tenant_id})
    if not row:
        raise HTTPException(status_code=404, detail="DID not found")
    return dict(row)

@router.post("/{did_id}/unassign")
async def unassign_did(
    did_id: UUID,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    query = "UPDATE dids SET tenant_id = NULL, updated_at = NOW() WHERE id = CAST(:id AS uuid) RETURNING id, did_number"
    row = await execute_query_one(query, {"id": did_id})
    return dict(row)
'''

with open(os.path.join(base_backend, "dids.py"), "w", encoding="utf-8") as f:
    f.write(dids_py)


# 4. HUNT_GROUPS.PY (Per Tenant Hunt Groups)
hunt_groups_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/hunt-groups", tags=["Hunt Groups"])

class HuntGroupCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    extension_number: str = Field(..., description="Extension e.g. 8001")
    strategy: str = "sequential"  # sequential, simultaneous, circular
    members: str = Field(..., description="Comma-separated member extension numbers e.g. 1001,1002")
    timeout: int = 20
    tenant_id: Optional[UUID] = None

@router.get("")
async def list_hunt_groups(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT id, name, extension_number, strategy, members, timeout, created_at::text
        FROM hunt_groups
        WHERE deleted_at IS NULL
    """
    params = {}
    if target_tenant:
        query += " AND tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    query += " ORDER BY extension_number ASC"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_hunt_group(
    payload: HuntGroupCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    target_tenant = payload.tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        INSERT INTO hunt_groups (name, extension_number, strategy, members, timeout, tenant_id)
        VALUES (:name, :extension_number, :strategy, :members, :timeout, CAST(:tenant_id AS uuid))
        RETURNING id, name, extension_number, strategy, members, timeout, created_at::text
    """
    data = payload.dict()
    data["tenant_id"] = target_tenant
    row = await execute_query_one(query, data)
    return dict(row)
'''

with open(os.path.join(base_backend, "hunt_groups.py"), "w", encoding="utf-8") as f:
    f.write(hunt_groups_py)


# 5. IVR.PY (IVR Flow Designer & DTMF Mapper)
ivr_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/ivr", tags=["IVR Menus"])

class IvrCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    greeting_audio: Optional[str] = "welcome_prompt.wav"
    direct_extension_dial: bool = True
    timeout: int = 10
    tenant_id: Optional[UUID] = None

class IvrActionCreate(BaseModel):
    digit: str = Field(..., description="DTMF digit 0-9, *, #")
    action_type: str = "extension"  # extension, queue, voicemail, external, hangup
    destination: str

@router.get("")
async def list_ivrs(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT id, name, greeting_audio, direct_extension_dial, timeout, created_at::text
        FROM ivr_menus
        WHERE deleted_at IS NULL
    """
    params = {}
    if target_tenant:
        query += " AND tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    query += " ORDER BY name ASC"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_ivr(
    payload: IvrCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    target_tenant = payload.tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        INSERT INTO ivr_menus (name, greeting_audio, direct_extension_dial, timeout, tenant_id)
        VALUES (:name, :greeting_audio, :direct_extension_dial, :timeout, CAST(:tenant_id AS uuid))
        RETURNING id, name, greeting_audio, direct_extension_dial, timeout, created_at::text
    """
    data = payload.dict()
    data["tenant_id"] = target_tenant
    row = await execute_query_one(query, data)
    return dict(row)
'''

with open(os.path.join(base_backend, "ivr.py"), "w", encoding="utf-8") as f:
    f.write(ivr_py)


# UPDATE MAIN.PY TO REGISTER DIDS, HUNT_GROUPS, IVR
main_py_path = r"C:\PROJECTS\Fullstack PBX\PBX\src\main.py"
with open(main_py_path, "r", encoding="utf-8") as f:
    content = f.read()

target_imp = "from src.api.v1 import auth, tenants, extensions, users, trunks, gateways, routing, queues"
new_imp = "from src.api.v1 import auth, tenants, extensions, users, trunks, gateways, routing, queues, dids, hunt_groups, ivr"

target_inc = "app.include_router(queues.router, prefix=settings.API_V1_STR)"
new_inc = """app.include_router(queues.router, prefix=settings.API_V1_STR)
app.include_router(dids.router, prefix=settings.API_V1_STR)
app.include_router(hunt_groups.router, prefix=settings.API_V1_STR)
app.include_router(ivr.router, prefix=settings.API_V1_STR)"""

if target_imp in content:
    content = content.replace(target_imp, new_imp)
if target_inc in content:
    content = content.replace(target_inc, new_inc)

with open(main_py_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Backend features updated successfully.")
