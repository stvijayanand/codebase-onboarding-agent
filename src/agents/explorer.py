import os
import sys
from typing import Optional

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agents.base import BaseAgent

EXPLORER_PROMPT = """You are the Explorer Agent. Your role is to walk the codebase, index the files, detect the language/tech stack, and review the git history. 

Your objectives:
1. Walk the directory tree (using `list_files`).
2. Identify core programming languages, config files, package managers, and dependencies (e.g. package.json, requirements.txt, go.mod).
3. Query the commit history (using `get_git_history`) to learn about active development paths and top developers/SMEs.
4. Output a comprehensive Markdown structural report of the codebase. Include:
   - High-level directory tree representation (group files logically).
   - Technology stack detected and packaging setup.
   - Core directories and their high-level responsibilities.
   - Top contributors list and active developer insights from git history.

Use your tools to query information. Do not speculate or make assumptions. Provide citations to configuration files (e.g., package.json, go.mod) where dependencies are listed.
"""

class ExplorerAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None):
        super().__init__(
            name="ExplorerAgent",
            role="Codebase Structural Analyst",
            system_instruction=EXPLORER_PROMPT,
            model_name=model_name
        )

    async def analyze(self, mcp_session) -> str:
        prompt = "Walk the codebase directory tree, run git history inspection, and compile a structural overview report of the project."
        return await self.run(mcp_session, prompt)
