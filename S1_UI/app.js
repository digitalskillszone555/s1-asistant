import { api } from './services/api.js';
import { state } from './state.js';
import { router } from './router.js';

// --- Debug & Utility Functions ---
const DEBUG_MODE = true;

const safeLog = (...args) => {
    if (DEBUG_MODE) console.log(...args);
};

const safeWarn = (...args) => {
    if (DEBUG_MODE) console.warn(...args);
};

const safeError = (...args) => {
    if (DEBUG_MODE) console.error(...args);
};

const debounce = (func, wait = 300) => {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
};

const showLoading = () => {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.style.display = 'block';
};

const hideLoading = () => {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.style.display = 'none';
};

const showError = (message) => {
    updateStatusIndicator('error');
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        setTimeout(() => errorContainer.style.display = 'none', 5000);
    } else {
        alert(message);
    }
    // Also append to chat for better visibility
    appendMessage(`Error: ${message}`, 'assistant');
};

const updateStatusIndicator = (status) => {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');
    if (!indicator || !text) return;
    
    indicator.className = '';
    if (status === 'idle') {
        indicator.classList.add('status-active');
        text.textContent = 'AI Active';
    } else if (status === 'thinking') {
        indicator.classList.add('status-thinking');
        text.textContent = 'Thinking...';
    } else if (status === 'error') {
        indicator.classList.add('status-error');
        text.textContent = 'Error';
    }
};

state.subscribe((s) => {
    if (s.assistantState === 'idle') updateStatusIndicator('idle');
    else if (s.assistantState === 'thinking') updateStatusIndicator('thinking');
});

let activityLog = [];
const logActivity = (text, type = 'info') => {
    activityLog.unshift({ text, type, time: new Date().toLocaleTimeString() });
    if (activityLog.length > 50) activityLog.pop();
    
    const logContainer = document.getElementById('dash-activity-log');
    if (logContainer) {
        logContainer.innerHTML = '';
        activityLog.forEach(log => {
            const div = document.createElement('div');
            div.className = `log-item ${log.type}`;
            div.textContent = `[${log.time}] ${log.text}`;
            logContainer.appendChild(div);
        });
    }
};

const speak = (text) => {
    if (!state.voiceEnabled || !window.speechSynthesis) return;
    
    // Cancel previous speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-IN';
    utterance.rate = 1;
    utterance.pitch = 1;
    
    window.speechSynthesis.speak(utterance);
};

const appendMessage = (text, sender, isSuggestion = false) => {
    const chatContainer = document.getElementById('chat-messages');
    if (!chatContainer) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `message message-${sender}`;
    if (isSuggestion) {
        msgDiv.classList.add('message-suggestion');
    }
    
    if (text === 'Typing...') {
        msgDiv.innerHTML = '<div class="typing-dots"><div></div><div></div><div></div></div>';
        msgDiv.classList.add('typing-indicator');
    } else {
        msgDiv.textContent = text;
    }
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
};

const handleActionFailure = async (action, errorStr) => {
    try {
        await api.logError({ action: JSON.stringify(action), error: errorStr, retry_result: "Pending" });
    } catch (e) {}

    logActivity(`❌ Action failed: ${action.data || action.type}. Retrying...`, 'error');
    appendMessage(`❌ Action failed: ${action.data || action.type}. Retrying in 2 seconds...`, 'failed');
    speak("Something went wrong. Let me try that again.");

    setTimeout(async () => {
        try {
            let result;
            if (action.type === 'open_url' && action.data) {
                window.open(action.data, '_blank');
                result = { status: 'success', action: `open_url:${action.data}` };
            } else if (action.type === 'open_app' && action.data) {
                result = await api.executeAction('open_app', action.data);
            }
            
            if (result && result.status === 'success') {
                logActivity(`✅ Action executed: ${action.data || action.type}`, 'success');
                appendMessage(`✅ Action executed: ${action.data || action.type} (Retry)`, 'success');
                try {
                    await api.logError({ action: JSON.stringify(action), error: errorStr, retry_result: "Success" });
                } catch (e) {}
            } else {
                throw new Error(result ? result.message : 'Unknown error');
            }
        } catch (retryErr) {
            logActivity(`❌ Retry failed: ${action.data || action.type}`, 'error');
            appendMessage(`❌ Action failed: Something went wrong. Skipping this step.`, 'failed');
            speak("Something went wrong. Skipping this step.");
            try {
                await api.logError({ action: JSON.stringify(action), error: errorStr, retry_result: "Failed" });
            } catch (e) {}
        }
    }, 2000);
};

