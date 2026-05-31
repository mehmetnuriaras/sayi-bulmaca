import os
import re

os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract CSS
css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if css_match:
    css_content = css_match.group(1)
    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content.strip())
    content = content.replace(f'<style>{css_content}</style>', '<link rel="stylesheet" href="/static/css/style.css">')

# Extract JS
js_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if js_match:
    js_content = js_match.group(1)
    
    # We will manually split js_content based on comments or known structures
    # Let's find the parts
    
    i18n_script = ""
    auth_script = ""
    game_core_script = ""
    socket_client_script = ""
    ui_script = ""
    main_script = ""
    
    # Actually, rather than writing fragile python code, I'll just save the whole JS to main.js
    # and then manually split it in subsequent steps. Or I can do it now.
    
    # I'll just write it to a temporary file and split it with another Python script that I'll refine.
    with open('static/js/all_js_temp.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    content = content.replace(f'<script>{js_content}</script>', '''
    <script src="/static/js/main.js"></script>
    <script src="/static/js/i18n.js"></script>
    <script src="/static/js/auth.js"></script>
    <script src="/static/js/ui.js"></script>
    <script src="/static/js/game_core.js"></script>
    <script src="/static/js/socket_client.js"></script>
    ''')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Extraction 1 complete")
