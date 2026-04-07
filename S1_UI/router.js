import { state } from './state.js';

export const router = {
    routes: ['/login', '/register', '/reset', '/home', '/dashboard', '/voice', '/actions', '/suggestions', '/memory'],
    
    init() {
        window.addEventListener('popstate', () => this.handleRoute());
        
        document.body.addEventListener('click', e => {
            const link = e.target.closest('a[data-route], a[href^="/"]');
            if (link && link.getAttribute('target') !== '_blank') {
                const href = link.getAttribute('href');
                if (this.routes.includes(href) || href === '/') {
                    e.preventDefault();
                    this.navigate(href);
                }
            }
        });

        // Handle initial load
        this.handleRoute();
    },

    navigate(path) {
        if (path === '/') path = '/home';
        if (this.routes.includes(path)) {
            history.pushState(null, '', path);
            this.handleRoute();
        }
    },

    handleRoute() {
        let path = window.location.pathname;
        if (path === '/') path = '/home';
        
        // Hide all page containers
        document.querySelectorAll('.page-container').forEach(page => {
            page.style.display = 'none';
            page.classList.remove('active');
        });
        
        // Protection check
        const protectedRoutes = ['/dashboard', '/voice', '/actions', '/suggestions', '/memory'];
        if (protectedRoutes.includes(path) && !state.isAuthenticated) {
            this.navigate('/login');
            return;
        }

        // Auto-login check
        if ((path === '/login' || path === '/register') && state.isAuthenticated) {
            this.navigate('/dashboard');
            return;
        }

        // Show active page container
        // Assumes HTML elements like <div id="page-dashboard" class="page-container">
        const activePageId = `page-${path.substring(1)}`;
        const activePage = document.getElementById(activePageId);
        
        if (activePage) {
            activePage.style.display = 'block';
            activePage.classList.add('active');
        } else {
            console.warn(`Page container #${activePageId} not found.`);
        }
        
        // Dispatch custom event to trigger page-specific initialization logic
        window.dispatchEvent(new CustomEvent('routeChanged', { detail: { path } }));
    }
};
