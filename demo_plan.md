# Codebase Onboarding Concierge - Demo Walkthrough Plan

This guide outlines a structured, high-impact demonstration flow to showcase the capabilities of the **Codebase Onboarding Concierge**.

---

## 📋 Preparation & Setup

Ensure the virtual environment is active and all required dependencies are installed:
```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies (fastapi, uvicorn, and aiofiles are now integrated)
pip install -r requirements.txt

# Export your Gemini API key
$env:GEMINI_API_KEY="your_actual_gemini_api_key"
```

---

## 🌐 Demo Route 1: The Interactive Web UI (Recommended)

The Web UI provides a visually stunning, glassmorphic dark-themed cockpit ideal for live presentations. It showcases both the multi-agent reasoning steps and the synthesized output in a user-friendly way.

### Step 1: Start the Local Web Server
```powershell
python src/server.py
```
*   **What to highlight:** The server is running locally on [http://localhost:8080](http://localhost:8080) and can easily be deployed to container environments like Google Cloud Run.

### Step 2: Open the Web UI
Open your browser and navigate to `http://localhost:8080`.
*   **What to highlight:** The modern responsive design, dark-mode gradient ambient glows, and glassmorphic panels.

### Step 3: Trigger Codebase Analysis
Enter a repository source in the input box.
*   **Local Repository Option:** Use the absolute path to this onboarding agent project:
    `C:\Users\test.LAPTOP-GJAAATM6\Downloads\Antigravity\submission\codebase-onboarding-agent`
*   **GitHub Repository Option:** Use a lightweight public repo:
    `https://github.com/fastapi/fastapi` (cloned previously)

Click **"Generate Onboarding Guide"**.

### Step 4: Show the Multi-Agent Orchestrator Feed
*   Explain that the system runs a team of cooperative agents.
*   Direct attention to the **Multi-Agent Orchestrator Feed** console, showing the agents coordinating and using sandboxed tools (`list_files`, `get_git_history`, `read_file`, `run_ast_query`).
*   Point out that the Explorer Agent runs the file indexing and git contributor trace, the Mapper Agent handles AST parse, and the Doc-Writer synthesizes them.

### Step 5: Explore the Onboarding Guide
Once the analysis is complete, a beautiful Markdown document will render below the controls.
*   Highlight the **architecture overview** section and structural directory tree mapping.
*   Highlight the **packaging setup** and major dependencies section (parsed directly from files like `requirements.txt` or `package.json`).
*   Highlight the **top contributors** list extracted safely from the git history.

### Step 6: Interactive Q&A Session
Click the **"Interactive Q&A"** tab in the sidebar.
*   Ask a question like: *“What libraries does this app depend on and how does it parse command-line arguments?”*
*   Click one of the suggested questions.
*   **What to highlight:** The response is context-aware, formatting answers in Markdown with exact files, classes, or function citation blocks.

---

## 💻 Demo Route 2: The Command Line Interface (CLI)

For audiences who prefer terminal tools or developers building automation scripts, the CLI demo is highly compelling.

### Step 1: Generate an Onboarding Guide via CLI
Run the `analyze` command on the target repository:
```powershell
python onboard.py analyze https://github.com/fastapi/fastapi --output ./fastapi_outputs
```
*   **What to look for:** Observe the terminal logs indicating agent tool invocations (`list_files`, `get_git_history` with the newly fixed non-blocking stdin handling!).
*   **Output:** Open the newly created guide at `./fastapi_outputs/ONBOARDING_GUIDE.md` to show the final document.

### Step 2: Run a Codebase Q&A Query
Run a direct query from the CLI:
```powershell
python onboard.py ask https://github.com/fastapi/fastapi "How are routes defined in FastAPI?"
```
*   **What to look for:** Watch the agent query the codebase and return a complete explanation alongside code citations.

---

## 🔌 Demo Route 3: Editor Integration (Claude Desktop / Cursor)

Demonstrate how this tool can be exposed as a standalone standard MCP server to enhance AI tools like Claude Desktop or Cursor.

### Configuration Walkthrough
Show the JSON config snippet for Claude Desktop:
```json
{
  "mcpServers": {
    "codebase-onboarding-concierge": {
      "command": "python",
      "args": ["C:/Users/test.LAPTOP-GJAAATM6/Downloads/Antigravity/submission/codebase-onboarding-agent/src/mcp_server.py"],
      "env": {
        "ONBOARD_REPO_PATH": "C:/Users/test.LAPTOP-GJAAATM6/Downloads/Antigravity/submission/codebase-onboarding-agent"
      }
    }
  }
}
```
*   Explain that this connects our AST search, symbol inspection, and directory-safe tools directly to their editor, ensuring they have an onboarding assistant inside their IDE.
