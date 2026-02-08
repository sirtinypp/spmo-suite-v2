/**
 * Session Timeout Warning System (Standardized)
 * Implements auto-logout with extension capability and configurable redirect.
 * 
 * Usage: 
 * 1. Include this script in your base template.
 * 2. Initialize with configuration:
 *    initSessionTimeout({
 *        logoutUrl: '/logout/',
 *        loginUrl: '/login/',
 *        sessionMinutes: 10,
 *        warningMinutes: 9
 *    });
 */

(function () {
    'use strict';

    let CONFIG = {
        sessionTimeout: 10 * 60 * 1000,      // Default: 10 minutes
        warningTime: 9 * 60 * 1000,          // Default: Warning at 9 minutes
        autoLogoutDelay: 60 * 1000,          // Time between warning and logout
        checkInterval: 1000,                 // Check every second
        logoutUrl: '/logout/',               // Default logout URL
        loginUrl: '/login/'                  // Default login URL (for redirect)
    };

    let warningTimer = null;
    let logoutTimer = null;
    let countdownInterval = null;
    let lastActivity = Date.now();
    let warningShown = false;

    // Create warning modal HTML
    function createWarningModal() {
        // Prevent duplicate modals
        if (document.getElementById('session-timeout-modal')) return;

        const modal = document.createElement('div');
        modal.id = 'session-timeout-modal';
        modal.innerHTML = `
            <div class="session-timeout-overlay">
                <div class="session-timeout-dialog">
                    <div class="session-timeout-header">
                        <h3>⚠️ Session Expiring Soon</h3>
                    </div>
                    <div class="session-timeout-body">
                        <p>Your session will expire due to inactivity.</p>
                        <p class="session-timeout-countdown">
                            Time remaining: <span id="countdown-timer">60</span> seconds
                        </p>
                        <p class="session-timeout-hint">Click "Extend Session" to continue working, or you will be logged out automatically.</p>
                    </div>
                    <div class="session-timeout-footer">
                        <button id="extend-session-btn" class="btn-extend">
                            🔄 Extend Session
                        </button>
                        <button id="logout-now-btn" class="btn-logout">
                            🚪 Logout Now
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.id = 'session-timeout-styles';
        style.textContent = `
            .session-timeout-overlay {
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex; align-items: center; justify-content: center;
                z-index: 99999; animation: fadeIn 0.3s ease-in;
            }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            
            .session-timeout-dialog {
                background: white; border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                max-width: 450px; width: 90%;
                animation: slideIn 0.3s ease-out; font-family: 'Inter', system-ui, sans-serif;
            }
            @keyframes slideIn { from { transform: translateY(-30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            
            .session-timeout-header {
                background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
                color: white; padding: 16px 20px;
                border-radius: 12px 12px 0 0; text-align: center;
            }
            .session-timeout-header h3 { margin: 0; font-size: 1.25rem; font-weight: 600; }
            
            .session-timeout-body { padding: 24px; text-align: center; }
            .session-timeout-body p { margin: 8px 0; color: #4b5563; }
            
            .session-timeout-countdown {
                font-size: 1.1rem; font-weight: 700; color: #b91c1c;
                margin: 16px 0 !important; padding: 12px;
                background: #fef2f2; border-radius: 8px; border: 1px solid #fecaca;
            }
            #countdown-timer { font-size: 1.5rem; font-weight: 800; }
            
            .session-timeout-hint { font-size: 0.85rem; color: #6b7280; }
            
            .session-timeout-footer {
                padding: 0 24px 24px; display: flex; gap: 12px; justify-content: center;
            }
            .session-timeout-footer button {
                padding: 10px 20px; border: none; border-radius: 6px;
                font-size: 0.95rem; font-weight: 600; cursor: pointer;
                transition: transform 0.1s, opacity 0.2s; flex: 1;
            }
            .session-timeout-footer button:active { transform: scale(0.98); }
            
            .btn-extend { background: #10b981; color: white; }
            .btn-extend:hover { background: #059669; }
            
            .btn-logout { background: #6b7280; color: white; }
            .btn-logout:hover { background: #4b5563; }
        `;

        if (!document.getElementById('session-timeout-styles')) {
            document.head.appendChild(style);
        }
        document.body.appendChild(modal);

        // Attach event listeners
        document.getElementById('extend-session-btn').addEventListener('click', extendSession);
        document.getElementById('logout-now-btn').addEventListener('click', logoutNow);
    }

    // Show warning modal
    function showWarning() {
        if (warningShown) return;

        warningShown = true;
        createWarningModal();

        // Start countdown
        let secondsLeft = 60;
        const timerElement = document.getElementById('countdown-timer');
        if (timerElement) timerElement.textContent = secondsLeft;

        countdownInterval = setInterval(() => {
            secondsLeft--;
            if (timerElement) timerElement.textContent = secondsLeft;

            if (secondsLeft <= 0) {
                clearInterval(countdownInterval);
                logoutNow();
            }
        }, 1000);
    }

    // Hide warning modal
    function hideWarning() {
        const modal = document.getElementById('session-timeout-modal');
        if (modal) modal.remove();

        if (countdownInterval) clearInterval(countdownInterval);
        warningShown = false;
    }

    // Extend session
    function extendSession() {
        // Reset activity timestamp
        lastActivity = Date.now();

        // Make AJAX call to keep session alive
        fetch(window.location.href, {
            method: 'HEAD',
            credentials: 'same-origin'
        }).then(() => {
            console.log('[Session] Extended via heartbeat.');
        }).catch(err => {
            console.error('[Session] Heartbeat failed:', err);
        });

        hideWarning();
        resetTimers();
    }

    // Logout immediately
    function logoutNow() {
        console.log('[Session] Expired. Initiating secure logout sequence...');

        // Construct the logout URL with the ?next= parameter
        // This ensures that after logout, the server redirects the user to the specific login page
        // rather than the default LOGIN_REDIRECT_URL or root.
        let targetLogoutUrl = CONFIG.logoutUrl;
        if (CONFIG.loginUrl) {
            // Check if ? already exists
            const separator = targetLogoutUrl.includes('?') ? '&' : '?';
            targetLogoutUrl = `${targetLogoutUrl}${separator}next=${encodeURIComponent(CONFIG.loginUrl)}`;
        }

        // Create a hidden form to perform a POST logout (Django standard)
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = targetLogoutUrl;

        // Add CSRF token if available
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = csrfToken.value;
            form.appendChild(input);
        } else {
            console.warn('[Session] CSRF token not found. Attempting logout without token...');
        }

        document.body.appendChild(form);
        form.submit();
    }

    // Reset all timers
    function resetTimers() {
        if (warningTimer) clearTimeout(warningTimer);

        // Calculate milliseconds for warning
        warningTimer = setTimeout(showWarning, CONFIG.warningTime);
    }

    // Track user activity
    function trackActivity() {
        lastActivity = Date.now();
        if (!warningShown) {
            // Debounce the timer reset to avoid excessive processing
            if (warningTimer) clearTimeout(warningTimer);
            warningTimer = setTimeout(showWarning, CONFIG.warningTime);
        }
    }

    // Initialize the session timeout system with custom config
    function initSessionTimeout(options) {
        // Merge defaults with user options
        if (options) {
            Object.assign(CONFIG, options);

            // Recalculate times if minutes were provided
            if (options.sessionMinutes) {
                CONFIG.sessionTimeout = options.sessionMinutes * 60 * 1000;
            }
            if (options.warningMinutes) {
                CONFIG.warningTime = options.warningMinutes * 60 * 1000;
            }
        }

        // Track various user activities
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        events.forEach(event => {
            document.addEventListener(event, trackActivity, { passive: true });
        });

        // Start initial timer
        resetTimers();

        console.log(`[Session] Monitor active. Timeout: ${CONFIG.sessionTimeout / 1000 / 60}m. Redirect -> ${CONFIG.loginUrl}`);
    }

    // Expose init function globally
    window.initSessionTimeout = initSessionTimeout;

})();
