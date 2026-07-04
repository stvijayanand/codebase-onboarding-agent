# Codebase Onboarding Concierge

An AI-powered multi-agent onboarding assistant. When pointed at any GitHub repository (or local folder), it runs a team of agents that inspect the codebase through a sandboxed Model Context Protocol (MCP) server to generate a premium developer onboarding guide and answer freeform questions with precise citations.

---

## Features

1. **Multi-Agent Crew**:
   - **Explorer Agent**: Maps files, directory trees, identifies packaging systems, and reviews Git commit logs to identify key contributors.
   - **Mapper Agent**: Traces code routing, entry points, AST definitions, database linkages, and data flow.
   - **Doc-Writer Agent**: Synthesizes analysis reports into a premium onboarding README with Mermaid diagrams, setup walkthroughs, and a ranked list of "Good First Issues."
   - **Q&A Agent**: Answers interactive queries about the repository citing exact files and line ranges.
2. **Model Context Protocol (MCP) Server**: 
   Exposes read-only inspection tools (`list_files`, `read_file`, `search_symbols`, `get_git_history`, `run_ast_query`) so agents can interact through standard, sandboxed protocol actions. Can also be exposed standalone for editors like Claude Desktop or Cursor.
3. **Double Interface**: Exposes operations both as a **Local CLI** and a **FastAPI Web Server** for container deployment.
4. **Sandboxed Security**: Read-only directory access with strict validation checks preventing directory traversal escapes.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone & Install Dependencies
```bash
# Clone the onboarding agent repository
cd codebase-onboarding-agent

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure API Key
Export your Gemini API Key:
```bash
# Windows Command Prompt:
set GEMINI_API_KEY=your_gemini_api_key

# Windows PowerShell:
$env:GEMINI_API_KEY="your_gemini_api_key"

# Linux/macOS:
export GEMINI_API_KEY="your_gemini_api_key"
```

---

## Command Line Interface (CLI)

Use `onboard.py` from the root directory:

### 1. Generate an Onboarding Guide
Point the agent at any public GitHub repository URL or local directory. It generates `ONBOARDING_GUIDE.md` under the specified output directory.
```bash
# Analyze a GitHub repository
python onboard.py analyze https://github.com/fastapi/fastapi --output ./fastapi_onboarding

# Analyze a local codebase folder
python onboard.py analyze C:\Users\Example\MyProject --output ./my_onboarding
```

### 2. Ask a Codebase Question
Ask freeform questions and get answers with exact file and line-number citations.
```bash
python onboard.py ask https://github.com/fastapi/fastapi "How are exception handlers registered?"
```

### 3. Run Standalone MCP Server
You can launch the codebase concierge as a standalone stdio-based MCP server. This allows tools like Claude Desktop or Cursor to inspect a codebase through our custom AST and symbol search tools.
```bash
python onboard.py serve C:\Users\Example\MyProject
```

---

## Standalone MCP Integration (Claude Desktop / Cursor)

To connect the server to Claude Desktop, add it to your configuration file (e.g. `C:\Users\<user>\AppData\Roaming\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "codebase-onboarding-concierge": {
      "command": "python",
      "args": ["C:/path/to/codebase-onboarding-agent/src/mcp_server.py"],
      "env": {
        "ONBOARD_REPO_PATH": "C:/path/to/target/repo"
      }
    }
  }
}
```

---

## Web API Server (FastAPI)

Run the backend web server locally:
```bash
python src/server.py
```
It starts on port `8080` (or `PORT` env variable) and exposes the following REST endpoints:

- **GET `/`**: Health check.
- **POST `/analyze`**: Generates onboarding guide.
  - Payload: `{"repo_url": "https://github.com/user/repo"}`
  - Returns: `{"status": "success", "onboarding_guide": "..."}`
- **POST `/ask`**: Interactive Q&A.
  - Payload: `{"repo_url": "https://github.com/user/repo", "question": "where is auth handled?"}`
  - Returns: `{"status": "success", "answer": "..."}`

---

## Security Sandboxing

Security constraints are hardcoded into the MCP server implementation:
- **Strict Read-Only**: The server implements no write/command-execution tools.
- **Path Sanitization**: Every file operation verifies that paths resolve inside the `ONBOARD_REPO_PATH` directory using path prefix validation (`os.path.commonpath`), completely blocking directory traversal (`..`) attempts.

---

## Containerization & Cloud Run Deployment

You can package and deploy this service to Google Cloud Run:

### 1. Build and Run Container Locally
Ensure Docker is installed and running, then:
```bash
# Build the Docker image
docker build -t codebase-onboarding-concierge .

# Run the container locally (passing API Key via environment)
docker run -p 8080:8080 -e GEMINI_API_KEY="your_api_key" codebase-onboarding-concierge
```

### 2. Deploy to Google Cloud Run
Deploy the container to Google Cloud Run in a single command using `gcloud`:
```bash
# Build & deploy directly from source
gcloud run deploy codebase-onboarding-concierge \
    --source . \
    --platform managed \
    --region us-central1 \
    --set-env-vars GEMINI_API_KEY="your_gemini_api_key" \
    --allow-unauthenticated
```
It will output a service URL (e.g. `https://codebase-onboarding-concierge-xxxx-uc.a.run.app`) where you can submit POST requests.

---

## Running the Unit Tests
You can run the codebase unit tests at any time without needing an API key:
```bash
python tests/test_onboard.py
```
