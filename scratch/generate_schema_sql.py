import subprocess, os

print("Extracting clean database schema from pbx_postgres...")

cmd = ['docker', 'exec', '-i', 'pbx_postgres', 'pg_dump', '-U', 'pbx_user', '-d', 'pbx_db', '--schema-only', '--no-owner', '--no-privileges']
proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

if proc.returncode != 0:
    print("Error dumping schema:", proc.stderr)
    exit(1)

schema_sql = proc.stdout

# Clean up pg_dump meta-commands like \restrict if present
lines = []
for line in schema_sql.splitlines(keepends=True):
    if line.strip().startswith('\\restrict'):
        continue
    lines.append(line)

cleaned_schema = "".join(lines)

seed_roles_sql = """

-- ============================================================================
-- SEED DATA: CORE ROLES & PERMISSIONS
-- ============================================================================

INSERT INTO roles (id, name, description) VALUES
    ('3fb08e00-1d89-4618-a783-c13e5e34d7f9', 'SUPER_ADMIN', 'Platform Super Administrator with complete system access'),
    ('89b9e390-729d-4855-b6e7-9387870d1db4', 'TENANT_ADMIN', 'Tenant Master Administrator with full access to tenant features'),
    ('6c1dfe90-5ec9-4587-997b-30eecaeaec0c', 'SUB_ADMIN', 'Tenant Sub-Administrator with configurable modular permissions'),
    ('e1b4d41a-382e-4ee9-99a3-4039e1ace468', 'SUPERVISOR', 'Call Center / Extension Supervisor with monitoring & reports access'),
    ('1b6dc9d3-247f-4bf3-b3f7-af1acc82d439', 'AGENT', 'Standard Extension / Softphone User with voicemail & forwarding access')
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description;

-- ============================================================================
-- END OF SCHEMA & INITIAL SEED
-- ============================================================================
"""

final_sql = cleaned_schema + seed_roles_sql

target_paths = [
    'c:/PROJECTS/Fullstack PBX/PBX/migrations/001_initial_schema.sql',
    'c:/PROJECTS/PBX/migrations/001_initial_schema.sql'
]

for p in target_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(final_sql)
    print(f"Wrote updated schema ({len(final_sql)} chars) to: {p}")

print("Database schema synchronization complete!")
