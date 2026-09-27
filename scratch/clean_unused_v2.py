import os

def clean_file(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    for old, new in replacements.items():
        c = c.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

clean_file(r"C:\PROJECTS\Fullstack PBX\frontend\src\components\GatewaysView.tsx", {
    "import { Cpu, Link, CheckCircle2, Layers } from 'lucide-react';": "import { Link } from 'lucide-react';"
})

clean_file(r"C:\PROJECTS\Fullstack PBX\frontend\src\components\ReportsView.tsx", {
    "import { FileText, Calendar, Filter, PhoneIncoming, PhoneOutgoing, PhoneCall, Disc, Volume2 } from 'lucide-react';": "import { FileText, Calendar, Filter, PhoneOutgoing, PhoneCall, Disc, Volume2 } from 'lucide-react';"
})

clean_file(r"C:\PROJECTS\Fullstack PBX\frontend\src\components\RoutingView.tsx", {
    "import { Route as RouteIcon, Plus, Search, ArrowUpRight, ArrowDownLeft, PhoneCall, Trash2 } from 'lucide-react';": "import { Route as RouteIcon, Plus, Search, Trash2 } from 'lucide-react';",
    "const [trunks, setTrunks] = useState<any[]>([]);\n": "",
    "const [rData, tData, sData] = await Promise.allSettled([\n        apiService.getRoutes(token),\n        apiService.getTenants(token),\n        apiService.getTrunks(token)\n      ]);": "const [rData, tData] = await Promise.allSettled([\n        apiService.getRoutes(token),\n        apiService.getTenants(token)\n      ]);",
    "if (sData.status === 'fulfilled') setTrunks(sData.value);\n": ""
})

print("Unused imports cleaned.")
