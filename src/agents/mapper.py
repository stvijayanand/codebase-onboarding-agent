import os
import sys
from typing import Optional

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agents.base import BaseAgent

MAPPER_PROMPT = """You are the Mapper Agent. Your role is to trace code dependencies, class interfaces, module relationships, and data flows in the codebase.

Your objectives:
1. Identify major entry points (e.g., main.go, index.js, app.py, main.py).
2. Trace routes, API endpoints, or command line dispatchers (e.g. controllers, router definitions).
3. Search for symbols (e.g., Database connections, middleware, authentication flows) using `search_symbols` and `run_ast_query`.
4. Inspect source files (using `read_file`) to understand interface mappings and data passing schemas.
5. Output a comprehensive Markdown report mapping the codebase routing and data flow:
   - Entry points: Where execution starts and how systems boot.
   - API endpoints or key operations map.
   - Core data flow: From input/routing to processing/business logic to output/storage.
   - Key modules and dependency relationships.

Provide exact file names and code citations for classes and methods. Avoid generic statements; show real code routes.
"""

class MapperAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None):
        super().__init__(
            name="MapperAgent",
            role="Codebase Dependency and Flow Mapper",
            system_instruction=MAPPER_PROMPT,
            model_name=model_name
        )

    async def analyze(self, mcp_session, explorer_report: str) -> str:
        prompt = f"""Use the structural codebase details below to locate key components, trace files, perform AST queries, and trace data flow:
        
--- Explorer Structural Report ---
{explorer_report}
--- End of Explorer Report ---

Trace how routes are registered, what entry points exist, and how data moves between layers. Output a detailed Codebase Routing and Flow Map."""
        return await self.run(mcp_session, prompt)
