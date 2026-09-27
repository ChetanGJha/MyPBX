# Clean up unused identifiers

# 1. CallForwardingView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/CallForwardingView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('PhoneCall, PhoneMissed, ', '')
c = c.replace('({ token, user })', '({ token })')
# Either use handleQuickToggleAlways or remove it
c = c.replace('const handleQuickToggleAlways', '// const handleQuickToggleAlways')

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/CallForwardingView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)

# 2. UsersView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/UsersView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(', CheckSquare, Square', '')

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/UsersView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)

# 3. VoicemailView.tsx
with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/VoicemailView.tsx', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('Volume2, ', '')
c = c.replace('Shield, ', '')
c = c.replace('({ token, user })', '({ token })')

with open('c:/PROJECTS/Fullstack PBX/frontend/src/components/VoicemailView.tsx', 'w', encoding='utf-8') as f:
    f.write(c)

print("Cleaned unused identifiers in all 3 components.")
