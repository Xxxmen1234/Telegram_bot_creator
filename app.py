from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from telegram import Bot
import asyncio
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# מאפשר לאתר שלך ב-GitHub לתקשר עם השרת הזה
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class BotRequest(BaseModel):
    token: str
    gemini_key: str = None
    type: str
    content: str

@app.get("/")
def health_check():
    return {"status": "Server is up and running!"}

@app.post("/create_bot")
async def create_bot(request: BotRequest):
    try:
        # 1. עיבוד התוכן לפי הסוג
        final_logic = ""
        
        if request.type == "ai" and request.gemini_key:
            genai.configure(api_key=request.gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"The user wants a telegram bot with this description: {request.content}. Return ONLY a simple JSON list of commands and their text responses. Example: [{{'cmd': 'start', 'txt': 'hello'}}] "
            response = model.generate_content(prompt)
            final_logic = response.text
        else:
            final_logic = request.content

        # 2. בדיקת הטוקן והפעלת הודעת ניסיון בטלגרם
        bot = Bot(token=request.token)
        bot_info = await bot.get_me()
        
        # כאן אנחנו רק בודקים שהבוט עובד. 
        # במערכת מלאה היינו מריצים פה 'Polling', אבל בשביל ההתחלה נחזיר אישור
        return {
            "status": "success",
            "bot_name": bot_info.first_name,
            "logic": final_logic
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
