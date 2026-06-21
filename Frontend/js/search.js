// Global Search Engine
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('search-results');
    
    if(!searchInput || !searchResults) return;

    let searchData = [];
    
    // Load data from backend (lakes and rivers)
    Promise.all([
        fetch('http://localhost:8000/api/map-data/lakes').then(res => res.json()).catch(() => ({features:[]})),
        fetch('http://localhost:8000/api/map-data/rivers').then(res => res.json()).catch(() => ({features:[]}))
    ]).then(([lakesData, riversData]) => {
        
        // Process Lakes
        lakesData.features.forEach(f => {
            if(f.properties && f.properties.name) {
                searchData.push({
                    type: 'Lake',
                    name: f.properties.name,
                    id: f.properties.glacier_id,
                    url: `lake_intelligence.html?id=${f.properties.glacier_id}`,
                    tags: ['Lake', f.properties.risk || '', f.properties.glacier_id]
                });
            }
        });
        
        // Process Rivers
        riversData.features.forEach(f => {
            if(f.properties && f.properties.name) {
                // Generate a dummy ID if none exists
                const id = f.properties.id || f.properties.name.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
                searchData.push({
                    type: 'River',
                    name: f.properties.name,
                    id: id,
                    url: `river_intelligence.html?id=${id}`,
                    tags: ['River', f.properties.basin || '', f.properties.type || '']
                });
            }
        });
    });

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        searchResults.innerHTML = '';
        
        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }

        const results = searchData.filter(item => {
            return item.name.toLowerCase().includes(query) || 
                   item.tags.some(t => t.toLowerCase().includes(query));
        }).slice(0, 8); // Limit to 8 results

        if (results.length > 0) {
            searchResults.classList.remove('hidden');
            
            // Group by type
            const lakes = results.filter(r => r.type === 'Lake');
            const rivers = results.filter(r => r.type === 'River');
            
            if(lakes.length > 0) {
                const header = document.createElement('div');
                header.className = 'px-4 py-2 text-[10px] font-bold text-textSecondary uppercase tracking-widest bg-white/5 border-b border-white/10';
                header.innerText = 'Lakes & Glacier Regions';
                searchResults.appendChild(header);
                
                lakes.forEach(renderItem);
            }
            
            if(rivers.length > 0) {
                const header = document.createElement('div');
                header.className = 'px-4 py-2 text-[10px] font-bold text-textSecondary uppercase tracking-widest bg-white/5 border-b border-white/10 border-t';
                if(lakes.length === 0) header.classList.remove('border-t');
                header.innerText = 'River Systems';
                searchResults.appendChild(header);
                
                rivers.forEach(renderItem);
            }
        } else {
            searchResults.classList.remove('hidden');
            const noRes = document.createElement('div');
            noRes.className = 'px-4 py-3 text-sm text-textSecondary text-center';
            noRes.innerText = 'No results found.';
            searchResults.appendChild(noRes);
        }
    });
    
    function renderItem(item) {
        const div = document.createElement('a');
        div.href = item.url;
        div.className = 'block px-4 py-3 hover:bg-white/10 border-b border-white/5 last:border-0 transition-colors flex items-center gap-3 cursor-pointer';
        
        const icon = item.type === 'Lake' ? 'water' : 'waves';
        const colorClass = item.type === 'Lake' ? 'text-accent' : 'text-riskLow';
        
        div.innerHTML = `
            <span class="material-symbols-outlined ${colorClass} text-lg">${icon}</span>
            <div>
                <div class="text-sm text-white font-medium">${item.name}</div>
                <div class="text-[10px] text-textSecondary font-mono mt-0.5">${item.tags.filter(t=>t).join(' • ')}</div>
            </div>
        `;
        searchResults.appendChild(div);
    }

    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });
});
