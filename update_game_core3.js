import re

with open('static/js/game_core.js', 'r') as f:
    content = f.read()

content = content.replace("turnBadge.innerText = t('time_status', {time: timeLeft, score: soloScore});", "document.getElementById('turn-text').innerText = t('time_status', {time: timeLeft, score: soloScore});\n    document.getElementById('timer-text').innerText = '';")

with open('static/js/game_core.js', 'w') as f:
    f.write(content)