const executeActions = (res) => {
    const handleAction = async (action) => {
        try {
            let result;
            if (action.type === 'open_url' && action.data) {
                logActivity(`Opening URL: ${action.data}`);
                window.open(action.data, '_blank');
                result = { status: 'success', action: `open_url:${action.data}` };
            } else if (action.type === 'open_app' && action.data) {
                logActivity(`Opening App: ${action.data}`);
                result = await api.executeAction('open_app', action.data);
            }
            
            if (result && result.status === 'success') {
                logActivity(`✅ Action executed: ${action.data || action.type}`, 'success');
                appendMessage(`✅ Action executed: ${action.data || action.type}`, 'success');
            } else if (result) {
                handleActionFailure(action, result.message || 'Execution failed');
            }
        } catch (err) {
            console.error('Failed to execute action:', err);
            handleActionFailure(action, err.message || 'Execution failed');
        }
    };

    let maxDelay = 0;

    // Handle multiple actions (Automation Chain)
    if (res.actions && Array.isArray(res.actions)) {
        res.actions.forEach((action, index) => {
            const delay = 1000 * (index + 1);
            if (delay > maxDelay) maxDelay = delay;
            setTimeout(() => handleAction(action), delay);
        });
    }

    // Handle followup (Continuous Flow)
    if (res.followup) {
        setTimeout(() => {
            appendMessage(res.followup, 'assistant');
            speak(res.followup);
        }, maxDelay + 1500);
    }
};

// --- Page Controllers ---

// 1. LOGIN PAGE
const initLogin = () => {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    // Remove old listeners to prevent duplicates
    const newLoginForm = loginForm.cloneNode(true);
    loginForm.parentNode.replaceChild(newLoginForm, loginForm);

    newLoginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        showLoading();
        try {
            const res = await api.login(email, password);
            // Assuming res returns a token
            state.update({ token: res.token || 'mock_token', user: res.user || { email } });
            
            // Load memory after login
            try {
                const memoryData = await api.getMemory();
                console.log('User memory loaded');
            } catch (mErr) {
                console.warn('Could not load memory on login');
            }

            router.navigate('/dashboard');
        } catch (err) {
            showError(err.message);
        } finally {
            hideLoading();
        }
    });
};

// 2. REGISTER PAGE
const initRegister = () => {
    const registerForm = document.getElementById('register-form');
    if (!registerForm) return;

    const newRegisterForm = registerForm.cloneNode(true);
    registerForm.parentNode.replaceChild(newRegisterForm, registerForm);

    newRegisterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(newRegisterForm);
        const data = Object.fromEntries(formData.entries());

        showLoading();
        try {
            await api.register(data);
            router.navigate('/login');
        } catch (err) {
            showError(err.message);
        } finally {
            hideLoading();
        }
    });
};

