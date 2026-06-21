import os
import re

files = [
    'index.html', 'registry.html', 'lake_intelligence.html', 
    'river_intelligence.html', 'LiveMonitoring.html', 
    'Alerts.html', 'Analysis.html'
]

for f in files:
    if not os.path.exists(f):
        continue
        
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace w-16 hover:w-64 with w-64
    new_content = content.replace('w-16 hover:w-64 transition-all duration-300', 'w-64 flex-none')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(new_content)

print("Navigation made permanently static (w-64) successfully.")
