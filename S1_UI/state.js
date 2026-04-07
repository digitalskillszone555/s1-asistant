export const state = {
    user: JSON.parse(localStorage.getItem('s1_user')) || null,
    token: localStorage.getItem('s1_token') || null,
    isAuthenticated: !!localStorage.getItem('s1_token'),
    voiceEnabled: localStorage.getItem('s1_voice') !== 'off',
    autoMode: localStorage.getItem('s1_auto_mode') === 'on',
    autoExecution: localStorage.getItem('s1_auto_exec') === 'on',
    assistantState: 'idle', // idle, listening, thinking, speaking
    listeners: [],

    subscribe(listener) {
        this.listeners.push(listener);
    },

    notify() {
        this.listeners.forEach(listener => listener(this));
    },

    update(newState) {
        Object.assign(this, newState);
        if (newState.token !== undefined) {
            if (newState.token) {
                localStorage.setItem('s1_token', newState.token);
                this.isAuthenticated = true;
            } else {
                localStorage.removeItem('s1_token');
                this.isAuthenticated = false;
            }
        }
        if (newState.user !== undefined) {
            if (newState.user) {
                localStorage.setItem('s1_user', JSON.stringify(newState.user));
            } else {
                localStorage.removeItem('s1_user');
            }
        }
        if (newState.voiceEnabled !== undefined) {
            localStorage.setItem('s1_voice', newState.voiceEnabled ? 'on' : 'off');
        }
        if (newState.autoMode !== undefined) {
            localStorage.setItem('s1_auto_mode', newState.autoMode ? 'on' : 'off');
        }
        if (newState.autoExecution !== undefined) {
            localStorage.setItem('s1_auto_exec', newState.autoExecution ? 'on' : 'off');
        }
        this.notify();
    },

    logout() {
        this.update({ token: null, user: null });
        window.dispatchEvent(new Event('authChanged'));
    }
};
