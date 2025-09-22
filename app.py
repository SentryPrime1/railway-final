#!/usr/bin/env python3
"""
SentryPrime - Enterprise Accessibility Scanning SaaS
Production-ready Flask application with real Puppeteer + axe-core scanning
"""

import os
import json
import subprocess
import tempfile
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO )
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration - Railway uses PORT environment variable
PORT = int(os.environ.get('PORT', 3000))
NODE_ENV = os.environ.get('NODE_ENV', 'production')

# HTML Template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SentryPrime - Enterprise Accessibility Scanner</title>
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
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .scanner-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .scanner-form {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .url-input {
            flex: 1;
            padding: 1rem;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
        }
        
        .scan-button {
            padding: 1rem 2rem;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .scan-button:hover {
            transform: translateY(-2px);
        }
        
        .scan-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .results {
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            display: none;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .feature-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .feature-description {
            opacity: 0.8;
            line-height: 1.5;
        }
        
        .error {
            color: #ff6b6b;
            background: rgba(255, 107, 107, 0.1);
            padding: 1rem;
            border-radius: 10px;
            margin-top: 1rem;
        }
        
        .success {
            color: #51cf66;
            background: rgba(81, 207, 102, 0.1);
            padding: 1rem;
            border-radius: 10px;
            margin-top: 1rem;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
        }
        
        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 3px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .violation-item {
            background: rgba(255, 255, 255, 0.1);
            margin: 0.5rem 0;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #ff6b6b;
        }
        
        .violation-impact {
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }
        
        .violation-description {
            margin-bottom: 0.5rem;
        }
        
        .violation-help {
            font-size: 0.9rem;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SentryPrime</h1>
            <p>Enterprise-grade accessibility scanning with real Puppeteer + axe-core technology</p>
        </div>
        
        <div class="scanner-card">
            <h2>Website Accessibility Scanner</h2>
            <div class="scanner-form">
                <input type="url" id="urlInput" class="url-input" placeholder="https://example.com" value="https://essolar.com/">
                <button id="scanButton" class="scan-button" onclick="scanWebsite( )">Scan Website</button>
            </div>
            <div id="results" class="results"></div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Real Browser Scanning</div>
                <div class="feature-description">Uses genuine Puppeteer automation with Chrome browser for authentic accessibility testing</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">axe-core Engine</div>
                <div class="feature-description">Powered by the industry-standard axe-core library used by Microsoft, Google, and major enterprises</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">WCAG Compliance</div>
                <div class="feature-description">Complete coverage of WCAG 2.1 guidelines with detailed violation reporting and remediation guidance</div>
            </div>
        </div>
    </div>

    <script>
        async function scanWebsite() {
            const urlInput = document.getElementById('urlInput');
            const scanButton = document.getElementById('scanButton');
            const results = document.getElementById('results');
            
            const url = urlInput.value.trim();
            if (!url) {
                showError('Please enter a valid URL');
                return;
            }
            
            // Show loading state
            scanButton.disabled = true;
            scanButton.textContent = 'Scanning...';
            results.style.display = 'block';
            results.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Scanning ${url} for accessibility issues...</p>
                    <p><small>This may take 5-15 seconds</small></p>
                </div>
            `;
            
            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showResults(data.data);
                } else {
                    showError(data.error || 'Scan failed');
                }
            } catch (error) {
                showError('Failed to parse scan results');
                console.error('Scan error:', error);
            } finally {
                scanButton.disabled = false;
                scanButton.textContent = 'Scan Website';
            }
        }
        
        function showResults(data) {
            const results = document.getElementById('results');
            const violations = data.violations || [];
            
            let html = `
                <div class="success">
                    <h3>✅ Scan Complete</h3>
                    <p><strong>URL:</strong> ${data.url}</p>
                    <p><strong>Violations Found:</strong> ${violations.length}</p>
                    <p><strong>Scan Time:</strong> ${data.scanTime}</p>
                    <p><strong>Engine:</strong> ${data.engine}</p>
                    <p><strong>Infrastructure:</strong> ${data.infrastructure}</p>
                </div>
            `;
            
            if (violations.length > 0) {
                html += '<h4>Accessibility Violations:</h4>';
                violations.forEach(violation => {
                    html += `
                        <div class="violation-item">
                            <div class="violation-impact">${violation.impact || 'unknown'} impact</div>
                            <div class="violation-description"><strong>${violation.description}</strong></div>
                            <div class="violation-help">${violation.help}</div>
                            <div><small>Affected elements: ${violation.nodes ? violation.nodes.length : 0}</small></div>
                        </div>
                    `;
                });
            } else {
                html += '<div class="success"><h4>🎉 No accessibility violations found!</h4></div>';
            }
            
            results.innerHTML = html;
        }
        
        function showError(message) {
            const results = document.getElementById('results');
            results.style.display = 'block';
            results.innerHTML = `
                <div class="error">
                    <h3>❌ Scan Failed</h3>
                    <p>${message}</p>
                    <p>Please try again or contact support if the issue persists.</p>
                </div>
            `;
        }
        
        // Allow Enter key to trigger scan
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                scanWebsite();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/health')
def health_check():
    """Health check endpoint for Railway"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'SentryPrime Accessibility Scanner',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': NODE_ENV,
            'port': PORT
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/scan', methods=['POST'])
def scan_website():
    """Scan a website for accessibility issues"""
    try:
        # Get URL from request
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL cannot be empty'
            }), 400
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://' )):
            url = 'https://' + url
        
        logger.info(f"Starting accessibility scan for: {url}" )
        start_time = datetime.utcnow()
        
        # Run the scanner
        result = subprocess.run(
            ['node', 'scanner.js', url],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        end_time = datetime.utcnow()
        scan_duration = (end_time - start_time).total_seconds()
        
        if result.returncode != 0:
            logger.error(f"Scanner failed with return code {result.returncode}")
            logger.error(f"Scanner stderr: {result.stderr}")
            return jsonify({
                'success': False,
                'error': 'Scanner execution failed'
            }), 500
        
        # Parse scanner output
        try:
            scan_results = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse scanner output: {str(e)}")
            logger.error(f"Scanner stdout: {result.stdout}")
            return jsonify({
                'success': False,
                'error': 'Failed to parse scan results'
            }), 500
        
        # Add metadata
        scan_results.update({
            'scanTime': f"{scan_duration:.2f}s",
            'timestamp': end_time.isoformat(),
            'engine': 'Puppeteer + axe-core 4.10.3',
            'infrastructure': 'Railway.app Production'
        })
        
        logger.info(f"Scan completed for {url}: {len(scan_results.get('violations', []))} violations found")
        
        return jsonify({
            'success': True,
            'data': scan_results
        })
        
    except subprocess.TimeoutExpired:
        logger.error(f"Scan timeout for URL: {url}")
        return jsonify({
            'success': False,
            'error': 'Scan timeout - please try again'
        }), 408
        
    except Exception as e:
        logger.error(f"Unexpected error during scan: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

if __name__ == '__main__':
    print(f"Starting SentryPrime Enterprise Scanner on port {PORT}")
    print(f"Environment: {NODE_ENV}")
    print(f"Health check endpoint: /api/health")
    app.run(host='0.0.0.0', port=PORT, debug=(NODE_ENV == 'development'))
