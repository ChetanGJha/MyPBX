import os

components_dir = r"c:\PROJECTS\Fullstack PBX\frontend\src\components"

# 1. Fix RoutingView.tsx
routing_path = os.path.join(components_dir, "RoutingView.tsx")
with open(routing_path, "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace("apiService.getRoutingRules(token)", "apiService.getRoutes(token)")
with open(routing_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Fixed RoutingView.tsx getRoutes")

# 2. Fix HuntGroupsView.tsx unused imports
hunt_path = os.path.join(components_dir, "HuntGroupsView.tsx")
with open(hunt_path, "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace("import { PhoneForwarded, Plus, Edit2, Trash2, Search, X, Users, PhoneCall } from 'lucide-react';",
                    "import { PhoneForwarded, Plus, Edit2, Trash2, Search, X } from 'lucide-react';")
with open(hunt_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Fixed HuntGroupsView.tsx imports")

# 3. Fix QueuesView.tsx unused imports
queues_path = os.path.join(components_dir, "QueuesView.tsx")
with open(queues_path, "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace("import { Users, Plus, Edit2, Trash2, Search, Check, X, PhoneCall, Clock } from 'lucide-react';",
                    "import { Users, Plus, Edit2, Trash2, Search, X } from 'lucide-react';")
with open(queues_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Fixed QueuesView.tsx imports")

# 4. Fix VoicemailView.tsx unused imports
vm_path = os.path.join(components_dir, "VoicemailView.tsx")
with open(vm_path, "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace("import { Voicemail, Mail, Key, RefreshCw, Edit2, AlertCircle, Plus, Music, Search, CheckCircle2, Shield } from 'lucide-react';",
                    "import { Voicemail, Mail, RefreshCw, Edit2, Plus, Search } from 'lucide-react';")
with open(vm_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Fixed VoicemailView.tsx imports")
