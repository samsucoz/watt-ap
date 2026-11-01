from fastapi import FastAPI, Request, Response, Query

app = FastAPI()

# رمز التحقق الخاص بك (يمكنك اختياره كما تشاء)
VERIFY_TOKEN = "my_secret_token_123"

@app.get("/")
def read_root():
    return {"status": "bot is running successfully"}

# نقطة التحقق من الـ Webhook لـ Meta (GET)
@app.get("/webhook")
def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)

# نقطة استقبال الرسائل الواردة من واتساب (POST)
@app.post("/webhook")
async def receive_whatsapp_message(request: Request):
    data = await request.json()
    print("Incoming WhatsApp Data:", data)
    return {"status": "success"}
