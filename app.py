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

# Configuration
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
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .scanner-card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .input-group {
            margin-bottom: 2rem;
        }
        
        .input-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #555;
        }
        
        .input-group input {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .input-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .scan-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
            width: 100%;
        }
        
        .scan-button:hover {
            transform: translateY(-2px);
        }
        
        .scan-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .results {
            margin-top: 2rem;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #667eea;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .violation {
            background: white;
            border-left: 4px solid #e74c3c;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 5px;
        }
        
        .violation h4 {
            color: #e74c3c;
            margin-bottom: 0.5rem;
        }
        
        .violation-meta {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.5rem;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        
        .feature {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        .feature h3 {
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
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
            <h2 style="margin-bottom: 2rem; color: #333;">Website Accessibility Scanner</h2>
            
            <div class="input-group">
                <label for="url">Website URL</label>
                <input type="url" id="url" placeholder="https://example.com" value="https://example.com">
            </div>
            
            <button class="scan-button" onclick="scanWebsite( )">
                <span id="button-text">Scan Website</span>
            </button>
            
            <div id="results" class="results">
                <!-- Results will be populated here -->
            </div>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>🔍 Real Browser Scanning</h3>
                <p>Uses genuine Puppeteer automation with Chrome browser for authentic accessibility testing</p>
            </div>
            
            <div class="feature">
                <h3>⚡ axe-core Engine</h3>
                <p>Powered by the industry-standard axe-core library used by Microsoft, Google, and major enterprises</p>
            </div>
            
            <div class="feature">
                <h3>📊 WCAG Compliance</h3>
                <p>Complete coverage of WCAG 2.1 guidelines with detailed violation reporting and remediation guidance</p>
            </div>
            
            <div class="feature">
                <h3>🚀 Enterprise Ready</h3>
                <p>Production-grade infrastructure with API access, continuous monitoring, and scalable architecture</p>
            </div>
        </div>
    </div>

    <script>
        async function scanWebsite() {
            const url = document.getElementById('url').value;
            const button = document.querySelector('.scan-button');
            const buttonText = document.getElementById('button-text');
            const results = document.getElementById('results');
            
            if (!url) {
                alert('Please enter a valid URL');
                return;
            }
            
            // Show loading state
            button.disabled = true;
            buttonText.textContent = 'Scanning...';
            results.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Scanning ${url} for accessibility issues...</p>
                    <p style="font-size: 0.9rem; margin-top: 1rem;">This may take 10-30 seconds</p>
                </div>
            `;
            results.classList.add('show');
            
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
                    displayResults(data.data);
                } else {
                    displayError(data.error || 'Scan failed');
                }
            } catch (error) {
                displayError('Network error: ' + error.message);
            } finally {
                button.disabled = false;
                buttonText.textContent = 'Scan Website';
            }
        }
        
        function displayResults(data) {
            const results = document.getElementById('results');
            const violations = data.violations || [];
            
            let html = `
                <h3 style="margin-bottom: 1rem; color: #333;">Scan Results</h3>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">${violations.length}</div>
                        <div class="stat-label">Violations Found</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">${data.passes?.length || 0}</div>
                        <div class="stat-label">Tests Passed</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">${data.incomplete?.length || 0}</div>
                        <div class="stat-label">Manual Review</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">${data.scanTime || 'N/A'}</div>
                        <div class="stat-label">Scan Time</div>
                    </div>
                </div>
            `;
            
            if (violations.length > 0) {
                html += '<h4 style="margin: 2rem 0 1rem; color: #e74c3c;">Accessibility Violations</h4>';
                violations.forEach(violation => {
                    html += `
                        <div class="violation">
                            <h4>${violation.id}</h4>
                            <div class="violation-meta">
                                Impact: ${violation.impact} | 
                                Elements: ${violation.nodes?.length || 0} | 
                                Tags: ${violation.tags?.join(', ') || 'N/A'}
                            </div>
                            <p>${violation.description}</p>
                            ${violation.helpUrl ? `<p><a href="${violation.helpUrl}" target="_blank">Learn more →</a></p>` : ''}
                        </div>
                    `;
                });
            } else {
                html += '<div style="text-align: center; padding: 2rem; color: #27ae60;"><h3>🎉 No accessibility violations found!</h3><p>This website appears to be well-optimized for accessibility.</p></div>';
            }
            
            html += `
                <div style="margin-top: 2rem; padding: 1rem; background: #e8f4fd; border-radius: 5px; font-size: 0.9rem;">
                    <strong>Scan Details:</strong>  

                    URL: ${data.url}  

                    Timestamp: ${data.timestamp}  

                    Engine: ${data.engine}  

                    Infrastructure: ${data.infrastructure}
                </div>
            `;
            
            results.innerHTML = html;
        }
        
        function displayError(error) {
            const results = document.getElementById('results');
            results.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: #e74c3c;">
                    <h3>❌ Scan Failed</h3>
                    <p>${error}</p>
                    <p style="font-size: 0.9rem; margin-top: 1rem;">Please try again or contact support if the issue persists.</p>
                </div>
            `;
        }
        
        // Allow Enter key to trigger scan
        document.getElementById('url').addEventListener('keypress', function(e) {
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
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'SentryPrime Accessibility Scanner',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': NODE_ENV
    })

@app.route('/api/scan', methods=['POST'])
def scan_website():
    """Scan a website for accessibility issues"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data['url'].strip()
        if not url.startswith(('http://', 'https://' )):
            url = 'https://' + url
        
        logger.info(f"Starting accessibility scan for: {url}" )
        
        # Run the Node.js scanner
        start_time = datetime.utcnow()
        result = subprocess.run([
            'node', 'scanner.js', url
        ], capture_output=True, text=True, timeout=60)
        
        end_time = datetime.utcnow()
        scan_duration = (end_time - start_time).total_seconds()
        
        if result.returncode != 0:
            logger.error(f"Scanner failed: {result.stderr}")
            return jsonify({
                'success': False,
                'error': f'Scanner error: {result.stderr}'
            }), 500
        
        # Parse the scanner output
        try:
            scan_results = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse scanner output: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to parse scan results'
            }), 500
        
        # Enhance results with metadata
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
    app.run(host='0.0.0.0', port=PORT, debug=(NODE_ENV == 'development'))
