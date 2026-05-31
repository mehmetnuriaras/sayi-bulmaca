import re

with open('static/js/ui.js', 'r') as f:
    content = f.read()

content = content.replace("turnBadge.innerText = t('turn_you');", "document.getElementById('turn-text').innerText = t('turn_you');")
content = content.replace("turnBadge.innerText = t('turn_opp');", "document.getElementById('turn-text').innerText = t('turn_opp');")

with open('static/js/ui.js', 'w') as f:
    f.write(content)
