#!/usr/bin/env node
/**
 * SentryPrime Enterprise - Google Cloud Run Scanner
 * Pure Node.js service with Puppeteer + axe-core
 * Designed for enterprise-grade reliability and performance
 */

const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());

// Load axe-core from node_modules
const axeCoreSource = fs.readFileSync(
    path.join(__dirname, 'node_modules', 'axe-core', 'axe.min.js'),
    'utf8'
);

// Enterprise Dashboard HTML
const DASHBOARD_HTML = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SentryPrime Enterprise - Google Cloud Run</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 48px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .gcp-badge {
            background: linear-gradient(45deg, #4285f4, #34a853);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            display: inline-block;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .scan-form {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .form-group {
            margin: 20px 0;
        }
        
        .form-group input {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            background: rgba(255,255,255,0.9);
            color: #333;
        }
        
        .btn {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .results {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 15px;
            margin-top: 20px;
            display: none;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .score {
            font-size: 72px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .feature-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .feature-icon {
            font-size: 40px;
            margin-bottom: 15px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 3px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .violation-item {
            background: rgba(255,255,255,0.1);
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ff6b6b;
        }
        
        .success-badge {
            background: rgba(40,167,69,0.2);
            border: 1px solid #28a745;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SentryPrime Enterprise</h1>
            <p>Enterprise-grade accessibility scanning with real Puppeteer + axe-core technology</p>
            <div class="gcp-badge">☁️ POWERED BY GOOGLE CLOUD RUN - Real Scanning Active</div>
        </div>
        
        <div class="scan-form">
            <h2>Start Real Accessibility Scan</h2>
            <div class="form-group">
                <input type="url" id="urlInput" placeholder="https://example.com" value="https://example.com">
            </div>
            <button class="btn" id="scanBtn" onclick="startScan()">🚀 Start Google Cloud Scan</button>
        </div>
        
        <div id="results" class="results">
            <div id="resultsContent"></div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <h3>Real Browser Scanning</h3>
                <p>Uses genuine Puppeteer automation with Chrome browser for authentic accessibility testing</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3>axe-core Engine</h3>
                <p>Powered by the industry-standard axe-core library used by Microsoft, Google, and major enterprises</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">☁️</div>
                <h3>Google Cloud Infrastructure</h3>
                <p>Enterprise-grade reliability and performance with automatic scaling and 99.95% uptime</p>
            </div>
        </div>
    </div>
    
    <script>
        async function startScan() {
            const urlInput = document.getElementById('urlInput');
            const scanBtn = document.getElementById('scanBtn');
            const resultsDiv = document.getElementById('results');
            const resultsContent = document.getElementById('resultsContent');
            
            const url = urlInput.value.trim();
            if (!url) {
                alert('Please enter a valid URL');
                return;
            }
            
            // Show loading state
            scanBtn.disabled = true;
            scanBtn.textContent = 'Scanning...';
            resultsDiv.style.display = 'block';
            resultsContent.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <h3>🔄 Performing Google Cloud Real Scan...</h3>
                    <p>Using genuine Puppeteer + axe-core on Google Cloud Run infrastructure</p>
                    <p><small>This may take 5-15 seconds</small></p>
                </div>
            `;
            
            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const data = result.data;
                    const scoreColor = data.score >= 80 ? '#28a745' : data.score >= 60 ? '#ffc107' : '#dc3545';
                    
                    resultsContent.innerHTML = `
                        <h2>✅ Google Cloud Real Scan Completed!</h2>
                        <div class="score" style="color: ${scoreColor}">${data.score}/100</div>
                        <p><strong>URL:</strong> ${data.url}</p>
                        <p><strong>WCAG Level:</strong> ${data.wcagLevel}</p>
                        <p><strong>Violations Found:</strong> ${data.violations.length}</p>
                        <p><strong>Passed Rules:</strong> ${data.passedRules}</p>
                        <p><strong>Scan Time:</strong> ${data.scanTime}ms</p>
                        <p><strong>Infrastructure:</strong> ${data.infrastructure}</p>
                        <p><strong>Scanner:</strong> ${data.scannerType}</p>
                        <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                        
                        <div class="success-badge">
                            <strong>🎯 CONFIRMED: Real Google Cloud Puppeteer + axe-core scanning completed successfully!</strong>
                        </div>
                        
                        ${data.violations.length > 0 ? `
                            <h3>Accessibility Violations:</h3>
                            ${data.violations.map(v => `
                                <div class="violation-item">
                                    <strong>${v.impact.toUpperCase()} Impact:</strong> ${v.description}
                                    <br><small>Affected elements: ${v.nodes}</small>
                                </div>
                            `).join('')}
                        ` : '<div class="success-badge"><h3>🎉 No accessibility violations found!</h3></div>'}
                    `;
                } else {
                    resultsContent.innerHTML = `
                        <div style="color: #dc3545; text-align: center;">
                            <h3>❌ Scan Failed</h3>
                            <p>${result.error}</p>
                            <p>Please try again or contact support if the issue persists.</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultsContent.innerHTML = `
                    <div style="color: #dc3545; text-align: center;">
                        <h3>❌ Network Error</h3>
                        <p>${error.message}</p>
                        <p>Please check your connection and try again.</p>
                    </div>
                `;
            } finally {
                scanBtn.disabled = false;
                scanBtn.textContent = '🚀 Start Google Cloud Scan';
            }
        }
        
        // Allow Enter key to trigger scan
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                startScan();
            }
        });
    </script>
</body>
</html>
`;

// Routes
app.get('/', (req, res) => {
    res.send(DASHBOARD_HTML);
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'SentryPrime Enterprise Scanner',
        version: '1.0.0',
        infrastructure: 'Google Cloud Run',
        timestamp: new Date().toISOString(),
        scanner: 'REAL_PUPPETEER_AXECORE'
    });
});

app.post('/api/scan', async (req, res) => {
    const startTime = Date.now();
    let browser = null;
    
    try {
        const { url } = req.body;
        
        if (!url) {
            return res.status(400).json({
                success: false,
                error: 'URL is required'
            });
        }
        
        let targetUrl = url;
        if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
            targetUrl = 'https://' + targetUrl;
        }
        
        console.log(`Starting accessibility scan for: ${targetUrl}`);
        
        // Launch Puppeteer with Google Cloud Run optimized settings
        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection'
            ],
            timeout: 10000
        });
        
        const page = await browser.newPage();
        
        // Set viewport and user agent
        await page.setViewport({
            width: 1280,
            height: 720
        });
        
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 SentryPrime/1.0');
        
        // Navigate to the page
        console.log(`Navigating to: ${targetUrl}`);
        await page.goto(targetUrl, {
            waitUntil: 'networkidle2',
            timeout: 30000
        });
        
        // Wait for page to be fully loaded
        await page.waitForTimeout(2000);
        
        // Inject axe-core from bundled source
        await page.evaluate(axeCoreSource);
        
        // Run axe-core accessibility analysis
        console.log('Running axe-core accessibility analysis...');
        const axeResults = await page.evaluate(async () => {
            return new Promise((resolve, reject) => {
                axe.run({
                    tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
                    resultTypes: ['violations', 'passes']
                }, (err, results) => {
                    if (err) reject(err);
                    else resolve(results);
                });
            });
        });
        
        const scanTime = Date.now() - startTime;
        
        // Process results
        const violations = axeResults.violations.map(violation => ({
            id: violation.id,
            impact: violation.impact || 'unknown',
            description: violation.description,
            help: violation.help,
            nodes: violation.nodes.length
        }));
        
        const totalRules = violations.length + axeResults.passes.length;
        const score = totalRules > 0 ? Math.round((axeResults.passes.length / totalRules) * 100) : 100;
        
        const wcagLevel = violations.some(v => v.impact === 'critical') ? 'A' :
                         violations.some(v => v.impact === 'serious') ? 'AA' : 'AAA';
        
        const scanResults = {
            success: true,
            url: targetUrl,
            score: score,
            wcagLevel: wcagLevel,
            scanTime: scanTime,
            violations: violations,
            passedRules: axeResults.passes.length,
            timestamp: new Date().toISOString(),
            infrastructure: 'Google Cloud Run',
            scannerType: 'REAL_PUPPETEER_AXECORE',
            engine: 'Puppeteer + axe-core 4.10.3'
        };
        
        console.log(`Scan completed: ${violations.length} violations found in ${scanTime}ms`);
        
        res.json({
            success: true,
            data: scanResults
        });
        
    } catch (error) {
        console.error('Scan error:', error);
        
        const scanTime = Date.now() - startTime;
        
        res.status(500).json({
            success: false,
            error: error.message,
            scanTime: scanTime,
            infrastructure: 'Google Cloud Run'
        });
        
    } finally {
        if (browser) {
            try {
                await browser.close();
            } catch (e) {
                console.error('Error closing browser:', e);
            }
        }
    }
});

// Error handling
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        infrastructure: 'Google Cloud Run'
    });
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 SentryPrime Enterprise Scanner running on port ${PORT}`);
    console.log(`📊 Infrastructure: Google Cloud Run`);
    console.log(`🔍 Scanner: Real Puppeteer + axe-core`);
    console.log(`⚡ Status: Ready for enterprise accessibility scanning`);
});
