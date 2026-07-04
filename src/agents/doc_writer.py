import os
import sys
from typing import Optional

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agents.base import BaseAgent

DOC_WRITER_PROMPT = """You are the Doc-Writer Agent. Your task is to compile a beautifully structured, onboarding README / guide for new engineers ramping up on this codebase.

Your objectives:
1. Synthesize the Explorer's structural report and the Mapper's data flow report into a single premium document.
2. Structure the document with the following specific sections:
   - **Repository Overview & Architecture Map**: A brief introduction to the repo's purpose, including a visual Mermaid diagram representing the architecture and relationships between services.
   - **Directory & File Hierarchy**: A clean directory list showing what each path is responsible for.
   - **Core Workflows & Data Flows**: Detailed answers to "Where does X live?" (e.g. Authentication, Database connection, router configs, tests) and a step-by-step description of how data flows (e.g. API request handling).
   - **Setup Walkthrough**: Complete, reproducible commands to install dependencies, run development servers, run tests, and configure environment variables.
   - **Good First Issues**: A prioritized, ranked list of 3-4 suggestions for beginner tasks or codebase modifications that new hires can take on (e.g., adding an API validation, fixing a specific model boundary, writing tests). Explain *why* these are good first issues and which files need to be modified.

Ensure the document is written in clear, professional technical English, avoiding placeholders. Format code blocks, directories, and files as markdown links or code snippets. Use Mermaid formatting carefully for clean rendering.
"""

class DocWriterAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None):
        super().__init__(
            name="DocWriterAgent",
            role="Onboarding Technical Writer",
            system_instruction=DOC_WRITER_PROMPT,
            model_name=model_name
        )

    async def write_guide(self, explorer_report: str, mapper_report: str) -> str:
        prompt = f"""Synthesize the following Explorer and Mapper reports into a premium Onboarding Guide. 
Make sure it follows all formatting instructions and includes a Mermaid architecture graph, setup guide, and ranked good first issues.

--- Explorer Report ---
{explorer_report}

--- Mapper Report ---
{mapper_report}
"""
        # Since Doc-Writer just does synthesis, we pass a dummy session (or None)
        # because the prompt is self-contained and the Doc-Writer doesn't need to call tools.
        return await self.run(None, prompt)
