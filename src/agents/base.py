import os
import json
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
import colorama

colorama.init()

# Define the tools manually for Gemini API tool declaration
mcp_tools = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="list_files",
            description="Recursively lists all files in the repository sandbox, excluding binary files, node_modules, and typical package dependencies.",
            parameters=types.Schema(
                type="OBJECT",
                properties={}
            )
        ),
        types.FunctionDeclaration(
            name="read_file",
            description="Safely reads the contents of a text file inside the sandbox by relative path.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "path": types.Schema(
                        type="STRING",
                        description="The relative path of the file to read (must be inside the sandbox)."
                    )
                },
                required=["path"]
            )
        ),
        types.FunctionDeclaration(
            name="search_symbols",
            description="Searches for symbols (class, function, method definitions) matching a regex or substring across files in the sandbox.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query": types.Schema(
                        type="STRING",
                        description="The substring or regex query to match against file contents (e.g. 'class ', 'def ', 'function ')."
                    )
                },
                required=["query"]
            )
        ),
        types.FunctionDeclaration(
            name="get_git_history",
            description="Gets the Git commit history log and contributor analysis for the repository.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "limit": types.Schema(
                        type="INTEGER",
                        description="Maximum number of commits to return (default: 20)."
                    )
                }
            )
        ),
        types.FunctionDeclaration(
            name="run_ast_query",
            description="Parses a file imports, classes, and top-level functions (AST parse for Python files, regex parser fallback for Javascript, TypeScript, Go, etc.).",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "path": types.Schema(
                        type="STRING",
                        description="The relative path of the file to run the AST query on."
                    )
                },
                required=["path"]
            )
        )
    ]
)

class BaseAgent:
    def __init__(self, name: str, role: str, system_instruction: str, model_name: Optional[str] = None):
        self.name = name
        self.role = role
        self.system_instruction = system_instruction
        # Fall back to custom model env or default to gemini-2.5-flash
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Initialize Google GenAI client
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        self.client = genai.Client(api_key=api_key)
        
    async def run(self, mcp_session, prompt: str) -> str:
        """
        Runs the agent task with access to the MCP client session.
        Interprets and executes tool calls recursively.
        """
        print(f"\n{colorama.Fore.GREEN}=== [{self.name} - {self.role}] Starting Task ==={colorama.Style.RESET_ALL}")
        print(f"{colorama.Fore.WHITE}Prompt: {prompt}{colorama.Style.RESET_ALL}")
        
        # Setup conversation history
        # We start with the prompt
        contents = [prompt]
        
        config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=[mcp_tools],
            temperature=0.2
        )
        
        step = 1
        while True:
            # Generate content from Gemini
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # If no function calls, return final text
            if not response.function_calls:
                print(f"{colorama.Fore.GREEN}=== [{self.name}] Completed ==={colorama.Style.RESET_ALL}\n")
                return response.text or ""
                
            # Append model's response (with function call) to history
            contents.append(response.candidates[0].content)
            
            # Process function calls
            function_responses = []
            for function_call in response.function_calls:
                tool_name = function_call.name
                args = dict(function_call.args) if function_call.args else {}
                
                print(f"  {colorama.Fore.YELLOW}[Step {step} - Tool Call]{colorama.Style.RESET_ALL} {tool_name} with arguments: {json.dumps(args)}")
                
                # Execute the tool via MCP
                try:
                    mcp_result = await mcp_session.call_tool(tool_name, arguments=args)
                    
                    # Extract text content from MCP result
                    tool_output = ""
                    for block in mcp_result.content:
                        if block.type == "text":
                            tool_output += block.text
                    
                    # Truncate debug log if long
                    preview = tool_output[:120].replace('\n', ' ')
                    dots = "..." if len(tool_output) > 120 else ""
                    print(f"  {colorama.Fore.BLUE}[Step {step} - Tool Response]{colorama.Style.RESET_ALL} (length={len(tool_output)}): {preview}{dots}")
                    
                except Exception as e:
                    tool_output = f"Error executing tool '{tool_name}': {str(e)}"
                    print(f"  {colorama.Fore.RED}[Step {step} - Tool Error]{colorama.Style.RESET_ALL} {tool_output}")
                
                # Format response block
                resp_part = types.Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_output}
                )
                function_responses.append(resp_part)
                
            # Append function responses as user turn
            contents.append(types.Content(role="user", parts=function_responses))
            step += 1
