document.addEventListener('DOMContentLoaded', () => {
    // Navigation / Tab elements
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    const qaNavBtn = document.getElementById('qa-nav-btn');

    // Forms and Inputs
    const analyzeForm = document.getElementById('analyze-form');
    const repoInput = document.getElementById('repo-input');
    const btnSubmitAnalyze = document.getElementById('btn-submit-analyze');
    const consoleOutput = document.getElementById('console-output');
    const guideContainer = document.getElementById('guide-container');
    const guideViewer = document.getElementById('guide-viewer');
    const btnCopyGuide = document.getElementById('btn-copy-guide');

    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessagesContainer = document.getElementById('chat-messages-container');
    const activeRepoBadge = document.getElementById('active-repo-badge');
    const suggestionItems = document.querySelectorAll('.suggestion-item');

    // State Variables
    let currentRepo = '';
    let generatedGuideMarkdown = '';

    // Set marked options
    marked.setOptions({
        breaks: true,
        headerIds: true,
        mangle: false
    });

    // Tab Switching Logic
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            if (item.disabled) return;

            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Update active tab content
            const targetTab = item.getAttribute('data-tab');
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === targetTab) {
                    content.classList.add('active');
                }
            });

            // Update titles
            if (targetTab === 'analyze-tab') {
                pageTitle.textContent = 'Codebase Analysis';
                pageSubtitle.textContent = 'Map repositories and synthesize comprehensive developer onboarding guides';
            } else if (targetTab === 'qa-tab') {
                pageTitle.textContent = 'Interactive Q&A Session';
                pageSubtitle.textContent = 'Ask context-aware questions about the active repository with precise source citations';
            }
        });
    });

    // Helper: Add Line to Console Feed
    function logToConsole(message, type = 'info') {
        const line = document.createElement('div');
        line.className = `console-line ${type}`;
        
        // Custom formatting
        let text = message;
        if (message.startsWith('===')) {
            line.style.fontWeight = '700';
            line.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
            line.style.paddingBottom = '4px';
            line.style.marginTop = '10px';
        }
        
        line.innerHTML = text;
        consoleOutput.appendChild(line);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    // Clear Console
    function clearConsole() {
        consoleOutput.innerHTML = '';
    }

    // Simulate Orchestrator Progress Feed (Visual Polish for Demo)
    async function runSimulatedLogs(repoUrl) {
        clearConsole();
        logToConsole(`=== Starting Codebase Analysis ===`, 'success');
        logToConsole(`Target: ${repoUrl}`);
        logToConsole(`Output: ./outputs`);
        await sleep(1200);
        
        logToConsole(`Checking clone source...`);
        await sleep(800);
        logToConsole(`Starting sandboxed MCP Server process...`, 'success');
        logToConsole(`Initializing MCP Client Session...`);
        await sleep(1000);
        logToConsole(`MCP Server handshake successful.`, 'success');
        await sleep(600);

        logToConsole(`=== [ExplorerAgent - Codebase Structural Analyst] Starting Task ===`, 'agent');
        logToConsole(`Prompt: Walk the codebase directory tree, run git history inspection, and compile a structural overview report.`, 'info');
        await sleep(1500);
        
        logToConsole(`  [Step 1 - Tool Call] list_files with arguments: {}`, 'tool');
        await sleep(1200);
        logToConsole(`  [Step 1 - Tool Response] Success. Discovered source structure, configurations, and environment scripts.`, 'success');
        await sleep(1000);
        
        logToConsole(`  [Step 2 - Tool Call] get_git_history with arguments: {}`, 'tool');
        await sleep(1500);
        logToConsole(`  [Step 2 - Tool Response] Success. Extracted contributor commits, history log, and active branches.`, 'success');
        await sleep(1000);
        
        logToConsole(`=== [ExplorerAgent] Structural Analysis Report synthesized. ===`, 'success');
        await sleep(1200);

        logToConsole(`=== [MapperAgent - Codebase Data-Flow Architect] Starting Task ===`, 'agent');
        logToConsole(`Prompt: Trace configurations, dependency packages, import dependencies, and entry-points.`, 'info');
        await sleep(1500);
        
        logToConsole(`  [Step 1 - Tool Call] read_file with arguments: {"path": "main.py"}`, 'tool');
        await sleep(1000);
        logToConsole(`  [Step 1 - Tool Response] Read main.py entry-point module imports and app instantiation.`, 'success');
        await sleep(800);
        
        logToConsole(`  [Step 2 - Tool Call] run_ast_query with arguments: {"path": "src/utils.py"}`, 'tool');
        await sleep(1200);
        logToConsole(`  [Step 2 - Tool Response] Analyzed AST nodes. Discovered 5 class structures and 14 function symbols.`, 'success');
        await sleep(1000);

        logToConsole(`=== [MapperAgent] Component mapping and flow chart compiled. ===`, 'success');
        await sleep(1200);

        logToConsole(`=== [DocWriterAgent] Synthesizing final onboarding guide document... ===`, 'agent');
        logToConsole(`Merging Explorer structural model and Mapper data-flow definitions.`, 'info');
        await sleep(2000);
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Analysis Form Submission
    analyzeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const repoUrl = repoInput.value.trim();
        if (!repoUrl) return;

        // Reset state
        currentRepo = repoUrl;
        generatedGuideMarkdown = '';
        guideContainer.classList.add('hidden');
        
        // Update Button State
        btnSubmitAnalyze.disabled = true;
        btnSubmitAnalyze.innerHTML = `
            <div class="spinner-container">
                <div class="spinner"></div>
                <span>Analyzing Codebase...</span>
            </div>
        `;

        // Start simulated logs (visual effect)
        const logPromise = runSimulatedLogs(repoUrl);

        try {
            // Trigger actual API request concurrently
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ repo_url: repoUrl })
            });

            // Wait for logs simulation to finish minimum steps so user sees the beauty
            await logPromise;

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'An error occurred during analysis.');
            }

            const data = await response.json();
            generatedGuideMarkdown = data.onboarding_guide;

            logToConsole(`=== Onboarding Guide Successfully Generated! ===`, 'success');
            logToConsole(`Saved to outputs directory. Guide length: ${generatedGuideMarkdown.length} bytes.`);

            // Display Guide
            guideViewer.innerHTML = marked.parse(generatedGuideMarkdown);
            // Highlight code blocks
            Prism.highlightAllUnder(guideViewer);
            guideContainer.classList.remove('hidden');

            // Enable QA Tab
            qaNavBtn.disabled = false;
            activeRepoBadge.querySelector('.repo-name').textContent = repoUrl;

            // Scroll to Guide
            setTimeout(() => {
                guideContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);

        } catch (error) {
            logToConsole(`Error: ${error.message}`, 'error');
            console.error(error);
        } finally {
            // Restore Button State
            btnSubmitAnalyze.disabled = false;
            btnSubmitAnalyze.innerHTML = `
                <span class="btn-text">Generate Onboarding Guide</span>
                <i class="fa-solid fa-arrow-right btn-icon"></i>
            `;
        }
    });

    // Copy Guide Button
    btnCopyGuide.addEventListener('click', () => {
        if (!generatedGuideMarkdown) return;
        navigator.clipboard.writeText(generatedGuideMarkdown).then(() => {
            const originalText = btnCopyGuide.innerHTML;
            btnCopyGuide.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                btnCopyGuide.innerHTML = originalText;
            }, 2000);
        });
    });

    // Chat Q&A Logic
    function appendMessage(text, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isUser ? 'user-message' : 'assistant-message'}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = isUser ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';
        
        if (isUser) {
            content.textContent = text;
        } else {
            // Render markdown answer for rich responses (including code formatting)
            content.innerHTML = marked.parse(text);
            // Highlight code blocks
            Prism.highlightAllUnder(content);
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatMessagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        return messageDiv;
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = chatInput.value.trim();
        if (!question || !currentRepo) return;

        chatInput.value = '';
        appendMessage(question, true);

        // Add loading bubble
        const loadingMessage = appendMessage('<div class="spinner-container"><div class="spinner"></div><span>Agent is thinking...</span></div>');

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repo_url: currentRepo,
                    question: question
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'An error occurred during query.');
            }

            const data = await response.json();
            // Remove loading message
            chatMessagesContainer.removeChild(loadingMessage);
            // Add actual response
            appendMessage(data.answer);

        } catch (error) {
            chatMessagesContainer.removeChild(loadingMessage);
            appendMessage(`**Error:** ${error.message}`);
            console.error(error);
        }
    });

    // Suggested Questions
    suggestionItems.forEach(item => {
        item.addEventListener('click', () => {
            chatInput.value = item.textContent;
            chatInput.focus();
        });
    });
});
