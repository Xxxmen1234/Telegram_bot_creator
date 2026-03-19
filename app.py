import os
import google.generativeai as genai
from fastapi import FastAPI, Request
from telegram import Bot, Update

app = FastAPI()

# הגדרת Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

@app.get("/")
def home():
    return {"status": "Bot is running"}

@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    try:
        data = await request.json()
        bot = Bot(token=token)
        update = Update.de_json(data, bot)
        
        if update.message and update.message.text:
            chat_id = update.message.chat_id
            user_text = update.message.text
            
            # יצירת תשובה מה-AI
            response = model.generate_content(user_text)
            await bot.send_message(chat_id=chat_id, text=response.text)
            
        return {"ok": True}
    except Exception as e:
        print(f"Error: {e}")
        return {"ok": False, "error": str(e)}
