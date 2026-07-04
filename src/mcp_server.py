import os
import sys
from typing import List, Dict, Any

# Ensure the parent directory is in sys.path so we can import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from mcp.server.fastmcp import FastMCP
import json
from utils import (
    list_files_in_sandbox,
    read_file_safe,
    search_symbols_regex,
    get_git_history,
    run_ast_query
)

# Initialize FastMCP Server
mcp = FastMCP("Codebase Onboarding Concierge Server")

# Retrieve sandbox path from environment
def get_sandbox_dir() -> str:
    path = os.environ.get("ONBOARD_REPO_PATH")
    if not path:
        raise ValueError("ONBOARD_REPO_PATH environment variable must be set to run the onboarding server.")
    return os.path.abspath(path)

@mcp.tool(name="list_files", description="Recursively lists all files in the repository sandbox, excluding binary files and node_modules.")
def list_files() -> str:
    sandbox = get_sandbox_dir()
    return json.dumps(list_files_in_sandbox(sandbox), indent=2)

@mcp.tool(name="read_file", description="Safely reads the contents of a text file inside the sandbox by relative path.")
def read_file(path: str) -> str:
    sandbox = get_sandbox_dir()
    return read_file_safe(sandbox, path)

@mcp.tool(name="search_symbols", description="Searches for symbols matching a regex or substring across files in the sandbox.")
def search_symbols(query: str) -> str:
    sandbox = get_sandbox_dir()
    return json.dumps(search_symbols_regex(sandbox, query), indent=2)

@mcp.tool(name="get_git_history", description="Gets the Git commit history log and contributor analysis for the repository.")
def git_history(limit: int = 20) -> str:
    sandbox = get_sandbox_dir()
    return json.dumps(get_git_history(sandbox, limit), indent=2)

@mcp.tool(name="run_ast_query", description="Parses a file imports, classes, and top-level functions (AST parse for python, regex fallback for others).")
def ast_query(path: str) -> str:
    sandbox = get_sandbox_dir()
    return json.dumps(run_ast_query(sandbox, path), indent=2)

if __name__ == "__main__":
    # FastMCP uses stdio transport by default if run directly
    mcp.run()
