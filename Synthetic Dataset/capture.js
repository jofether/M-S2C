const { chromium } = require('playwright');
const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');

const execPromise = util.promisify(exec);
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const PORT = 5173;
const URL = `http://localhost:${PORT}`;

// ============================================================================
// DIRECTORY SETUP FOR ML DATASET
// ============================================================================
const ROOT_DIR = __dirname;
const IMAGES_DIR = path.join(ROOT_DIR, 'images');
const OUTPUT_JSON_PATH = path.join(ROOT_DIR, 'github_finetune.json');

// Ensure centralized images folder exists
if (!fs.existsSync(IMAGES_DIR)) {
    fs.mkdirSync(IMAGES_DIR, { recursive: true });
}

// Global Array to hold the final Triplet Dataset
const masterDataset = [];

const getDirectories = source => fs.readdirSync(source)
    .map(name => path.join(source, name))
    .filter(dir => {
        try {
            return fs.lstatSync(dir).isDirectory() && 
                   !path.basename(dir).startsWith('.') && 
                   path.basename(dir) !== 'node_modules' &&
                   path.basename(dir) !== 'images'; // Ignore our new images folder
        } catch (e) { return false; }
    });

const repositories = getDirectories(__dirname);

// ============================================================================
// SERVER MANAGEMENT
// ============================================================================

async function killPort() {
    if (process.platform === 'win32') {
        try {
            await execPromise(`taskkill /F /IM node.exe /FI "MEMUSAGE>10000" 2>nul || exit 0`);
        } catch (e) {}
        try {
            await execPromise(`powershell -Command "Get-NetTCPConnection -LocalPort ${PORT} -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"`);
        } catch (e) {}
    }
}

async function deleteViteCache(repoPath) {
    const viteCachePath = path.join(repoPath, 'node_modules', '.vite');
    try {
        if (fs.existsSync(viteCachePath)) {
            fs.rmSync(viteCachePath, { recursive: true, force: true });
        }
    } catch (e) {
        console.warn(`      ⚠️ Failed to delete .vite cache: ${e.message}`);
    }
}

async function runViteServer(repoPath) {
    await killPort();
    const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
    const server = spawn(npmCmd, ['run', 'dev'], { cwd: repoPath, shell: true });
    
    for (let i = 0; i < 30; i++) {
        try {
            const res = await fetch(URL);
            if (res.ok) return server;
        } catch (e) {}
        await delay(1000);
    }
    throw new Error("Vite server timeout");
}

// ============================================================================
// PHASE 1: BASE SNIPE (Static Elements)
// ============================================================================

