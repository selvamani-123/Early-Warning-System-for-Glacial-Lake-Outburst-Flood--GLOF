window.API_BASE = (window.location.port === '8081' || window.location.port === '3000' || window.location.protocol === 'file:') ? 'http://localhost:8000' : '';

class AppHeader extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
        <header class="h-14 border-b border-white/10 flex items-center justify-between px-6 bg-bgPanel z-50 shrink-0">
            <div class="flex items-center gap-3 w-1/4">
                <span class="material-symbols-outlined text-accent text-2xl">satellite_alt</span>
                <span class="font-bold tracking-widest text-lg text-white">GLOF SENTINEL</span>
                <span class="text-xs text-textSecondary ml-2 font-mono border border-white/10 px-2 py-0.5 rounded">v2.0 MISSION CONTROL</span>
            </div>
            
            <div class="flex-1 max-w-2xl relative px-4">
                <div class="relative">
                    <span class="material-symbols-outlined absolute left-3 top-1.5 text-textSecondary text-[20px]">search</span>
                    <input type="text" id="global-search" placeholder="Search Lakes, Rivers, Regions..." class="w-full bg-white/5 border border-white/10 rounded-lg py-1.5 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-accent focus:bg-white/10 transition-colors" autocomplete="off">
                </div>
                <div id="search-results" class="absolute top-full left-4 right-4 mt-1 bg-bgPanel border border-white/10 rounded-lg shadow-xl hidden z-50 max-h-64 overflow-y-auto">
                </div>
            </div>

            <div class="flex items-center justify-end gap-6 w-1/4">
                <div class="flex items-center gap-2">
                    <span class="relative flex h-3 w-3">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-riskLow opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-3 w-3 bg-riskLow"></span>
                    </span>
                    <span class="text-xs font-mono text-textSecondary uppercase">System Online</span>
                </div>
                <div class="text-xs font-mono text-textSecondary" id="live-clock">--:--:-- UTC</div>
            </div>
        </header>
        `;
        
        setInterval(() => {
            const clock = document.getElementById('live-clock');
            if(clock) {
                const now = new Date();
                clock.innerText = now.toISOString().substring(11,19) + ' UTC';
            }
        }, 1000);
    }
}

class AppSidebar extends HTMLElement {
    connectedCallback() {
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const urlParams = new URLSearchParams(window.location.search);
        const currentId = urlParams.get('id');
        const queryString = currentId ? `?id=${currentId}` : '';
        
        const links = [
            { href: 'index.html', icon: 'public', text: 'Global Overview' },
            { href: 'registry.html', icon: 'table_view', text: 'Global Registry' },
            { href: 'lake_intelligence.html', icon: 'analytics', text: 'Lake Intelligence' },
            { href: 'river_intelligence.html', icon: 'waves', text: 'River Intelligence' },
            { href: 'history.html', icon: 'history', text: 'Historical Analysis' },
            { href: 'monitoring.html', icon: 'speed', text: 'Live Monitoring' },
            { href: 'alerts.html', icon: 'warning', text: 'Alert Center' },
            { href: 'analytics.html', icon: 'insights', text: 'Analytics' }
        ];

        let linksHTML = links.map(link => {
            const isActive = currentPage === link.href ? 'active bg-white/5' : 'hover:bg-white/5';
            const textClass = currentPage === link.href ? 'text-white' : 'text-textSecondary hover:text-white';
            
            // Do not append ?id to Global Overview or Global Registry
            const isGlobal = link.href === 'index.html' || link.href === 'registry.html';
            const finalHref = isGlobal ? link.href : `${link.href}${queryString}`;
            
            return `
                <a href="${finalHref}" class="nav-item ${isActive} flex items-center gap-4 px-4 py-3 ${textClass} transition-colors">
                    <span class="material-symbols-outlined shrink-0">${link.icon}</span>
                    <span class="text-sm font-medium whitespace-nowrap">${link.text}</span>
                </a>
            `;
        }).join('');

        this.innerHTML = `
        <!-- Hamburger Menu Button for Mobile -->
        <button id="mobile-menu-btn" class="lg:hidden absolute top-3 left-4 z-[60] text-white p-2">
            <span class="material-symbols-outlined">menu</span>
        </button>
        
        <!-- Sidebar overlay for mobile -->
        <div id="mobile-overlay" class="lg:hidden fixed inset-0 bg-black/50 z-[45] hidden"></div>
        
        <!-- Sidebar -->
        <nav id="app-sidebar-nav" class="fixed lg:static w-64 border-r border-white/10 bg-bgPanel z-50 flex flex-col py-4 overflow-hidden shrink-0 h-[calc(100vh-3.5rem)] lg:h-full transform -translate-x-full lg:translate-x-0 transition-transform duration-300">
            <div class="flex flex-col gap-2 w-64 mt-10 lg:mt-0">
                ${linksHTML}
            </div>
            <div class="mt-auto px-4 pb-4">
            </div>
        </nav>
        `;
        
        // Add mobile menu toggle logic after render
        setTimeout(() => {
            const btn = document.getElementById('mobile-menu-btn');
            const nav = document.getElementById('app-sidebar-nav');
            const overlay = document.getElementById('mobile-overlay');
            
            if (btn && nav && overlay) {
                const toggleMenu = () => {
                    const isClosed = nav.classList.contains('-translate-x-full');
                    if (isClosed) {
                        nav.classList.remove('-translate-x-full');
                        overlay.classList.remove('hidden');
                    } else {
                        nav.classList.add('-translate-x-full');
                        overlay.classList.add('hidden');
                    }
                };
                
                btn.addEventListener('click', toggleMenu);
                overlay.addEventListener('click', toggleMenu);
            }
        }, 0);
    }
}

customElements.define('app-header', AppHeader);
customElements.define('app-sidebar', AppSidebar);
