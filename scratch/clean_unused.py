import os

# Clean UsersView unused imports
users_view_path = r"C:\PROJECTS\Fullstack PBX\frontend\src\components\UsersView.tsx"
with open(users_view_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import { Plus, Trash2, KeyRound, ShieldCheck, Building2, User } from 'lucide-react';", "import { Plus, Trash2, KeyRound } from 'lucide-react';")

with open(users_view_path, "w", encoding="utf-8") as f:
    f.write(content)

# Clean Sidebar unused prop
sidebar_path = r"C:\PROJECTS\Fullstack PBX\frontend\src\components\Sidebar.tsx"
with open(sidebar_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("  user,\n", "")

with open(sidebar_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Unused imports cleaned successfully.")
