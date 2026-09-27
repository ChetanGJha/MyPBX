import os
import json

base_backend = r"C:\PROJECTS\Fullstack PBX\PBX\src\api\v1"
base_frontend = r"C:\PROJECTS\Fullstack PBX\frontend\src"
base_components = r"C:\PROJECTS\Fullstack PBX\frontend\src\components"

os.makedirs(base_backend, exist_ok=True)
os.makedirs(base_components, exist_ok=True)

# 1. TRUNKS.PY
trunks_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/trunks", tags=["SIP Trunks"])

class TrunkCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    host: str = Field(..., description="SIP Proxy or Host IP/Domain")
    port: int = 5060
    transport: str = "UDP"
    username: Optional[str] = None
    password: Optional[str] = None
    realm: Optional[str] = None
    priority: int = 1
    tenant_id: Optional[UUID] = None
    register: bool = True
    srtp: bool = False
    p_asserted_identity: bool = True

@router.get("")
async def list_trunks(current_user: CurrentUser = Depends(get_current_user)):
    query = """
        SELECT id, name, host, port, transport, username, realm, priority,
               tenant_id, register, srtp, enabled, created_at::text
        FROM sip_trunks
        WHERE deleted_at IS NULL
        ORDER BY priority ASC, name ASC
    """
    rows = await execute_query(query)
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_trunk(
    payload: TrunkCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    query = """
        INSERT INTO sip_trunks (name, host, port, transport, username, password, realm, priority, tenant_id, register, srtp)
        VALUES (:name, :host, :port, :transport, :username, :password, :realm, :priority, :tenant_id, :register, :srtp)
        RETURNING id, name, host, port, transport, username, realm, priority, register, srtp, enabled, created_at::text
    """
    row = await execute_query_one(query, payload.dict())
    return dict(row)

@router.delete("/{trunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trunk(
    trunk_id: UUID,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    await execute_query("UPDATE sip_trunks SET deleted_at = NOW(), enabled = false WHERE id = :id", {"id": trunk_id})
    return None
'''

with open(os.path.join(base_backend, "trunks.py"), "w", encoding="utf-8") as f:
    f.write(trunks_py)


# 2. GATEWAYS.PY
gateways_py = '''from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.database import execute_query, execute_query_one
from src.core.permissions import get_current_user, require_roles, CurrentUser

router = APIRouter(prefix="/gateways", tags=["Sofia Gateways"])

class GatewayCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    proxy: str = Field(..., description="Proxy IP/Domain")
    username: Optional[str] = None
    password: Optional[str] = None
    realm: Optional[str] = None
    from_domain: Optional[str] = None
    codecs: str = "PCMU,PCMA,G722"
    tenant_id: Optional[UUID] = None
    register: bool = True
    caller_id_in_from: bool = False

class GatewayAssignmentCreate(BaseModel):
    tenant_id: UUID
    gateway_id: UUID
    direction: str = "inbound_outbound"
    priority: int = 1
    caller_id_policy: str = "tenant_default"
    allow_outbound: bool = True
    accept_inbound: bool = True
    allow_international: bool = False

@router.get("")
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
    return [dict(r) for r in rows]

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_gateway(
    payload: GatewayCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    query = """
        INSERT INTO gateways (name, proxy, username, password, realm, from_domain, codecs, tenant_id, register)
        VALUES (:name, :proxy, :username, :password, :realm, :from_domain, :codecs, :tenant_id, :register)
        RETURNING id, name, proxy, username, realm, from_domain, codecs, register, enabled, created_at::text
    """
    row = await execute_query_one(query, payload.dict())
    return dict(row)

@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_gateway_to_tenant(
    payload: GatewayAssignmentCreate,
    current_user: CurrentUser = Depends(require_roles(["SUPER_ADMIN"]))
):
    query = """
        INSERT INTO tenant_gateways (tenant_id, gateway_id, direction, priority, caller_id_policy, allow_outbound, accept_inbound, allow_international)
        VALUES (:tenant_id, :gateway_id, :direction, :priority, :caller_id_policy, :allow_outbound, :accept_inbound, :allow_international)
        ON CONFLICT (tenant_id, gateway_id) DO UPDATE SET
            direction = EXCLUDED.direction,
            priority = EXCLUDED.priority,
            caller_id_policy = EXCLUDED.caller_id_policy,
            allow_outbound = EXCLUDED.allow_outbound,
            accept_inbound = EXCLUDED.accept_inbound,
            allow_international = EXCLUDED.allow_international
        RETURNING tenant_id, gateway_id, direction, priority, caller_id_policy
    """
    row = await execute_query_one(query, payload.dict())
    return dict(row)
'''

with open(os.path.join(base_backend, "gateways.py"), "w", encoding="utf-8") as f:
    f.write(gateways_py)


# 3. ROUTING.PY
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
        VALUES (:name, :did_number, :route_type, :destination_type, :destination, :priority, :regex_pattern, :gateway_id, :tenant_id)
        RETURNING id, name, did_number, route_type, destination_type, destination, priority, regex_pattern, enabled, created_at::text
    """
    data = payload.dict()
    data["tenant_id"] = target_tenant
    row = await execute_query_one(query, data)
    return dict(row)
'''

with open(os.path.join(base_backend, "routing.py"), "w", encoding="utf-8") as f:
    f.write(routing_py)


# 4. QUEUES.PY
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
    announce_position: bool = True
    announce_wait_time: bool = True
    tenant_id: Optional[UUID] = None

@router.get("")
async def list_queues(
    tenant_id: Optional[UUID] = None,
    current_user: CurrentUser = Depends(get_current_user)
):
    target_tenant = tenant_id if current_user.is_super_admin else current_user.tenant_id
    query = """
        SELECT q.id, q.name, q.queue_number, q.strategy, q.agent_timeout, q.wrap_up_time,
               q.max_wait_time, q.agents, q.announce_position, q.announce_wait_time, q.enabled,
               q.created_at::text, t.name as tenant_name
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
        INSERT INTO queues (name, queue_number, strategy, agent_timeout, wrap_up_time, max_wait_time, agents, announce_position, announce_wait_time, tenant_id)
        VALUES (:name, :queue_number, :strategy, :agent_timeout, :wrap_up_time, :max_wait_time, :agents, :announce_position, :announce_wait_time, :tenant_id)
        RETURNING id, name, queue_number, strategy, agent_timeout, wrap_up_time, max_wait_time, agents, enabled, created_at::text
    """
    data = payload.dict()
    data["tenant_id"] = target_tenant
    row = await execute_query_one(query, data)
    return dict(row)
'''

with open(os.path.join(base_backend, "queues.py"), "w", encoding="utf-8") as f:
    f.write(queues_py)


# UPDATE MAIN.PY
main_py_path = r"C:\PROJECTS\Fullstack PBX\PBX\src\main.py"
with open(main_py_path, "r", encoding="utf-8") as f:
    content = f.read()

target_import = "from src.api.v1 import auth, tenants, extensions, users"
new_import = "from src.api.v1 import auth, tenants, extensions, users, trunks, gateways, routing, queues"

target_routers = "app.include_router(users.router, prefix=settings.API_V1_STR)"
new_routers = """app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(trunks.router, prefix=settings.API_V1_STR)
app.include_router(gateways.router, prefix=settings.API_V1_STR)
app.include_router(routing.router, prefix=settings.API_V1_STR)
app.include_router(queues.router, prefix=settings.API_V1_STR)"""

if target_import in content:
    content = content.replace(target_import, new_import)
if target_routers in content:
    content = content.replace(target_routers, new_routers)

with open(main_py_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Backend files successfully updated in C:\\PROJECTS\\Fullstack PBX\\PBX")
