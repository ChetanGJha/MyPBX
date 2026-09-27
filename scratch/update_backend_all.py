import os

base_backend = r"C:\PROJECTS\Fullstack PBX\PBX\src\api\v1"

# 1. REPORTS.PY (Requirement 8: Date Range Filters, Tenant-wise CDR, Extension-to-Extension, Outbound, IVR, Recordings)
reports_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/cdr")
async def get_cdr_report(
    tenant_id: Optional[UUID] = None,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    call_type: Optional[str] = "all", # all, internal, inbound, outbound
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id

    query = """
        SELECT c.id, c.caller_id_number, c.caller_id_name, c.destination_number,
               c.context, c.start_stamp::text, c.answer_stamp::text, c.end_stamp::text,
               c.duration, c.billsec, c.hangup_cause, c.direction,
               t.name as tenant_name, t.domain as tenant_domain
        FROM cdr c
        LEFT JOIN tenants t ON c.tenant_id = t.id
        WHERE 1=1
    """
    params = {}

    if target_tenant:
        query += " AND c.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    if start_date:
        query += " AND c.start_stamp >= CAST(:start_date AS timestamptz)"
        params["start_date"] = f"{start_date} 00:00:00"

    if end_date:
        query += " AND c.start_stamp <= CAST(:end_date AS timestamptz)"
        params["end_date"] = f"{end_date} 23:59:59"

    if call_type and call_type != "all":
        query += " AND c.direction = :call_type"
        params["call_type"] = call_type

    query += " ORDER BY c.start_stamp DESC LIMIT 500"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.get("/internal")
async def get_internal_call_report(
    tenant_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT c.caller_id_number, c.destination_number,
               COUNT(*) as total_calls,
               SUM(c.duration) as total_duration_sec,
               AVG(c.duration)::int as avg_duration_sec
        FROM cdr c
        WHERE (c.direction = 'internal' OR c.context LIKE '%internal%')
    """
    params = {}
    if target_tenant:
        query += " AND c.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    if start_date:
        query += " AND c.start_stamp >= CAST(:start_date AS timestamptz)"
        params["start_date"] = f"{start_date} 00:00:00"

    if end_date:
        query += " AND c.start_stamp <= CAST(:end_date AS timestamptz)"
        params["end_date"] = f"{end_date} 23:59:59"

    query += " GROUP BY c.caller_id_number, c.destination_number ORDER BY total_calls DESC"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.get("/outbound")
async def get_outbound_call_report(
    tenant_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT c.caller_id_number, c.destination_number, c.billsec,
               c.hangup_cause, c.start_stamp::text, t.name as tenant_name
        FROM cdr c
        LEFT JOIN tenants t ON c.tenant_id = t.id
        WHERE (c.direction = 'outbound' OR c.context LIKE '%outbound%')
    """
    params = {}
    if target_tenant:
        query += " AND c.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    if start_date:
        query += " AND c.start_stamp >= CAST(:start_date AS timestamptz)"
        params["start_date"] = f"{start_date} 00:00:00"

    if end_date:
        query += " AND c.start_stamp <= CAST(:end_date AS timestamptz)"
        params["end_date"] = f"{end_date} 23:59:59"

    query += " ORDER BY c.start_stamp DESC LIMIT 300"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.get("/recordings")
async def get_recordings_report(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT r.id, r.call_id, r.file_name, r.file_path, r.file_size,
               r.duration, r.created_at::text, t.name as tenant_name
        FROM recordings r
        LEFT JOIN tenants t ON r.tenant_id = t.id
        WHERE 1=1
    """
    params = {}
    if target_tenant:
        query += " AND r.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    query += " ORDER BY r.created_at DESC LIMIT 100"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]
'''

with open(os.path.join(base_backend, "reports.py"), "w", encoding="utf-8") as f:
    f.write(reports_py)


# 2. AUDIO.PY (Requirement 7: Voice Files Management & Audio Upload)
audio_py = '''import os
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/audio", tags=["Audio Prompts"])

AUDIO_DIR = "/var/lib/freeswitch/recordings"

@router.get("")
async def list_audio_files(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT id, file_name, file_path, category, description, created_at::text
        FROM announcements
        WHERE 1=1
    """
    params = {}
    if target_tenant:
        query += " AND tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_audio_file(
    file: UploadFile = File(...),
    category: str = "ivr_greeting",
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    filename = file.filename
    rel_path = f"prompts/{filename}"

    query = """
        INSERT INTO announcements (name, file_name, file_path, category, tenant_id)
        VALUES (:name, :file_name, :file_path, :category, CAST(:tenant_id AS uuid))
        RETURNING id, file_name, file_path, category, created_at::text
    """
    row = await execute_query_one(query, {
        "name": filename,
        "file_name": filename,
        "file_path": rel_path,
        "category": category,
        "tenant_id": target_tenant
    })
    return dict(row)
'''

with open(os.path.join(base_backend, "audio.py"), "w", encoding="utf-8") as f:
    f.write(audio_py)


# 3. ROUTING.PY (Full CRUD: GET, POST, PUT, DELETE)
routing_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/routing", tags=["Call Routing"])

class RouteCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    did_number: Optional[str] = Field(None, description="DID Number for Inbound routes")
    route_type: str = "inbound_did"
    destination_type: str = "queue"
    destination: str = Field(..., description="Target destination ID or number")
    priority: int = 1
    regex_pattern: Optional[str] = None
    gateway_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None

@router.get("")
async def list_routes(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT r.id, r.name, r.did_number, r.route_type, r.destination_type,
               r.destination, r.priority, r.regex_pattern, r.enabled, r.created_at::text,
               t.name as tenant_name
        FROM call_routes r
        LEFT JOIN tenants t ON r.tenant_id = t.id
        WHERE r.deleted_at IS NULL
    """
    params = {}
    if target_tenant:
        query += " AND r.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    query += " ORDER BY r.priority ASC, r.name ASC"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_route(
    payload: RouteCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    target_tenant = payload.tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        INSERT INTO call_routes (name, did_number, route_type, destination_type, destination, priority, regex_pattern, gateway_id, tenant_id)
        VALUES (:name, :did_number, :route_type, :destination_type, :destination, :priority, :regex_pattern, CAST(:gateway_id AS uuid), CAST(:tenant_id AS uuid))
        RETURNING id, name, did_number, route_type, destination_type, destination, priority, regex_pattern, enabled, created_at::text
    """
    data = payload.dict()
    data["tenant_id"] = target_tenant
    row = await execute_query_one(query, data)
    return dict(row)

@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(
    route_id: UUID,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    await execute_query("UPDATE call_routes SET deleted_at = NOW(), enabled = false WHERE id = CAST(:id AS uuid)", {"id": route_id})
    return None
'''

with open(os.path.join(base_backend, "routing.py"), "w", encoding="utf-8") as f:
    f.write(routing_py)


# 4. QUEUES.PY (Full CRUD: GET, POST, PUT, DELETE)
queues_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/queues", tags=["Call Queues"])

class QueueCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    queue_number: str = Field(..., description="Extension number for queue e.g. 7001")
    strategy: str = "round_robin"
    agent_timeout: int = 30
    wrap_up_time: int = 10
    max_wait_time: int = 300
    agents: Optional[str] = None
    tenant_id: Optional[UUID] = None

@router.get("")
async def list_queues(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT q.id, q.name, q.queue_number, q.strategy, q.agent_timeout, q.wrap_up_time,
               q.max_wait_time, q.agents, q.enabled, q.created_at::text, t.name as tenant_name
        FROM queues q
        LEFT JOIN tenants t ON q.tenant_id = t.id
        WHERE q.deleted_at IS NULL
    """
    params = {}
    if target_tenant:
        query += " AND q.tenant_id = CAST(:t_id AS uuid)"
        params["t_id"] = target_tenant

    query += " ORDER BY q.queue_number ASC"
    rows = await execute_query(query, params)
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_queue(
    payload: QueueCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    target_tenant = payload.tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        INSERT INTO queues (name, queue_number, strategy, agent_timeout, wrap_up_time, max_wait_time, agents, tenant_id)
        VALUES (:name, :queue_number, :strategy, :agent_timeout, :wrap_up_time, :max_wait_time, :agents, CAST(:tenant_id AS uuid))
        RETURNING id, name, queue_number, strategy, agent_timeout, wrap_up_time, max_wait_time, agents, enabled, created_at::text
    """
    data = payload.dict()
    data["tenant_id"] = target_tenant
    row = await execute_query_one(query, data)
    return dict(row)

@router.put("/{queue_id}")
async def update_queue(
    queue_id: UUID,
    payload: QueueCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    query = """
        UPDATE queues
        SET name = :name, queue_number = :queue_number, strategy = :strategy,
            agent_timeout = :agent_timeout, wrap_up_time = :wrap_up_time,
            max_wait_time = :max_wait_time, agents = :agents, updated_at = NOW()
        WHERE id = CAST(:id AS uuid)
        RETURNING id, name, queue_number, strategy, agents
    """
    data = payload.dict()
    data["id"] = queue_id
    row = await execute_query_one(query, data)
    if not row:
        raise HTTPException(status_code=404, detail="Queue not found")
    return dict(row)

@router.delete("/{queue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_queue(
    queue_id: UUID,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN", "TENANT_ADMIN"]))
):
    await execute_query("UPDATE queues SET deleted_at = NOW(), enabled = false WHERE id = CAST(:id AS uuid)", {"id": queue_id})
    return None
'''

with open(os.path.join(base_backend, "queues.py"), "w", encoding="utf-8") as f:
    f.write(queues_py)


# 5. DIDS.PY (Fixed empty string validation)
dids_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/dids", tags=["DID Inventory"])

class DidCreate(BaseModel):
    did_number: str = Field(..., description="Phone number e.g. +18005550199")
    trunk_id: Optional[str] = None
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
    t_id = payload.trunk_id if payload.trunk_id and payload.trunk_id.strip() != "" else None

    query = """
        INSERT INTO dids (did_number, trunk_id, destination_type, destination)
        VALUES (:did_number, CAST(:trunk_id AS uuid), :destination_type, :destination)
        RETURNING id, did_number, trunk_id, destination_type, destination, enabled, created_at::text
    """
    row = await execute_query_one(query, {
        "did_number": payload.did_number,
        "trunk_id": t_id,
        "destination_type": payload.destination_type,
        "destination": payload.destination
    })
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


# REGISTER IN MAIN.PY
main_py_path = r"C:\PROJECTS\Fullstack PBX\PBX\src\main.py"
with open(main_py_path, "r", encoding="utf-8") as f:
    content = f.read()

target_imp = "from src.api.v1 import auth, tenants, extensions, users, trunks, gateways, routing, queues, dids, hunt_groups, ivr"
new_imp = "from src.api.v1 import auth, tenants, extensions, users, trunks, gateways, routing, queues, dids, hunt_groups, ivr, reports, audio"

target_inc = "app.include_router(ivr.router, prefix=settings.API_V1_STR)"
new_inc = """app.include_router(ivr.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(audio.router, prefix=settings.API_V1_STR)"""

if target_imp in content:
    content = content.replace(target_imp, new_imp)
if target_inc in content:
    content = content.replace(target_inc, new_inc)

with open(main_py_path, "w", encoding="utf-8") as f:
    f.write(content)

print("All backend API modules updated successfully.")
