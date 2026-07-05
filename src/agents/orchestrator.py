import os
import sys
import hashlib
import asyncio
import subprocess
from typing import Optional, Dict, Any

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agents.explorer import ExplorerAgent
from agents.mapper import MapperAgent
from agents.doc_writer import DocWriterAgent
from agents.qa import QAAgent

def setup_repo_sandbox(repo_source: str) -> str:
    """
    Returns the absolute path to the sandbox.
    Clones git repositories if a URL is provided, or validates local path.
    """
    # If path exists locally, treat as local repo
    if os.path.exists(repo_source):
        return os.path.abspath(repo_source)
        
    # Otherwise treat as git url
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cloned_dir = os.path.join(project_root, "cloned_repos")
    os.makedirs(cloned_dir, exist_ok=True)
    
    # Hash URL for unique local name
    url_hash = hashlib.md5(repo_source.encode("utf-8")).hexdigest()[:8]
    repo_name = repo_source.split("/")[-1].replace(".git", "")
    target_path = os.path.join(cloned_dir, f"{repo_name}_{url_hash}")
    
    if os.path.exists(target_path):
        print(f"Using cached clone of {repo_source} at:\n  {target_path}")
        return target_path
        
    print(f"Cloning public repository:\n  URL: {repo_source}\n  To:  {target_path}")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_source, target_path],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            stdin=subprocess.DEVNULL,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        )
        print("Cloning completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}", file=sys.stderr)
        raise e
        
    return target_path

class OnboardingOrchestrator:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name

    async def run_analysis(self, repo_source: str, output_dir: str) -> str:
        """
        Runs the full analysis pipeline: Explorer -> Mapper -> Doc-Writer.
        Saves the guide into the output directory and returns the path.
        """
        sandbox_path = setup_repo_sandbox(repo_source)
        
        # Configure standard Stdio server params for the MCP subprocess
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        server_script = os.path.join(src_dir, "mcp_server.py")
        
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            env={**os.environ, "ONBOARD_REPO_PATH": sandbox_path}
        )
        
        print("Starting sandboxed MCP Server process...")
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                print("Initializing MCP Client Session...")
                await session.initialize()
                print("MCP Server handshake successful.")
                
                # Instantiate agents
                explorer = ExplorerAgent(model_name=self.model_name)
                mapper = MapperAgent(model_name=self.model_name)
                doc_writer = DocWriterAgent(model_name=self.model_name)
                
                # Step 1: Run Explorer Agent
                explorer_report = await explorer.analyze(session)
                
                # Step 2: Run Mapper Agent
                mapper_report = await mapper.analyze(session, explorer_report)
                
                # Step 3: Run Doc-Writer Agent (does not need tools, purely synthesizes reports)
                print("\nSynthesizing final onboarding guide document...")
                guide_content = await doc_writer.write_guide(explorer_report, mapper_report)
                
                # Save guide to output path
                os.makedirs(output_dir, exist_ok=True)
                guide_filename = "ONBOARDING_GUIDE.md"
                output_file = os.path.join(output_dir, guide_filename)
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(guide_content)
                    
                print(f"Onboarding guide successfully generated at:\n  {output_file}")
                return output_file

    async def run_qa_session(self, repo_source: str, question: str) -> str:
        """
        Runs the interactive Q&A agent for a codebase question.
        """
        sandbox_path = setup_repo_sandbox(repo_source)
        
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        server_script = os.path.join(src_dir, "mcp_server.py")
        
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            env={**os.environ, "ONBOARD_REPO_PATH": sandbox_path}
        )
        
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                qa_agent = QAAgent(model_name=self.model_name)
                answer = await qa_agent.ask(session, question)
                return answer
