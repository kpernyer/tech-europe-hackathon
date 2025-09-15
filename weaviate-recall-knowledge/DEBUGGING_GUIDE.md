# 🔍 Frontend Debugging Guide for Weaviate Demo

## Overview

This guide provides comprehensive debugging strategies for your HTML/JavaScript Weaviate demo application. While this isn't a React project, the debugging principles are similar and can be applied to any frontend application.

## 🚀 Quick Start Debugging

### 1. **Use the Enhanced Debug Version**
```bash
# Open the debug-enhanced version
open enhanced_demo_with_debug.html
```

### 2. **Enable Browser Developer Tools**
- **Chrome/Edge**: `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
- **Firefox**: `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
- **Safari**: `Cmd+Option+I` (Mac, requires enabling Developer menu)

### 3. **Run Quick Diagnostics**
Click the "Run Full Diagnostics" button in the debug panel to test:
- ✅ Weaviate connection
- ✅ GraphQL queries
- ✅ OpenAI API key
- ✅ Network status

## 🔧 Debug Tools & Techniques

### **1. Console Debugging**

#### Enhanced Console Logging
```javascript
// Add to your JavaScript files
console.log('🔍 Debug Mode Enabled');
console.log('📡 API Calls:', {
    weaviate: 'http://localhost:8080',
    openai: 'https://api.openai.com/v1/chat/completions'
});

// Network monitoring
console.log('📨 Weaviate Response Status:', response.status);
console.log('📋 Raw Weaviate Response:', JSON.stringify(data, null, 2));
```

#### Error Tracking
```javascript
// Global error handler
window.addEventListener('error', (event) => {
    console.error('🚨 Global Error:', {
        message: event.error?.message,
        filename: event.filename,
        line: event.lineno,
        column: event.colno,
        stack: event.error?.stack
    });
});

// Promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('🚨 Unhandled Promise Rejection:', event.reason);
});
```

### **2. Network Debugging**

#### Monitor API Calls
```javascript
// Enhanced fetch monitoring
const originalFetch = window.fetch;
window.fetch = async (...args) => {
    const startTime = performance.now();
    const url = args[0];
    
    console.log('📡 API Call:', {
        url,
        method: args[1]?.method || 'GET',
        timestamp: new Date()
    });
    
    try {
        const response = await originalFetch(...args);
        const duration = performance.now() - startTime;
        
        console.log('✅ API Response:', {
            url,
            status: response.status,
            duration: `${duration.toFixed(2)}ms`,
            success: response.ok
        });
        
        return response;
    } catch (error) {
        console.error('❌ API Error:', {
            url,
            error: error.message,
            duration: `${performance.now() - startTime}ms`
        });
        throw error;
    }
};
```

### **3. Weaviate-Specific Debugging**

#### Connection Testing
```javascript
async function testWeaviateConnection() {
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
```

#### GraphQL Query Debugging
```javascript
async function debugGraphQLQuery(query) {
    console.log('📡 Weaviate GraphQL Query:', JSON.stringify(query, null, 2));
    
    const response = await fetch('http://localhost:8080/v1/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(query)
    });
    
    console.log('📨 Weaviate Response Status:', response.status);
    
    if (response.ok) {
        const data = await response.json();
        console.log('📋 Raw Weaviate Response:', JSON.stringify(data, null, 2));
        return data;
    } else {
        const errorData = await response.json();
        console.error('❌ Weaviate GraphQL Error:', errorData);
        return null;
    }
}
```

### **4. Performance Debugging**

#### Monitor Page Load Performance
```javascript
window.addEventListener('load', () => {
    const perfData = performance.getEntriesByType('navigation')[0];
    console.log('📊 Page Performance:', {
        loadTime: `${perfData.loadEventEnd - perfData.loadEventStart}ms`,
        domContentLoaded: `${perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart}ms`,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 'N/A'
    });
});
```

