from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.model_loader import load_model
from app.summarizer import build_summarizer, summarize

app = FastAPI(title="AI-Tech-Watch LLM API")

class TextRequest(BaseModel):
    text: str

print("Initializing model...")
tokenizer, model = load_model()
summarizer = build_summarizer(tokenizer, model)
print("Model ready")

@app.post("/summarize")
def summarize_text(req: TextRequest):
    try:
        summary = summarize(req.text, summarizer)
        print(summary)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "ok", "message": "AI-Tech-Watch LLM service is running"}
