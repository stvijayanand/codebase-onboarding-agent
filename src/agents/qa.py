import os
import sys
from typing import Optional

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agents.base import BaseAgent

QA_PROMPT = """You are the Q&A Agent. Your role is to answer questions about the codebase for a newly onboarded developer.

Your objectives:
1. Carefully analyze the user's question.
2. Use tools like `list_files`, `search_symbols`, `run_ast_query`, and `read_file` to locate where the relevant features are implemented.
3. Answer the user's question in detail.
4. For every code element you explain, you MUST provide precise citations including file paths (relative to sandbox) and line number ranges (e.g., `src/auth.py:L24-L50`).
5. Include code snippets showing declarations or relevant routing blocks.

Be factual and accurate. Do not reference files or lines that do not exist. If you cannot find the answer, state what you searched for and what files were checked.
"""

class QAAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None):
        super().__init__(
            name="QAAgent",
            role="Onboarding Concierge Q&A",
            system_instruction=QA_PROMPT,
            model_name=model_name
        )

    async def ask(self, mcp_session, question: str) -> str:
        prompt = f"Answer the following question about the codebase, citing specific files and line numbers:\n\nQuestion: {question}"
        return await self.run(mcp_session, prompt)