#### Monitor Function Execution Time
```javascript
function measureFunction(func, name) {
    return async (...args) => {
        const startTime = performance.now();
        console.log(`⏱️ Starting ${name}...`);
        
        try {
            const result = await func(...args);
            const duration = performance.now() - startTime;
            console.log(`✅ ${name} completed in ${duration.toFixed(2)}ms`);
            return result;
        } catch (error) {
            const duration = performance.now() - startTime;
            console.error(`❌ ${name} failed after ${duration.toFixed(2)}ms:`, error);
            throw error;
        }
    };
}

// Usage
const debugAskQuestion = measureFunction(askQuestion, 'askQuestion');
```

## 🐛 Common Issues & Solutions

### **1. Weaviate Connection Issues**

#### Problem: "Failed to fetch" or CORS errors
```javascript
// Check if Weaviate is running
async function checkWeaviateStatus() {
    try {
        const response = await fetch('http://localhost:8080/v1/meta');
        if (response.ok) {
            console.log('✅ Weaviate is running');
            return true;
        }
    } catch (error) {
        console.error('❌ Weaviate is not accessible:', error.message);
        console.log('💡 Solutions:');
        console.log('  1. Start Weaviate: docker-compose up -d weaviate');
        console.log('  2. Check port 8080 is not blocked');
        console.log('  3. Verify docker-compose.yml configuration');
        return false;
    }
}
```

#### Problem: GraphQL schema errors
```javascript
// Check if BusinessDocument class exists
async function checkSchema() {
    try {
        const response = await fetch('http://localhost:8080/v1/schema');
        const schema = await response.json();
        const businessDocClass = schema.classes.find(cls => cls.class === 'BusinessDocument');
        
        if (businessDocClass) {
            console.log('✅ BusinessDocument class exists:', businessDocClass);
        } else {
            console.error('❌ BusinessDocument class not found');
            console.log('💡 Run: python step2_schema.py to create schema');
        }
    } catch (error) {
        console.error('❌ Schema check failed:', error.message);
    }
}
```

### **2. OpenAI API Issues**

#### Problem: API key not working
```javascript
async function testOpenAIKey() {
    const OPENAI_API_KEY = 'your-openai-api-key-here';
    
    if (OPENAI_API_KEY === 'your-openai-api-key-here') {
        console.error('❌ OpenAI API key not configured');
        console.log('💡 Set your OpenAI API key in the code');
        return false;
    }
    
    try {
        const response = await fetch('https://api.openai.com/v1/models', {
            headers: {
                'Authorization': `Bearer ${OPENAI_API_KEY}`,
            }
        });
        
        if (response.ok) {
            console.log('✅ OpenAI API key is valid');
            return true;
        } else {
            console.error('❌ OpenAI API key test failed:', response.status);
            return false;
        }
    } catch (error) {
        console.error('❌ OpenAI API test error:', error.message);
        return false;
    }
}
```

### **3. Frontend JavaScript Issues**

#### Problem: Functions not working
```javascript
// Add function existence checks
function safeCall(func, ...args) {
    if (typeof func === 'function') {
        try {
            return func(...args);
        } catch (error) {
            console.error(`❌ Function ${func.name} failed:`, error);
            return null;
        }
    } else {
        console.error(`❌ Function ${func} is not defined`);
        return null;
    }
}

// Usage
safeCall(askQuestion);
safeCall(injectNextDocument);
```

#### Problem: DOM elements not found
```javascript
function safeGetElement(id) {
    const element = document.getElementById(id);
    if (element) {
        return element;
    } else {
        console.error(`❌ Element with id '${id}' not found`);
        return null;
    }
}

// Usage
const responseArea = safeGetElement('response-area');
if (responseArea) {
    responseArea.innerHTML = 'Content';
}
```

## 🔍 Advanced Debugging Techniques

### **1. State Management Debugging**

```javascript
// Track application state changes
class StateTracker {
    constructor() {
        this.state = {};
        this.listeners = [];
    }
    
    setState(newState) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...newState };
        
        console.log('🔄 State Changed:', {
            old: oldState,
            new: this.state,
            timestamp: new Date()
        });
        
        this.listeners.forEach(listener => listener(this.state, oldState));
    }
    
    getState() {
        return { ...this.state };
    }
    
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }
}

// Usage
const appState = new StateTracker();
appState.setState({ documentsInjected: 0 });
```

