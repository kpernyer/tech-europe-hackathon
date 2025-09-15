/**
 * Debug Helper for Weaviate Demo Frontend
 * Comprehensive debugging utilities for HTML/JS application
 */

class WeaviateDebugger {
    constructor() {
        this.debugMode = true;
        this.logs = [];
        this.errors = [];
        this.apiCalls = [];
        this.init();
    }

    init() {
        if (this.debugMode) {
            this.setupConsoleEnhancement();
            this.setupErrorHandling();
            this.setupNetworkMonitoring();
            this.setupPerformanceMonitoring();
            console.log('🔍 Weaviate Debugger initialized');
        }
    }

    setupConsoleEnhancement() {
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;

        console.log = (...args) => {
            this.logs.push({ type: 'log', timestamp: new Date(), message: args });
            originalLog('📝', ...args);
        };

        console.error = (...args) => {
            this.errors.push({ type: 'error', timestamp: new Date(), message: args });
            originalError('❌', ...args);
        };

        console.warn = (...args) => {
            this.logs.push({ type: 'warn', timestamp: new Date(), message: args });
            originalWarn('⚠️', ...args);
        };
    }

    setupErrorHandling() {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.errors.push({
                type: 'global-error',
                timestamp: new Date(),
                message: event.error?.message || 'Unknown error',
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                stack: event.error?.stack
            });
            console.error('🚨 Global Error:', event.error);
        });

        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.errors.push({
                type: 'unhandled-promise',
                timestamp: new Date(),
                message: event.reason?.message || 'Unhandled promise rejection',
                stack: event.reason?.stack
            });
            console.error('🚨 Unhandled Promise Rejection:', event.reason);
        });
    }

    setupNetworkMonitoring() {
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = performance.now();
            const url = args[0];
            const options = args[1] || {};

            console.log('📡 API Call:', {
                url,
                method: options.method || 'GET',
                timestamp: new Date()
            });

            try {
                const response = await originalFetch(...args);
                const endTime = performance.now();
                const duration = endTime - startTime;

                this.apiCalls.push({
                    url,
                    method: options.method || 'GET',
                    status: response.status,
                    duration,
                    timestamp: new Date(),
                    success: response.ok
                });

                console.log('✅ API Response:', {
                    url,
                    status: response.status,
                    duration: `${duration.toFixed(2)}ms`,
                    success: response.ok
                });

                return response;
            } catch (error) {
                const endTime = performance.now();
                const duration = endTime - startTime;

                this.apiCalls.push({
                    url,
                    method: options.method || 'GET',
                    status: 'ERROR',
                    duration,
                    timestamp: new Date(),
                    success: false,
                    error: error.message
                });

                console.error('❌ API Error:', {
                    url,
                    error: error.message,
                    duration: `${duration.toFixed(2)}ms`
                });

                throw error;
            }
        };
    }

    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('📊 Page Performance:', {
                loadTime: `${perfData.loadEventEnd - perfData.loadEventStart}ms`,
                domContentLoaded: `${perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart}ms`,
                firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 'N/A'
            });
        });
    }

    // Debug methods
    logWeaviateConnection() {
        console.log('🔗 Weaviate Connection Check:', {
            baseUrl: 'http://localhost:8080',
            endpoints: [
                '/v1/meta',
                '/v1/schema',
                '/v1/graphql',
                '/v1/objects'
            ]
        });
    }

    async testWeaviateConnection() {
        try {
            console.log('🧪 Testing Weaviate connection...');
            
            const response = await fetch('http://localhost:8080/v1/meta');
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Weaviate Connected:', data);
                return true;
            } else {
                console.error('❌ Weaviate Connection Failed:', response.status);
                return false;
            }
        } catch (error) {
            console.error('❌ Weaviate Connection Error:', error.message);
            return false;
        }
    }

    async testGraphQLQuery() {
        try {
            console.log('🧪 Testing GraphQL query...');
            
            const query = {
                query: `
                {
                    Get {
                        BusinessDocument {
                            title
                            _additional {
                                id
                            }
                        }
                    }
                }
                `
            };

            const response = await fetch('http://localhost:8080/v1/graphql', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(query)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ GraphQL Query Success:', data);
                return data;
            } else {
                const errorData = await response.json();
                console.error('❌ GraphQL Query Failed:', errorData);
                return null;
            }
        } catch (error) {
            console.error('❌ GraphQL Query Error:', error.message);
            return null;
        }
    }

    getDebugReport() {
        return {
            logs: this.logs.slice(-50), // Last 50 logs
            errors: this.errors,
            apiCalls: this.apiCalls.slice(-20), // Last 20 API calls
            timestamp: new Date(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };
    }

    exportDebugReport() {
        const report = this.getDebugReport();
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `weaviate-debug-report-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        console.log('📄 Debug report exported');
    }

    showDebugPanel() {
        const panel = document.createElement('div');
        panel.id = 'debug-panel';
        panel.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 300px;
            max-height: 400px;
            background: #1a1a1a;
            color: #00ff00;
            font-family: monospace;
            font-size: 12px;
            padding: 10px;
            border-radius: 5px;
            z-index: 10000;
            overflow-y: auto;
            border: 1px solid #333;
        `;

        panel.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <strong>🔍 Debug Panel</strong>
                <button onclick="this.parentElement.parentElement.remove()" style="background: #ff4444; color: white; border: none; padding: 2px 6px; border-radius: 3px; cursor: pointer;">×</button>
            </div>
            <div id="debug-content">
                <div>📊 Logs: ${this.logs.length}</div>
                <div>❌ Errors: ${this.errors.length}</div>
                <div>📡 API Calls: ${this.apiCalls.length}</div>
                <div style="margin-top: 10px;">
                    <button onclick="debugger.testWeaviateConnection()" style="background: #444; color: white; border: none; padding: 5px; margin: 2px; border-radius: 3px; cursor: pointer;">Test Weaviate</button>
                    <button onclick="debugger.testGraphQLQuery()" style="background: #444; color: white; border: none; padding: 5px; margin: 2px; border-radius: 3px; cursor: pointer;">Test GraphQL</button>
                    <button onclick="debugger.exportDebugReport()" style="background: #444; color: white; border: none; padding: 5px; margin: 2px; border-radius: 3px; cursor: pointer;">Export Report</button>
                </div>
            </div>
        `;

        document.body.appendChild(panel);
    }
}

// Initialize debugger
const debugger = new WeaviateDebugger();

// Make it globally available
window.weaviateDebugger = debugger;

// Auto-show debug panel in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    setTimeout(() => {
        debugger.showDebugPanel();
    }, 1000);
}