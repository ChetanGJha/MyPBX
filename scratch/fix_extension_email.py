for path in [
    'c:/PROJECTS/Fullstack PBX/PBX/src/api/v1/extensions.py',
    'c:/PROJECTS/PBX/src/api/v1/extensions.py'
]:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Replace EmailStr with str in ExtensionCreate and ExtensionUpdate
    code = code.replace('email: Optional[EmailStr] = None', 'email: Optional[str] = None')

    # Replace email handling in create_extension
    old_insert_call = '''        "tenant_id": target_tenant_id,
        "extension_number": payload.extension_number,
        "display_name": payload.display_name,
        "email": payload.email,'''

    new_insert_call = '''        "tenant_id": target_tenant_id,
        "extension_number": payload.extension_number,
        "display_name": payload.display_name,
        "email": payload.email.strip() if payload.email and payload.email.strip() else None,'''

    code = code.replace(old_insert_call, new_insert_call)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"Patched email validation in {path}")

print("Both extensions.py files updated.")
