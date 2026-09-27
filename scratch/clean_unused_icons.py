import os

def clean_file(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    for old, new in replacements.items():
        c = c.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

clean_file(r"C:\PROJECTS\Fullstack PBX\frontend\src\components\GatewaysView.tsx", {
    "import { Cpu, Plus, Link, CheckCircle2, Server, Layers, ShieldCheck } from 'lucide-react';": "import { Cpu, Link, CheckCircle2, Layers } from 'lucide-react';"
})

clean_file(r"C:\PROJECTS\Fullstack PBX\frontend\src\components\QueuesView.tsx", {
    "import { Users, Clock, PhoneIncoming, Headphones, CheckCircle2 } from 'lucide-react';": "import { Users, Clock, Headphones } from 'lucide-react';"
})

clean_file(r"C:\PROJECTS\Fullstack PBX\frontend\src\components\RoutingView.tsx", {
    "import { Route, Plus, Search, ArrowUpRight, ArrowDownLeft, PhoneCall } from 'lucide-react';": "import { Search, ArrowUpRight, ArrowDownLeft, PhoneCall } from 'lucide-react';"
})

clean_file(r"C:\PROJECTS\Fullstack PBX\frontend\src\components\TrunksView.tsx", {
    "import { Network, Plus, Search, Server, ShieldCheck, Activity, Trash2, CheckCircle2, XCircle } from 'lucide-react';": "import { Network, Plus, Search, Server, ShieldCheck, Activity, CheckCircle2 } from 'lucide-react';"
})

print("Unused imports cleaned.")
