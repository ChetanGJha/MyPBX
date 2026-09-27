import os

components_dir = r"c:\PROJECTS\Fullstack PBX\frontend\src\components"

# 1. Fix CallForwardingView.tsx
cf_path = os.path.join(components_dir, "CallForwardingView.tsx")
with open(cf_path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "import { PhoneForwarded, Clock, RefreshCw, Edit2, AlertCircle, X, Smartphone, ArrowRight, Plus, Search } from 'lucide-react';",
    "import { PhoneForwarded, RefreshCw, Edit2, Plus, Search } from 'lucide-react';"
)
text = text.replace("apiService.getForwardingRulesAll(token)", "apiService.getCallForwardingAll(token)")

with open(cf_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Fixed CallForwardingView.tsx")

# 2. Fix AudioView.tsx
audio_path = os.path.join(components_dir, "AudioView.tsx")
with open(audio_path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "import { Upload, Play, Pause, Trash2, Mic, Volume2, VolumeX, Music, Clock, Search } from 'lucide-react';",
    "import { Upload, Play, Pause, Trash2, Mic, Volume2, VolumeX, Music, Search } from 'lucide-react';"
)

with open(audio_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Fixed AudioView.tsx")
