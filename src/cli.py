import os
import sys
import argparse
import asyncio
import colorama
import traceback

# Ensure src directory is in sys.path
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from agents.orchestrator import OnboardingOrchestrator

colorama.init()

def check_api_key():
    if not os.environ.get("GEMINI_API_KEY"):
        print(f"{colorama.Fore.RED}Error: GEMINI_API_KEY environment variable is not set.{colorama.Style.RESET_ALL}", file=sys.stderr)
        print("Please export it before running onboard command:", file=sys.stderr)
        print("  Windows (Cmd):  set GEMINI_API_KEY=your_key", file=sys.stderr)
        print("  Windows (PS):   $env:GEMINI_API_KEY=\"your_key\"", file=sys.stderr)
        print("  Linux/macOS:    export GEMINI_API_KEY=\"your_key\"", file=sys.stderr)
        sys.exit(1)

def handle_analyze(args):
    check_api_key()
    orchestrator = OnboardingOrchestrator(model_name=args.model)
    
    print(f"{colorama.Fore.CYAN}=== Starting Codebase Analysis ==={colorama.Style.RESET_ALL}")
    print(f"Target: {args.repo}")
    print(f"Output: {args.output}")
    if args.model:
        print(f"Model:  {args.model}")
        
    try:
        output_file = asyncio.run(orchestrator.run_analysis(args.repo, args.output))
        print(f"\n{colorama.Fore.GREEN}Success! Onboarding guide generated successfully.{colorama.Style.RESET_ALL}")
        print(f"You can view it at: {output_file}")
    except Exception as e:
        print(f"\n{colorama.Fore.RED}Error during analysis:{colorama.Style.RESET_ALL}", file=sys.stderr)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        sys.exit(1)

def handle_ask(args):
    check_api_key()
    orchestrator = OnboardingOrchestrator(model_name=args.model)
    
    print(f"{colorama.Fore.CYAN}=== Asking Codebase Q&A ==={colorama.Style.RESET_ALL}")
    print(f"Repository: {args.repo}")
    print(f"Question:   \"{args.question}\"")
    print(f"Thinking...")
    
    try:
        answer = asyncio.run(orchestrator.run_qa_session(args.repo, args.question))
        print(f"\n{colorama.Fore.GREEN}=== Onboarding Concierge Answer ==={colorama.Style.RESET_ALL}")
        print(answer)
        print(f"{colorama.Fore.GREEN}==================================={colorama.Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{colorama.Fore.RED}Error during Q&A session:{colorama.Style.RESET_ALL}", file=sys.stderr)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        sys.exit(1)

def handle_serve(args):
    # Standalone serve does not strictly require GEMINI_API_KEY (can be run for third-party clients)
    repo_path = os.path.abspath(args.repo_path)
    if not os.path.exists(repo_path):
        print(f"{colorama.Fore.RED}Error: Local repository path '{repo_path}' does not exist.{colorama.Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
        
    os.environ["ONBOARD_REPO_PATH"] = repo_path
    
    # Import the mcp server module
    try:
        # We need the parent directory of mcp_server in sys.path
        if src_dir not in sys.path:
            sys.path.append(src_dir)
            
        import mcp_server
        print(f"{colorama.Fore.GREEN}Starting standalone MCP Server for: {repo_path}{colorama.Style.RESET_ALL}")
        print("Listening on stdio (compatible with Claude Desktop, Cursor, etc.)...")
        mcp_server.mcp.run()
    except Exception as e:
        print(f"{colorama.Fore.RED}Error starting MCP server: {str(e)}{colorama.Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Codebase Onboarding Concierge - Analyze repositories, search code, and run interactive Q&A.",
        prog="onboard"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")
    
    # Subcommand: analyze
    parser_analyze = subparsers.add_parser("analyze", help="Analyze repository structural map and trace data flow to build guide.")
    parser_analyze.add_argument("repo", help="Local directory path or public Git repository URL (HTTPS).")
    parser_analyze.add_argument("--output", "-o", default="./onboard_output", help="Directory where ONBOARDING_GUIDE.md will be saved (default: ./onboard_output).")
    parser_analyze.add_argument("--model", "-m", help="Gemini model to use (default: gemini-2.5-flash).")
    
    # Subcommand: ask
    parser_ask = subparsers.add_parser("ask", help="Ask a freeform question about the codebase with precise file citations.")
    parser_ask.add_argument("repo", help="Local directory path or public Git repository URL (HTTPS).")
    parser_ask.add_argument("question", help="The question to ask about the codebase.")
    parser_ask.add_argument("--model", "-m", help="Gemini model to use (default: gemini-2.5-flash).")
    
    # Subcommand: serve
    parser_serve = subparsers.add_parser("serve", help="Expose repository tools as a standalone stdio MCP server.")
    parser_serve.add_argument("repo_path", help="Local directory path to expose.")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        handle_analyze(args)
    elif args.command == "ask":
        handle_ask(args)
    elif args.command == "serve":
        handle_serve(args)

if __name__ == "__main__":
    main()
