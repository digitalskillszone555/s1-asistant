const BASE_URL = 'http://localhost:8000/api'; // Ensure proxy or CORS allows this

export const api = {
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('s1_token');
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };

        let url = `${BASE_URL}${endpoint}`;

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            const data = await response.json();
            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    window.dispatchEvent(new Event('tokenExpired'));
                }
                throw new Error(data.message || 'API request failed');
            }
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    login(email, password) {
        return this.request('/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    register(data) {
        return this.request('/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    resetPassword(email) {
        return this.request('/reset', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    },

    sendMessage(message) {
        return this.request('/command', {
            method: 'POST',
            body: JSON.stringify({ text: message })
        });
    },

    executeAction(type, data) {
        return this.request('/execute_action', {
            method: 'POST',
            body: JSON.stringify({ type, data })
        });
    },

    getSuggestions() {
        return this.request('/suggestions', { method: 'GET' });
    },

    runSelfTest() {
        return this.request('/self-test', { method: 'GET' });
    },

    runFullTest() {
        return this.request('/full-test', { method: 'GET' });
    },

    runAction(action) {
        return this.request('/command', {
            method: 'POST',
            body: JSON.stringify({ text: action })
        });
    },

    getMemory() {
        return this.request('/memory', { method: 'GET' });
    },

    saveMemory(data) {
        return this.request('/memory', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    getAutoSuggestion() {
        return this.request('/auto_mode/suggestion', { method: 'GET' });
    },

    toggleAutoMode(enabled) {
        return this.request('/auto_mode/toggle', {
            method: 'POST',
            body: JSON.stringify({ enabled })
        });
    },

    toggleAutoExec(enabled) {
        return this.request('/auto_mode/toggle_auto_exec', {
            method: 'POST',
            body: JSON.stringify({ enabled })
        });
    },

    logAction(action, result) {
        return this.request('/log_action', {
            method: 'POST',
            body: JSON.stringify({ action, result })
        });
    },

    logError(data) {
        return this.request('/log_error', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
};
