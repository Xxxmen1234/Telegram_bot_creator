from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import uvicorn

app = FastAPI()

class BotRequest(BaseModel):
    token: str
    gemini_key: str
    type: str
    content: str

@app.get("/")
def home():
    return {"message": "Server is running!"}

@app.post("/create_bot")
async def create_bot(request: BotRequest):
    # אם זה AI - נבקש מ-Gemini לתרגם ללוגיקה
    if request.type == "ai":
        genai.configure(api_key=request.gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Translate this bot description to a simple JSON command-response list: {request.content}"
        response = model.generate_content(prompt)
        # כאן תבוא הלוגיקה שמפעילה את הבוט בטלגרם
        return {"status": "success", "ai_response": response.text}
    
    return {"status": "received", "data": request.content}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
