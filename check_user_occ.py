import re

for filename in ['AudioView.tsx', 'GatewaysView.tsx', 'ReportsView.tsx', 'RoutingView.tsx']:
    path = rf'c:\PROJECTS\Fullstack PBX\frontend\src\components\{filename}'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # find where user appears
    matches = [m.start() for m in re.finditer(r'\buser\b', content)]
    print(f"{filename}: {len(matches)} occurrences of 'user'")
