import os
import asyncio
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telegram import Bot
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# הגדרת CORS - מאפשר לאתר ב-GitHub לדבר עם השרת
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# משיכת המפתח מהגדרות השרת (Render)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class BotRequest(BaseModel):
    token: str
    type: str
    content: str

@app.get("/")
def health_check():
    return {"status": "Server is up and running!"}

@app.post("/create_bot")
async def create_bot(request: BotRequest):
    try:
        final_logic = ""
        
        # 1. טיפול בבקשת AI (שימוש במפתח המאובטח מהשרת)
        if request.type == "ai":
            if not GEMINI_API_KEY:
                raise HTTPException(status_code=500, detail="Gemini API Key missing on server")
            
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"The user wants a telegram bot: {request.content}. Return ONLY a JSON list: [{{'cmd': 'start', 'txt': 'hello'}}]"
            
            response = model.generate_content(prompt)
            final_logic = response.text
        else:
            final_logic = request.content

        # 2. אימות מול טלגרם (בדיקה שהטוקן עובד)
        bot = Bot(token=request.token)
        bot_info = await bot.get_me()
        
        return {
            "status": "success",
            "bot_name": bot_info.first_name,
            "logic": final_logic
        }
        
    except Exception as e:
        # אם יש שגיאה (למשל טוקן לא תקין), נחזיר אותה לאתר
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # פורט 10000 הוא הפורט ש-Render מצפה לו
    uvicorn.run(app, host="0.0.0.0", port=10000)
