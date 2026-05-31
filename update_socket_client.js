import re

with open('static/js/socket_client.js', 'r') as f:
    content = f.read()

content = content.replace("showScreen('setup-screen');", "showScreen('setup-screen');\n    startTurnTimer();")
content = content.replace("initHelperPanel();", "initHelperPanel();\n    startTurnTimer();")
content = content.replace("updateTurnUI(data.current_turn);", "updateTurnUI(data.current_turn);\n    startTurnTimer();")
content = content.replace("const isWinner = (data.winner_sid === socket.id);", "stopTurnTimer();\n    const isWinner = (data.winner_sid === socket.id);")

with open('static/js/socket_client.js', 'w') as f:
    f.write(content)
