import os

sql_path = r"C:\PROJECTS\Fullstack PBX\PBX\migrations\001_initial_schema.sql"

new_tables_sql = """

-- ============================================================================
-- SOFIA GATEWAYS & TENANT ASSIGNMENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS gateways (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    proxy VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    password VARCHAR(255),
    realm VARCHAR(255),
    from_domain VARCHAR(255),
    codecs VARCHAR(255) DEFAULT 'PCMU,PCMA,G722',
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    register BOOLEAN DEFAULT true,
    caller_id_in_from BOOLEAN DEFAULT false,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS tenant_gateways (
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    gateway_id UUID REFERENCES gateways(id) ON DELETE CASCADE,
    direction VARCHAR(50) DEFAULT 'inbound_outbound',
    priority INT DEFAULT 1,
    caller_id_policy VARCHAR(50) DEFAULT 'tenant_default',
    allow_outbound BOOLEAN DEFAULT true,
    accept_inbound BOOLEAN DEFAULT true,
    allow_international BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant_id, gateway_id)
);

-- ============================================================================
-- CALL ROUTING & DIALPLAN RULES
-- ============================================================================

CREATE TABLE IF NOT EXISTS call_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    did_number VARCHAR(50),
    route_type VARCHAR(50) DEFAULT 'inbound_did',
    destination_type VARCHAR(50) DEFAULT 'queue',
    destination VARCHAR(255) NOT NULL,
    priority INT DEFAULT 1,
    regex_pattern VARCHAR(255),
    gateway_id UUID REFERENCES gateways(id) ON DELETE SET NULL,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- ============================================================================
-- CALL QUEUES (mod_callcenter)
-- ============================================================================

CREATE TABLE IF NOT EXISTS queues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    queue_number VARCHAR(20) NOT NULL,
    strategy VARCHAR(50) DEFAULT 'round_robin',
    agent_timeout INT DEFAULT 30,
    wrap_up_time INT DEFAULT 10,
    max_wait_time INT DEFAULT 300,
    agents TEXT,
    announce_position BOOLEAN DEFAULT true,
    announce_wait_time BOOLEAN DEFAULT true,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
"""

with open(sql_path, "r", encoding="utf-8") as f:
    content = f.read()

if "CREATE TABLE IF NOT EXISTS gateways" not in content:
    content += new_tables_sql
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Schema added to 001_initial_schema.sql")
else:
    print("Schema already present in 001_initial_schema.sql")
