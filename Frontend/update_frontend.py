import os
import re

def process_file(filepath, replacements):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, not found")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Fix index.html
process_file('d:\\GLOF Sentinel\\frontend\\index.html', [
    ('group overflow-hidden absolute h-[calc(100vh-3.5rem)]', 'overflow-hidden shrink-0'),
    ('<main class="flex-1 relative ml-16">', '<main class="flex-1 relative">'),
    ('http://localhost:8000/api/map-data/rivers', '/api/map-data/rivers'),
    ('http://localhost:8000/api/map-data/lakes', '/api/map-data/lakes')
])

# Fix Alerts.html
process_file('d:\\GLOF Sentinel\\frontend\\Alerts.html', [
    ("fetch('http://localhost:8000/api/alerts')", "fetch('/api/alerts')")
])

# Fix Analysis.html
process_file('d:\\GLOF Sentinel\\frontend\\Analysis.html', [
    ("fetch('http://localhost:8000/api/dashboard-summary')", "fetch('/api/dashboard-summary')")
])

# Fix LiveMonitoring.html
process_file('d:\\GLOF Sentinel\\frontend\\LiveMonitoring.html', [
    ("fetch('http://localhost:8000/", "fetch('/")
])

print("Global layout alignment and relative API paths updated.")
