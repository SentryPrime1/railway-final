#!/usr/bin/env node
/**
 * SentryPrime Accessibility Scanner
 * Production-ready Puppeteer + axe-core scanning engine
 */

const puppeteer = require('puppeteer');
const axeCore = require('axe-core');
const fs = require('fs');

// Configuration
const SCAN_TIMEOUT = 30000; // 30 seconds
const VIEWPORT_WIDTH = 1280;
const VIEWPORT_HEIGHT = 720;

/**
 * Main scanning function
 */
async function scanWebsite(url) {
    let browser = null;
    const startTime = Date.now();
    
    try {
        // Launch browser with production settings
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
                '--disable-gpu'
            ],
            timeout: 10000
        });
        
        const page = await browser.newPage();
        
        // Set viewport and user agent
        await page.setViewport({
            width: VIEWPORT_WIDTH,
            height: VIEWPORT_HEIGHT
        });
        
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SentryPrime/1.0'
        );
        
        // Navigate to the page
        await page.goto(url, {
            waitUntil: 'networkidle0',
            timeout: SCAN_TIMEOUT
        });
        
        // Wait for page to be fully loaded
        await page.waitForTimeout(2000);
        
        // Inject axe-core
        await page.addScriptTag({
            content: axeCore.source
        });
        
        // Run accessibility scan
        const results = await page.evaluate(async () => {
            return await axe.run({
                rules: {
                    // Enable all rules for comprehensive scanning
                    'color-contrast': { enabled: true },
                    'focus-order-semantics': { enabled: true },
                    'hidden-content': { enabled: true },
                    'label-content-name-mismatch': { enabled: true },
                    'link-in-text-block': { enabled: true },
                    'nested-interactive': { enabled: true },
                    'no-autoplay-audio': { enabled: true },
                    'role-img-alt': { enabled: true },
                    'scrollable-region-focusable': { enabled: true },
                    'select-name': { enabled: true },
                    'server-side-image-map': { enabled: true },
                    'svg-img-alt': { enabled: true },
                    'td-has-header': { enabled: true },
                    'td-headers-attr': { enabled: true },
                    'th-has-data-cells': { enabled: true },
                    'valid-lang': { enabled: true },
                    'video-caption': { enabled: true }
                },
                tags: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice']
            });
        });
        
        // Get page metadata
        const pageInfo = await page.evaluate(() => {
            return {
                title: document.title,
                url: window.location.href,
                lang: document.documentElement.lang || 'en',
                charset: document.characterSet,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            };
        });
        
        // Process and enhance results
        const processedResults = {
            url: pageInfo.url,
            title: pageInfo.title,
            lang: pageInfo.lang,
            charset: pageInfo.charset,
            viewport: pageInfo.viewport,
            violations: results.violations.map(violation => ({
                id: violation.id,
                impact: violation.impact,
                description: violation.description,
                help: violation.help,
                helpUrl: violation.helpUrl,
                tags: violation.tags,
                nodes: violation.nodes.map(node => ({
                    target: node.target,
                    html: node.html.substring(0, 200) + (node.html.length > 200 ? '...' : ''),
                    impact: node.impact,
                    failureSummary: node.failureSummary
                }))
            })),
            passes: results.passes.map(pass => ({
                id: pass.id,
                description: pass.description,
                tags: pass.tags,
                nodes: pass.nodes.length
            })),
            incomplete: results.incomplete.map(incomplete => ({
                id: incomplete.id,
                impact: incomplete.impact,
                description: incomplete.description,
                help: incomplete.help,
                helpUrl: incomplete.helpUrl,
                tags: incomplete.tags,
                nodes: incomplete.nodes.length
            })),
            inapplicable: results.inapplicable.length,
            testEngine: {
                name: results.testEngine.name,
                version: results.testEngine.version
            },
            testRunner: {
                name: results.testRunner.name
            },
            testEnvironment: {
                userAgent: results.testEnvironment.userAgent,
                windowWidth: results.testEnvironment.windowWidth,
                windowHeight: results.testEnvironment.windowHeight,
                orientationAngle: results.testEnvironment.orientationAngle,
                orientationType: results.testEnvironment.orientationType
            },
            timestamp: new Date().toISOString(),
            scanDuration: Date.now() - startTime
        };
        
        return processedResults;
        
    } catch (error) {
        throw new Error(`Scan failed: ${error.message}`);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

/**
 * Main execution
 */
async function main() {
    const startTime = Date.now();
    
    try {
        // Get URL from command line arguments
        const url = process.argv[2];
        
        if (!url) {
            console.error(JSON.stringify({
                success: false,
                error: 'URL parameter is required'
            }));
            process.exit(1);
        }
        
        // Validate URL format
        let targetUrl;
        try {
            targetUrl = new URL(url.startsWith('http' ) ? url : `https://${url}` );
        } catch (e) {
            console.error(JSON.stringify({
                success: false,
                error: 'Invalid URL format'
            }));
            process.exit(1);
        }
        
        // Run the scan
        const results = await scanWebsite(targetUrl.href);
        
        // Output results as JSON
        console.log(JSON.stringify(results, null, 0));
        
    } catch (error) {
        console.error(JSON.stringify({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        }));
        process.exit(1);
    }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error(JSON.stringify({
        success: false,
        error: `Uncaught exception: ${error.message}`,
        timestamp: new Date().toISOString()
    }));
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error(JSON.stringify({
        success: false,
        error: `Unhandled rejection: ${reason}`,
        timestamp: new Date().toISOString()
    }));
    process.exit(1);
});

// Run the scanner
if (require.main === module) {
    main();
}