### **2. Event Debugging**

```javascript
// Monitor all click events
document.addEventListener('click', (event) => {
    console.log('🖱️ Click Event:', {
        target: event.target.tagName,
        id: event.target.id,
        class: event.target.className,
        text: event.target.textContent?.substring(0, 50)
    });
});

// Monitor all form submissions
document.addEventListener('submit', (event) => {
    console.log('📝 Form Submit:', {
        action: event.target.action,
        method: event.target.method,
        data: new FormData(event.target)
    });
});
```

### **3. Memory Leak Detection**

```javascript
// Monitor memory usage
function checkMemoryUsage() {
    if (performance.memory) {
        console.log('🧠 Memory Usage:', {
            used: `${(performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
            total: `${(performance.memory.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
            limit: `${(performance.memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`
        });
    }
}

// Run memory check every 30 seconds
setInterval(checkMemoryUsage, 30000);
```

## 📊 Debug Reporting

### **Export Debug Information**
```javascript
function exportDebugReport() {
    const report = {
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        errors: window.debugger?.errors || [],
        apiCalls: window.debugger?.apiCalls || [],
        performance: {
            loadTime: performance.now(),
            memory: performance.memory ? {
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize
            } : null
        },
        weaviateStatus: await testWeaviateConnection(),
        graphqlStatus: await testGraphQLQuery()
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weaviate-debug-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}
```

## 🚀 Quick Debug Checklist

### **Before Starting Debugging:**
- [ ] Open browser developer tools (F12)
- [ ] Check console for errors
- [ ] Verify Weaviate is running (`docker-compose up -d weaviate`)
- [ ] Test network connectivity
- [ ] Check if OpenAI API key is configured

### **During Debugging:**
- [ ] Use `console.log()` for step-by-step tracking
- [ ] Monitor Network tab for API calls
- [ ] Check Elements tab for DOM issues
- [ ] Use Sources tab for breakpoints
- [ ] Monitor Performance tab for bottlenecks

### **After Debugging:**
- [ ] Export debug report
- [ ] Document the issue and solution
- [ ] Test the fix thoroughly
- [ ] Clean up debug code if needed

## 🎯 Specific Debug Scenarios

### **Scenario 1: "Documents not loading"**
```javascript
async function debugDocumentLoading() {
    console.log('🔍 Debugging document loading...');
    
    // Step 1: Check Weaviate connection
    const weaviateOk = await testWeaviateConnection();
    if (!weaviateOk) return;
    
    // Step 2: Check GraphQL query
    const query = {
        query: `{ Get { BusinessDocument { title content } } }`
    };
    const result = await debugGraphQLQuery(query);
    
    // Step 3: Check if documents exist
    if (result?.data?.Get?.BusinessDocument?.length === 0) {
        console.log('💡 No documents found. Run: python step3_add_data.py');
    }
}
```

### **Scenario 2: "AI responses not working"**
```javascript
async function debugAIResponses() {
    console.log('🔍 Debugging AI responses...');
    
    // Step 1: Check OpenAI API key
    const openaiOk = await testOpenAIKey();
    if (!openaiOk) return;
    
    // Step 2: Check document retrieval
    const docs = await retrieveAllDocuments();
    console.log(`📄 Retrieved ${docs.length} documents`);
    
    // Step 3: Check semantic search
    const searchResults = await performSemanticSearch("test query", 3);
    console.log(`🔍 Semantic search found ${searchResults.length} results`);
}
```

## 📚 Additional Resources

- **Browser DevTools Documentation**: [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools)
- **JavaScript Debugging**: [MDN Debugging Guide](https://developer.mozilla.org/en-US/docs/Learn/Common_questions/What_are_browser_developer_tools)
- **Weaviate Documentation**: [Weaviate Docs](https://weaviate.io/developers/weaviate)
- **OpenAI API Documentation**: [OpenAI API Docs](https://platform.openai.com/docs)

---

**Remember**: The key to effective debugging is systematic investigation. Start with the most likely causes and work your way through the possibilities. Use the enhanced debug version of your application for the best debugging experience!