async function phaseOneBaseSnipe(page, repoName, bugs, actionBugIds) {
    console.log(`      📍 Phase 1: Base Snipe (Static Elements)`);
    let capturedCount = 0;
    
    for (const bug of bugs) {
        let bugId = bug.bug_id || (bug.comment && bug.comment.match(/Bug #(\d+)/)?.[1]);
        if (!bugId) continue;
        
        // Skip bugs that require actions
        if (actionBugIds.has(bugId)) continue;
        
        try {
            if (!bug.css_selector) {
                console.warn(`        ⚠️ Bug #${bugId}: missing css_selector`);
                continue;
            }
            
            const element = page.locator(bug.css_selector).first();
            await element.waitFor({ state: 'attached', timeout: 5000 });
            
            // Generate Centralized File Path
            const imageName = `${repoName}_bug-${bugId}.png`;
            const pngPath = path.join(IMAGES_DIR, imageName);
            
            // ----------------------------------------------------------------
            // THE SILVER BULLET + FALLBACK FIX
            // ----------------------------------------------------------------
            try {
                // Try to snipe the specific element (5s timeout)
                await element.screenshot({ path: pngPath, padding: 15, timeout: 5000 });
            } catch (imgErr) {
                console.warn(`        ⚠️ Bug #${bugId}: Element 0x0 or invisible. Saving full-page fallback instead.`);
                // Fallback: If the element disappeared, take a picture of the whole page so the model sees the empty space
                await page.screenshot({ path: pngPath, fullPage: true, timeout: 5000 });
            }
            
            // Compile into Master ML Dataset
            masterDataset.push({
                image_path: `./images/${imageName}`,
                report_text: bug.report_text,
                pos_code: bug.pos_code,
                neg_code: bug.neg_code,
                file_modified: bug.file_modified
            });
            
            console.log(`        ✓ Bug #${bugId} mapped to Master JSON`);
            capturedCount++;
        } catch (e) {
            console.warn(`        ⚠️ Bug #${bugId}: ${e.message}`);
        }
    }
    return capturedCount;
}

// ============================================================================
// PHASE 2: ACTION SNIPE (Dynamic Elements)
// ============================================================================

async function phaseTwoActionSnipe(page, repoName, bugs, actionsData) {
    console.log(`      📍 Phase 2: Action Snipe (Dynamic Elements)`);
    
    if (!actionsData || !actionsData.actions || !Array.isArray(actionsData.actions)) {
        return 0;
    }
    
    const bugMap = {};
    for (const bug of bugs) {
        let bugId = bug.bug_id || (bug.comment && bug.comment.match(/Bug #(\d+)/)?.[1]);
        if (bugId) bugMap[bugId] = bug;
    }
    
    let actionCount = 0;
    
    for (const action of actionsData.actions) {
        try {
            console.log(`        ⧉ ${action.name}`);
            await page.goto(URL, { waitUntil: 'load', timeout: 60000 });
            await delay(500);
            
            const bugMatch = action.name.match(/bug-(\d+)/);
            if (!bugMatch) continue;
            
            const bugId = bugMatch[1];
            const bug = bugMap[bugId];
            if (!bug || !bug.css_selector) continue;
            
            // Execute Interactions (Janitor or Clicks)
            if (action.action_type === 'remove') {
                const targets = Array.isArray(action.selector) ? action.selector : [action.selector];
                for (const selector of targets) {
                    await page.evaluate((s) => {
                        document.querySelectorAll(s).forEach(el => el.remove());
                    }, selector);
                }
            } else {
                const steps = Array.isArray(action.selector) ? action.selector : [action.selector];
                for (const selector of steps) {
                    await page.waitForSelector(selector, { timeout: 5000 });
                    await page.click(selector, { timeout: 5000, force: true });
                    await delay(500);
                }
            }
            
            await delay(500);
            
            // Targeted Bug Capture
            const element = page.locator(bug.css_selector).first();
            await element.waitFor({ state: 'attached', timeout: 3000 });
            
            const imageName = `${repoName}_bug-${bugId}_${action.name}.png`;
            const pngPath = path.join(IMAGES_DIR, imageName);
            
            // ----------------------------------------------------------------
            // THE SILVER BULLET + FALLBACK FIX
            // ----------------------------------------------------------------
            try {
                await element.screenshot({ path: pngPath, padding: 15, timeout: 5000 });
            } catch (imgErr) {
                console.warn(`          ⚠️ Bug #${bugId}: Element 0x0 or invisible. Saving full-page fallback instead.`);
                await page.screenshot({ path: pngPath, fullPage: true, timeout: 5000 });
            }
            
            // Compile into Master ML Dataset
            masterDataset.push({
                image_path: `./images/${imageName}`,
                report_text: bug.report_text,
                pos_code: bug.pos_code,
                neg_code: bug.neg_code,
                file_modified: bug.file_modified
            });
            
            console.log(`          ✓ Captured Bug #${bugId} mapped to Master JSON`);
            actionCount++;
        } catch (e) {
            console.warn(`        ⚠️ Action "${action.name}" failed: ${e.message}`);
        }
    }
    return actionCount;
}

// ============================================================================
// MAIN PROCESSING
// ============================================================================

async function processRepository(repoPath) {
    const repoName = path.basename(repoPath);
    const gtFilePath = path.join(repoPath, 'ground_truth.json');
    
    let gtData;
    try {
        // We only care about the buggy branch ground_truth data now
        const gtFromBuggy = require('child_process').execSync(`git show buggy:ground_truth.json`, { cwd: repoPath, encoding: 'utf8' });
        console.log(`\n🚀 STARTING: ${repoName}`);
        gtData = JSON.parse(gtFromBuggy);
    } catch (e) {
        console.warn(`⚠️  SKIPPING: ${repoName} (No ground_truth.json on buggy branch)`);
        return;
    }
    
    if (!gtData.bugs || !Array.isArray(gtData.bugs)) return;

    const browser = await chromium.launch({ headless: true });

    try {
        // ML OPTIMIZATION: We ONLY process the buggy branch. 
        // The clean code is already stored as `neg_code` in the JSON.
        console.log(`\n  📌 Branch: buggy (Stage-2 ML Anchor Generation)`);
        
        try {
            await execPromise(`git checkout -f buggy`, { cwd: repoPath });
            await execPromise(`git reset --hard && git clean -fd`, { cwd: repoPath });
        } catch (err) {
            console.warn(`    ⚠️ Git checkout failed: ${err.message}`);
            return;
        }
        
        await deleteViteCache(repoPath);
        await delay(2000);
        
        let server;
        try {
            server = await runViteServer(repoPath);
        } catch (err) {
            console.error(`    ❌ Vite server failed: ${err.message}`);
            return;
        }
        
        const context = await browser.newContext({
            viewport: {
                width: 1280,
                height: gtData.playwright_config?.viewport_height || 800
            }
        });
        const page = await context.newPage();
        
        try {
            await page.goto(URL, { waitUntil: 'load', timeout: 60000 });
            await delay(500);
            
            let actionsData = null;
            const actionBugIds = new Set();
            const actionPath = path.join(repoPath, 'playwright_actions.json');
            
            if (fs.existsSync(actionPath)) {
                try {
                    actionsData = JSON.parse(fs.readFileSync(actionPath, 'utf8'));
                    if (actionsData.actions && Array.isArray(actionsData.actions)) {
                        for (const action of actionsData.actions) {
                            const match = action.name.match(/bug-(\d+)/);
                            if (match) actionBugIds.add(match[1]);
                        }
                    }
                } catch (e) {}
            }
            
            const baseCount = await phaseOneBaseSnipe(page, repoName, gtData.bugs, actionBugIds);
            const actionCount = await phaseTwoActionSnipe(page, repoName, gtData.bugs, actionsData);
            
            console.log(`    📊 Captured: ${baseCount} base + ${actionCount} actions = ${baseCount + actionCount} bugs`);
            
        } finally {
            await context.close();
        }
        
        if (process.platform === 'win32') {
            spawn("taskkill", ["/pid", server.pid, '/f', '/t']);
        } else {
            server.kill();
        }
        await delay(2000);
        
    } catch (err) {
        console.error(`❌ Failed: ${repoName} -> ${err.message}`);
    } finally {
        await browser.close();
    }
}

async function main() {
    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║      M-S2C Stage-2: Dataloader Capture System          ║');
    console.log('╚════════════════════════════════════════════════════════╝');
    console.log(`Processing ${repositories.length} repositories...\n`);
    
    for (const repo of repositories) {
        await processRepository(repo);
    }
    
    // SAVE THE FINAL MASTER JSON
    fs.writeFileSync(OUTPUT_JSON_PATH, JSON.stringify(masterDataset, null, 2), 'utf8');
    
    console.log("\n╔════════════════════════════════════════════════════════╗");
    console.log("║      🎉 DATASET GENERATION COMPLETE!                   ║");
    console.log(`║      Saved ${masterDataset.length} Triplet Samples to github_finetune.json   ║`);
    console.log("╚════════════════════════════════════════════════════════╝");
}

main();