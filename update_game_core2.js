import re

with open('static/js/game_core.js', 'r') as f:
    content = f.read()

content = content.replace("turnBadge.innerText = t('turn_you_ai');", "document.getElementById('turn-text').innerText = t('turn_you_ai');")
content = content.replace("turnBadge.innerText = t('turn_ai_think');", "document.getElementById('turn-text').innerText = t('turn_ai_think');")
content = content.replace("turnBadge.innerText = t('turn_you');", "document.getElementById('turn-text').innerText = t('turn_you');")

with open('static/js/game_core.js', 'w') as f:
    f.write(content)
