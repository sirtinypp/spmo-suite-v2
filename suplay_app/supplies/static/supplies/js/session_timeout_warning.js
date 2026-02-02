// Session Timeout Warning System
// Implements auto-logout with extension capability
// Usage: Include in base template and call initSessionTimeout() on page load

(function () {
    'use strict';

    const CONFIG = {
        sessionTimeout: 10 * 60 * 1000,      // 10 minutes in milliseconds
        warningTime: 9 * 60 * 1000,           // Show warning at 9 minutes (1 min before timeout)
        autoLogoutDelay: 60 * 1000,           // Auto-logout 1 minute after warning if no action
        extensionTime: 10 * 60 * 1000,        // Extension adds 10 more minutes
        checkInterval: 1000                    // Check every second
    };

    let warningTimer = null;
    let logoutTimer = null;
    let countdownInterval = null;
    let lastActivity = Date.now();
    let warningShown = false;

    // Create warning modal HTML
    function createWarningModal() {
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
                            🔄 Extend Session (+10 min)
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
        style.textContent = `
            .session-timeout-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 99999;
                animation: fadeIn 0.3s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .session-timeout-dialog {
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                max-width: 500px;
                width: 90%;
                animation: slideIn 0.3s ease-out;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateY(-50px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .session-timeout-header {
                background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                color: white;
                padding: 20px;
                border-radius: 12px 12px 0 0;
                text-align: center;
            }
            
            .session-timeout-header h3 {
                margin: 0;
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .session-timeout-body {
                padding: 30px;
                text-align: center;
            }
            
            .session-timeout-body p {
                margin: 10px 0;
                color: #374151;
                font-size: 1rem;
            }
            
            .session-timeout-countdown {
                font-size: 1.25rem;
                font-weight: 700;
                color: #dc2626;
                margin: 20px 0 !important;
                padding: 15px;
                background: #fef2f2;
                border-radius: 8px;
                border: 2px solid #fecaca;
            }
            
            #countdown-timer {
                font-size: 2rem;
                color: #b91c1c;
            }
            
            .session-timeout-hint {
                font-size: 0.875rem;
                color: #6b7280;
            }
            
            .session-timeout-footer {
                padding: 20px 30px 30px;
                display: flex;
                gap: 10px;
                justify-content: center;
            }
            
            .session-timeout-footer button {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                flex: 1;
                max-width: 200px;
            }
            
            .btn-extend {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
            }
            
            .btn-extend:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(16, 185, 129, 0.4);
            }
            
            .btn-logout {
                background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
                color: white;
                box-shadow: 0 4px 6px rgba(107, 114, 128, 0.3);
            }
            
            .btn-logout:hover {
                background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(107, 114, 128, 0.4);
            }
        `;

        document.head.appendChild(style);
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

        countdownInterval = setInterval(() => {
            secondsLeft--;
            timerElement.textContent = secondsLeft;

            if (secondsLeft <= 0) {
                clearInterval(countdownInterval);
                logoutNow();
            }
        }, 1000);
    }

    // Hide warning modal
    function hideWarning() {
        const modal = document.getElementById('session-timeout-modal');
        if (modal) {
            modal.remove();
        }
        if (countdownInterval) {
            clearInterval(countdownInterval);
        }
        warningShown = false;
    }

    // Extend session - adds 10 more minutes
    function extendSession() {
        // Reset activity timestamp
        lastActivity = Date.now();

        // Make AJAX call to keep session alive
        fetch(window.location.href, {
            method: 'HEAD',
            credentials: 'same-origin'
        }).then(() => {
            console.log('Session extended');
        }).catch(err => {
            console.error('Failed to extend session:', err);
        });

        // Hide warning
        hideWarning();

        // Restart timers
        resetTimers();

        // Show brief confirmation
        showExtensionConfirmation();
    }

    // Show confirmation that session was extended
    function showExtensionConfirmation() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            z-index: 100000;
            animation: slideInRight 0.3s ease-out;
            font-weight: 600;
        `;
        notification.innerHTML = '✅ Session extended by 10 minutes';
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }, 3000);

        // Add animation keyframes
        if (!document.getElementById('notification-animations')) {
            const style = document.createElement('style');
            style.id = 'notification-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Logout immediately
    function logoutNow() {
        // Redirect to logout URL (Django standard)
        window.location.href = '/logout/';
    }

    // Reset all timers
    function resetTimers() {
        if (warningTimer) clearTimeout(warningTimer);
        if (logoutTimer) clearTimeout(logoutTimer);

        warningTimer = setTimeout(showWarning, CONFIG.warningTime);
    }

    // Track user activity
    function trackActivity() {
        lastActivity = Date.now();
        if (!warningShown) {
            resetTimers();
        }
    }

    // Initialize the session timeout system
    function initSessionTimeout() {
        // Track various user activities
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        events.forEach(event => {
            document.addEventListener(event, trackActivity, { passive: true });
        });

        // Start initial timer
        resetTimers();

        console.log('Session timeout system initialized: 10-minute inactivity timeout');
    }

    // Expose init function globally
    window.initSessionTimeout = initSessionTimeout;

})();
