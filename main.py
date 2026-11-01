import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

# بيانات الـ Meta WhatsApp API
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "ضع_رمز_الوصول_هنا")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "ضع_معرف_الهاتف_هنا")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_secure_token_123")

@app.get("/")
async def root():
    return {"status": "WhatsApp Admin Bot is running successfully!"}

@app.get("/webhook")
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode and token and mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return "Verification Failed", 403

@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        if "messages" in value:
            message = value["messages"][0]
            sender = message["from"]
            
            # فحص نوع الرسالة الواردة (نص، صورة، فيديو، أو وثيقة/ملف)
            msg_type = message.get("type")
            
            # 1. إذا كانت الرسالة عبارة عن مستند أو وثيقة (Word, Excel, PDF...)
            if msg_type == "document":
                reply_text = "مرحباً، معكم مبارك. تم استلام الوثيقة أو الملف بنجاح، جاري مراجعتها في انتظار الرد. شكراً لتفهمكم."
            
            # 2. إذا كانت الرسالة عبارة عن صورة أو فيديو
            elif msg_type in ["image", "video"]:
                reply_text = "مرحباً، معكم مبارك. تم استلام الصورة أو الفيديو بنجاح، جاري الاطلاع عليه. شكراً لك."
            
            # 3. إذا كانت الرسالة نصية عادية
            elif msg_type == "text":
                text = message["text"]["body"].strip().lower()
                
                # تحية الصباح
                if any(word in text for word in ["صباح", "bonjour", "good morning"]):
                    reply_text = "طاب يومكم وصباح الخير، معكم مبارك. أهلاً بك، كيف يمكنني مساعدتك اليوم؟"
                
                # تحية المساء
                elif any(word in text for word in ["مساء", "مساء الخير", "bonsoir", "good evening"]):
                    reply_text = "طاب مساؤكم بكل خير، معكم مبارك. تفضل بطرح استفسارك وسأجيبك قريباً."

                # السلام والترحيب العام
                elif any(word in text for word in ["سلام", "مرحبا", "سلام عليكم", "السلام عليكم", "hello", "hi"]):
                    reply_text = "وعليكم السلام ورحمة الله وبركاته. معكم مبارك، جاري تحويل طلبك وفي انتظار الرد. شكراً على تفهمكم."

                # الاستفسارات عن الطلبات أو المعاملات
                elif any(word in text for word in ["طلب", "خدمة", "معاملة", "تتبع", "أوراق"]):
                    reply_text = "مرحباً بك، معكم مبارك. تم تسجيل طلبك الإداري بنجاح، وهو قيد المعالجة الآن. يرجى الانتظار قليلاً وشكراً لتفهمكم."

                # الرد العام والافتراضي لأي نص آخر
                else:
                    reply_text = "أنا مبارك، تلقيت رسالتك. انتظر قليلاً من فضلك وسأكون معك في أقرب وقت."
            
            else:
                # لأي نوع رسائل أخرى غير محددة
                reply_text = "مرحباً، معكم مبارك. تلقيت رسالتك وسأقوم بالاطلاع عليها قريباً."
                
            # إرسال الرد تلقائياً للرقم المرسل
            send_reply(sender, reply_text)
            
    except Exception as e:
        print(f"Error: {e}")
    return {"status": "ok"}

def send_reply(recipient, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": recipient, "type": "text", "text": {"body": text}}
    requests.post(url, json=payload, headers=headers)