// 3. CHAT / VOICE
const initChat = () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-messages');

    if (!chatForm || !chatInput || !chatContainer) return;

    const appendMessage = (text, sender) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message message-${sender}`;
        msgDiv.textContent = text;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };

    const newChatForm = chatForm.cloneNode(true);
    chatForm.parentNode.replaceChild(newChatForm, chatForm);

    const micBtn = document.getElementById('mic-btn');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (micBtn && SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-IN';
        recognition.interimResults = false;

        micBtn.addEventListener('click', () => {
            try {
                recognition.start();
                micBtn.style.background = '#e74c3c'; // Red while listening
            } catch (e) {
                console.error('Speech recognition already started');
            }
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const input = newChatForm.querySelector('#chat-input');
            if (input) {
                input.value = transcript;
                newChatForm.dispatchEvent(new Event('submit')); // Auto-trigger send
            }
        };

        recognition.onend = () => {
            micBtn.style.background = '#2ecc71'; // Back to green
        };

        recognition.onerror = (event) => {
            micBtn.style.background = '#2ecc71';
            if (event.error === 'not-allowed') {
                showError('Microphone permission denied.');
            } else {
                console.warn('Speech recognition error:', event.error);
            }
        };
    } else if (micBtn) {
        micBtn.style.display = 'none'; // Hide if not supported
    }

    newChatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        // Since we cloned the form, we must re-query the input inside it
        const input = newChatForm.querySelector('#chat-input') || document.getElementById('chat-input');
        const text = input.value.trim();
        if (!text) return;

        appendMessage(text, 'user');
        input.value = '';
        state.update({ assistantState: 'thinking' });

        // Add typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message message-assistant typing-indicator';
        typingIndicator.textContent = 'Typing...';
        typingIndicator.style.fontStyle = 'italic';
        typingIndicator.style.opacity = '0.7';
        chatContainer.appendChild(typingIndicator);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        showLoading();
        try {
            const res = await api.sendMessage(text);
            if (chatContainer.contains(typingIndicator)) {
                chatContainer.removeChild(typingIndicator);
            }
            appendMessage(res.reply || 'No response', 'assistant');
            speak(res.reply);

            // Handle actions (Automation Chain or Single)
            executeActions(res);
        } catch (err) {
            if (chatContainer.contains(typingIndicator)) {
                chatContainer.removeChild(typingIndicator);
            }
            appendMessage('AI unavailable', 'assistant');
            speak('AI unavailable');
        } finally {
            state.update({ assistantState: 'idle' });
            hideLoading();
        }
    });
};

// 4. VOICE TOGGLE
const initVoiceToggle = () => {
    const voiceToggleBtn = document.getElementById('voice-toggle-btn');
    const voiceIcon = document.getElementById('voice-icon');
    const voiceText = document.getElementById('voice-status-text');

    if (!voiceToggleBtn || !voiceIcon || !voiceText) return;

    const updateUI = () => {
        if (state.voiceEnabled) {
            voiceToggleBtn.style.background = '#9b59b6'; // Purple
            voiceIcon.textContent = 'volume_up';
            voiceText.textContent = 'Voice ON';
        } else {
            voiceToggleBtn.style.background = '#7f8c8d'; // Gray
            voiceIcon.textContent = 'volume_off';
            voiceText.textContent = 'Voice OFF';
            if (window.speechSynthesis) window.speechSynthesis.cancel();
        }
    };

    // Initial UI update
    updateUI();

    const newBtn = voiceToggleBtn.cloneNode(true);
    voiceToggleBtn.parentNode.replaceChild(newBtn, voiceToggleBtn);

    newBtn.addEventListener('click', () => {
        state.update({ voiceEnabled: !state.voiceEnabled });
        updateUI();
    });
};

let lastExecutedActionStr = null;

function handleUserConfirmation(suggestion, confirmed, actionDiv) {
    if (actionDiv) actionDiv.remove();
    
    // Also hide from dashboard panel
    const dashActions = document.getElementById('dash-suggestion-actions');
    if (dashActions) dashActions.style.display = 'none';

    const actionStr = JSON.stringify(suggestion.actions);

    if (confirmed) {
        // Prevent duplicate execution
        if (lastExecutedActionStr === actionStr) {
            appendMessage("Action already executed recently.", "assistant");
            return;
        }
        lastExecutedActionStr = actionStr;

        // Security check against whitelist
        const whitelistApps = ['chrome', 'notepad', 'calc'];
        let isSafe = true;
        for (let a of suggestion.actions) {
            if (a.type === 'open_app' && !whitelistApps.includes(a.data)) {
                isSafe = false;
            }
        }

        if (isSafe) {
            logActivity(`User accepted suggestion`, 'success');
            executeActions(suggestion);
            api.logAction("Executed " + actionStr, "Success");
        } else {
            logActivity(`Blocked unsafe suggestion`, 'error');
            appendMessage("Action blocked by security whitelist.", "assistant");
            api.logAction("Blocked " + actionStr, "Failed (Whitelist)");
        }
    } else {
        logActivity(`User rejected suggestion`, 'info');
        appendMessage("Okay, skipped.", "assistant");
        api.logAction("Skipped " + actionStr, "Cancelled by user");
    }
}

// 4. AUTO MODE TOGGLE & POLLING
const initAutoMode = () => {
    const autoToggleBtns = document.querySelectorAll('#auto-mode-toggle, #auto-mode-toggle-voice');
    const autoExecToggle = document.getElementById('auto-exec-toggle');
    const stopAutoBtn = document.getElementById('stop-auto-exec-btn');

    if (autoToggleBtns.length === 0) return;

    const updateUI = () => {
        autoToggleBtns.forEach(btn => {
            if (state.autoMode) {
                btn.classList.add('active');
                btn.textContent = 'Auto Mode: ON';
                btn.style.display = 'block';
            } else {
                btn.classList.remove('active');
                btn.textContent = 'Auto Mode: OFF';
                if (btn.id === 'auto-mode-toggle-voice') btn.style.display = 'none';
            }
        });

        if (autoExecToggle) {
            if (state.autoExecution) {
                autoExecToggle.classList.add('active');
                autoExecToggle.textContent = 'Auto Exec: ON';
                autoExecToggle.style.background = '#9b59b6';
                if (stopAutoBtn) stopAutoBtn.style.display = 'block';
            } else {
                autoExecToggle.classList.remove('active');
                autoExecToggle.textContent = 'Auto Exec: OFF';
                autoExecToggle.style.background = '#8e44ad';
                if (stopAutoBtn) stopAutoBtn.style.display = 'none';
            }
        }
    };

    updateUI();

    autoToggleBtns.forEach(btn => {
        // Prevent duplicate listeners
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);

        newBtn.addEventListener('click', async () => {
            const newState = !state.autoMode;
            try {
                await api.toggleAutoMode(newState);
                state.update({ autoMode: newState });
                updateUI();
                logActivity(`Auto Mode turned ${newState ? 'ON' : 'OFF'}`);
            } catch (err) {
                showError('Failed to toggle Auto Mode');
            }
        });
    });

    if (autoExecToggle) {
        const newExecBtn = autoExecToggle.cloneNode(true);
        autoExecToggle.parentNode.replaceChild(newExecBtn, autoExecToggle);
        newExecBtn.addEventListener('click', async () => {
            const newState = !state.autoExecution;
            try {
                await api.toggleAutoExec(newState);
                state.update({ autoExecution: newState });
                updateUI();
                logActivity(`Smart Auto Exec turned ${newState ? 'ON' : 'OFF'}`);
            } catch (err) {
                showError('Failed to toggle Auto Execution');
            }
        });
    }

    if (stopAutoBtn) {
        stopAutoBtn.addEventListener('click', async () => {
            try {
                await api.toggleAutoExec(false);
                state.update({ autoExecution: false });
                updateUI();
                logActivity('EMERGENCY: Auto Execution STOPPED', 'error');
                appendMessage('Auto execution has been disabled for safety.', 'assistant');
            } catch (err) {
                showError('Failed to stop Auto Mode');
            }
        });
    }
    
    // Suggestion Polling Loop
    if (!window.autoModeInterval) {
        window.autoModeInterval = setInterval(async () => {
        if (!state.autoMode || state.assistantState !== 'idle') return;

        try {
            const data = await api.getAutoSuggestion();
            if (data && data.suggestion) {
                const suggestion = data.suggestion;
                
                logActivity(`New Auto Suggestion received`);
                
                // Update Dashboard Panel
                const dashLastSug = document.getElementById('dash-last-suggestion');
                const dashSugContent = document.getElementById('dash-suggestion-content');
                const dashSugActions = document.getElementById('dash-suggestion-actions');
                const dashSugReason = document.getElementById('dash-suggestion-reason');
                
                if (dashLastSug) dashLastSug.textContent = suggestion.reply;
                if (dashSugContent) dashSugContent.textContent = suggestion.reply;
                if (dashSugReason && suggestion.reason) dashSugReason.textContent = "💡 Why: " + suggestion.reason;

                // --- Phase 2: Smart Auto Execution ---
                if (suggestion.auto_execute && state.autoExecution) {
                    logActivity(`AUTO-EXECUTING: ${suggestion.reason}`, 'success');
                    
                    let actionData = "action";
                    if (suggestion.actions && suggestion.actions.length > 0) {
                        actionData = suggestion.actions[0].data;
                    } else if (suggestion.executed_action) {
                        actionData = suggestion.executed_action;
                    }
                    
                    const msg = `⚡ Auto executed: ${actionData}`;
                    appendMessage(msg, 'assistant', true);
                    if (suggestion.reason) appendMessage(`💡 Why: ${suggestion.reason}`, 'assistant');
                    speak(msg);
                    
                    if (suggestion.actions && suggestion.actions.length > 0) {
                        executeActions(suggestion);
                        api.logAction("Auto-Executed: " + JSON.stringify(suggestion.actions), "Success (Reason: " + suggestion.reason + ")");
                    } else {
                        api.logAction("Auto-Executed in backend: " + actionData, "Success (Reason: " + suggestion.reason + ")");
                    }
                    return; // Skip confirmation UI
                }

                appendMessage(suggestion.reply, 'assistant', true);
                if (suggestion.reason) appendMessage(`💡 Why: ${suggestion.reason}`, 'assistant');
                speak(suggestion.reply);

                // Show action buttons for the suggestion
                if (suggestion.requires_confirmation && suggestion.actions && suggestion.actions.length > 0) {
                    const chatContainer = document.getElementById('chat-messages');
                    const actionDiv = document.createElement('div');
                    actionDiv.className = 'suggestion-actions';
                    
                    const yesBtn = document.createElement('button');
                    yesBtn.textContent = 'Yes, go ahead';
                    
                    const noBtn = document.createElement('button');
                    noBtn.textContent = 'No thanks';

                    // Dashboard panel buttons
                    if (dashSugActions) {
                        dashSugActions.style.display = 'flex';
                        const dashAccept = document.getElementById('dash-btn-accept');
                        const dashReject = document.getElementById('dash-btn-reject');
                        
                        // Timeout Safety
                        let timeoutId = setTimeout(() => {
                            handleUserConfirmation(suggestion, false, actionDiv);
                        }, 15000); // 15 sec timeout

                        const onAccept = () => {
                            clearTimeout(timeoutId);
                            handleUserConfirmation(suggestion, true, actionDiv);
                        };
                        
                        const onReject = () => {
                            clearTimeout(timeoutId);
                            handleUserConfirmation(suggestion, false, actionDiv);
                        };

                        yesBtn.onclick = onAccept;
                        noBtn.onclick = onReject;
                        if (dashAccept) dashAccept.onclick = onAccept;
                        if (dashReject) dashReject.onclick = onReject;
                    }

                    actionDiv.appendChild(yesBtn);
                    actionDiv.appendChild(noBtn);
                    chatContainer.appendChild(actionDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                } else if (suggestion.actions && suggestion.actions.length > 0) {
                    // Fallback if not flagged explicitly
                    executeActions(suggestion);
                }
            }
        } catch (err) {
            safeWarn('Auto suggestion fetch failed', err);
        }
    }, 20000); // Poll every 20 seconds
    } // closing the if statement correctly
};

// 4. QUICK ACTIONS
const initActions = () => {
    const actionButtons = document.querySelectorAll('.quick-action-btn:not(#btn-self-test)');
    actionButtons.forEach(btn => {
        // Prevent duplicate listeners
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);

        newBtn.addEventListener('click', debounce(async () => {
            const action = newBtn.getAttribute('data-action');
            if (!action) return;

            showLoading();
            try {
                const res = await api.runAction(action);
                // Speak and handle actions for quick buttons too
                if (res.reply) speak(res.reply);
                executeActions(res);
                safeLog('Action result:', res);
            } catch (err) {
                showError(err.message);
            } finally {
                hideLoading();
            }
        }, 300));
    });

    const selfTestBtn = document.getElementById('btn-self-test');
    if (selfTestBtn) {
        const newSelfTestBtn = selfTestBtn.cloneNode(true);
        selfTestBtn.parentNode.replaceChild(newSelfTestBtn, selfTestBtn);

        newSelfTestBtn.addEventListener('click', debounce(async () => {
            showLoading();
            appendMessage("Running self-test...", "user");
            try {
                const res = await api.runSelfTest();
                let reply = `🧪 SYSTEM TEST RESULT (${res.overall_status}):\n`;
                if (res.tests) {
                    res.tests.forEach(t => {
                        const icon = t.status === 'PASS' ? '✔' : '❌';
                        reply += `${icon} ${t.name} - ${t.status}\n`;
                    });
                }
                appendMessage(reply, 'assistant');
                speak(res.overall_status === 'PASS' ? "All systems are functioning normally." : "Self test encountered failures.");
            } catch (err) {
                showError(err.message);
            } finally {
                hideLoading();
            }
        }, 300));
    }

    const fullTestBtn = document.getElementById('btn-full-test');
    if (fullTestBtn) {
        const newFullTestBtn = fullTestBtn.cloneNode(true);
        fullTestBtn.parentNode.replaceChild(newFullTestBtn, fullTestBtn);

        newFullTestBtn.addEventListener('click', debounce(async () => {
            showLoading();
            appendMessage("Running full system integration test...", "user");
            try {
                const res = await api.runFullTest();
                let reply = `🧪 FULL SYSTEM TEST:\n\n`;
                if (res.details) {
                    res.details.forEach(t => {
                        const icon = t.status === 'PASS' ? '✔' : '❌';
                        reply += `${icon} ${t.test} - ${t.status}\n`;
                    });
                }
                reply += `\nScore: ${res.score}`;
                appendMessage(reply, 'assistant');
                speak(res.overall_status === 'PASS' ? "Full integration test passed." : "Integration test encountered failures.");
            } catch (err) {
                showError(err.message);
            } finally {
                hideLoading();
            }
        }, 300));
    }
};

// 5. MEMORY PAGE
const initMemory = async () => {
    const memoryForm = document.getElementById('memory-form');
    const memoryContent = document.getElementById('memory-content');

    if (!memoryForm && !memoryContent) return;

    showLoading();
    try {
        const memoryData = await api.getMemory();
        // Assuming memoryData is text or JSON string for a textarea
        if (memoryContent) {
            memoryContent.value = typeof memoryData === 'object' ? JSON.stringify(memoryData, null, 2) : memoryData;
        }
    } catch (err) {
        showError(err.message);
    } finally {
        hideLoading();
    }

    if (memoryForm) {
        const newMemoryForm = memoryForm.cloneNode(true);
        memoryForm.parentNode.replaceChild(newMemoryForm, memoryForm);

        newMemoryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const content = document.getElementById('memory-content').value;
            let dataToSave = content;
            try {
                dataToSave = JSON.parse(content);
            } catch (e) {
                // Not JSON
            }

            showLoading();
            try {
                await api.saveMemory(dataToSave);
                alert('Memory saved successfully.');
            } catch (err) {
                showError(err.message);
            } finally {
                hideLoading();
            }
        });
    }
};

// 6. SUGGESTIONS
const initSuggestions = async () => {
    const suggestionsContainer = document.getElementById('suggestions-list');
    if (!suggestionsContainer) return;

    showLoading();
    try {
        const data = await api.getSuggestions();
        suggestionsContainer.innerHTML = '';
        const suggestions = data.suggestions || [];
        
        suggestions.forEach(s => {
            const li = document.createElement('li');
            li.textContent = s.text || s;
            li.className = 'suggestion-item';
            suggestionsContainer.appendChild(li);
        });
    } catch (err) {
        showError(err.message);
    } finally {
        hideLoading();
    }
};

// 7. DASHBOARD
const initDashboard = async () => {
    const welcomeMsg = document.getElementById('dashboard-welcome');
    if (welcomeMsg && state.user) {
        const displayName = state.user.name || state.user.email || 'User';
        welcomeMsg.textContent = `Welcome ${displayName}! Your S1 Assistant is ready.`;
    }

    const memContent = document.getElementById('dash-memory-content');
    const btnClearMem = document.getElementById('dash-btn-clearmem');

    if (memContent) {
        try {
            const memoryData = await api.getMemory();
            if (memoryData && memoryData.memory && memoryData.memory.length > 0) {
                let html = '<ul>';
                memoryData.memory.forEach(item => {
                    html += `<li><strong>${item.key}:</strong> ${item.value}</li>`;
                });
                html += '</ul>';
                memContent.innerHTML = html;
            } else {
                memContent.innerHTML = 'No memory data found.';
            }
        } catch (err) {
            memContent.innerHTML = 'Failed to load memory.';
        }
    }

    if (btnClearMem) {
        // Prevent multiple listeners
        const newBtn = btnClearMem.cloneNode(true);
        btnClearMem.parentNode.replaceChild(newBtn, btnClearMem);
        
        newBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear system memory?')) return;
            try {
                await api.saveMemory({ user_id: 'default', memory: [] });
                logActivity('Cleared System Memory', 'info');
                if (memContent) memContent.innerHTML = 'No memory data found.';
            } catch (err) {
                showError('Failed to clear memory');
            }
        });
    }
};

// --- Core Initialization ---
const initApp = () => {
    router.init();

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            state.logout();
            router.navigate('/login');
        });
    }

    window.addEventListener('authChanged', () => {
        if (!state.isAuthenticated) {
            router.navigate('/login');
        }
    });

    window.addEventListener('tokenExpired', () => {
        state.logout();
        showError('Session expired. Please login again.');
        router.navigate('/login');
    });

    // Listen to route changes to initialize page-specific logic
    window.addEventListener('routeChanged', (e) => {
        const path = e.detail.path;
        
        // Always initialize navigation elements that might be shared across pages
        initActions();
        
        switch (path) {
            case '/login':
                initLogin();
                break;
            case '/register':
                initRegister();
                break;
            case '/dashboard':
                initDashboard();
                initChat(); // Some UI might still have chat here
                initAutoMode();
                break;
            case '/voice':
                initChat();
                initVoiceToggle();
                initAutoMode();
                break;
            case '/memory':
                initMemory();
                break;
            case '/suggestions':
                initSuggestions();
                break;
            case '/actions':
                initActions();
                break;
        }
    });
};

document.addEventListener('DOMContentLoaded', initApp);
