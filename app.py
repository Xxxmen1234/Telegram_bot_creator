import os
import asyncio
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from telegram import Bot, Update
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class BotRequest(BaseModel):
    token: str
    type: str
    content: str

@app.get("/")
def health_check():
    return {"status": "Server is up!"}

# --- החלק החדש: טיפול בהודעות נכנסות מטלגרם ---
@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    data = await request.json()
    update = Update.de_json(data, Bot(token=token))
    
    if update.message and update.message.text:
        chat_id = update.message.chat_id
        user_text = update.message.text
        bot = Bot(token=token)

        # כאן ה-AI נכנס לפעולה ועונה למשתמש בטלגרם!
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

        response = model.generate_content(f"You are a helpful telegram bot. The user said: {user_text}")
        
        await bot.send_message(chat_id=chat_id, text=response.text)
    
    return {"status": "ok"}

# --- עדכון פונקציית יצירת הבוט ---
@app.post("/create_bot")
async def create_bot(request: BotRequest):
    try:
        bot = Bot(token=request.token)
        bot_info = await bot.get_me()
        
        # הגדרת ה-Webhook: אומרים לטלגרם לשלוח הודעות לכתובת של Render
        webhook_url = f"https://telegram-bot-creator-9bhw.onrender.com/webhook/{request.token}"
        await bot.set_webhook(url=webhook_url)
        
        return {
            "status": "success",
            "bot_name": bot_info.first_name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
