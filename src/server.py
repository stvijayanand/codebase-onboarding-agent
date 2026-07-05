import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Ensure src directory is in sys.path
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from agents.orchestrator import OnboardingOrchestrator

app = FastAPI(
    title="Codebase Onboarding Concierge API",
    description="HTTP API wrapper for the Codebase Onboarding Concierge multi-agent system."
)

class AnalyzeRequest(BaseModel):
    repo_url: str

class AskRequest(BaseModel):
    repo_url: str
    question: str

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Serve frontend SPA
@app.get("/")
def read_root():
    return FileResponse(os.path.join(src_dir, "static", "index.html"))

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "codebase-onboarding-concierge"}

app.mount("/static", StaticFiles(directory=os.path.join(src_dir, "static")), name="static")

@app.post("/analyze")
async def analyze_repo(req: AnalyzeRequest):
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY is not configured on the server."
        )
        
    orchestrator = OnboardingOrchestrator()
    # Save guide in a temp output dir
    output_dir = "./temp_output"
    try:
        output_file = await orchestrator.run_analysis(req.repo_url, output_dir)
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "status": "success", 
            "repo_url": req.repo_url,
            "onboarding_guide": content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(req: AskRequest):
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY is not configured on the server."
        )
        
    orchestrator = OnboardingOrchestrator()
    try:
        answer = await orchestrator.run_qa_session(req.repo_url, req.question)
        return {
            "status": "success", 
            "repo_url": req.repo_url,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get port from environment (Cloud Run injects PORT)
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
