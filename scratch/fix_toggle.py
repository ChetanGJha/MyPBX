with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/CallForwardingView.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for l in lines:
    if '// const handleQuickToggleAlways = async (rule: ForwardingRuleItem) => {' in l:
        skip = True
        continue
    if skip:
        if l.strip() == '};':
            skip = False
            continue
        continue
    new_lines.append(l)

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/CallForwardingView.tsx', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Removed unused handleQuickToggleAlways cleanly.")
