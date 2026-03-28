from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="S1 Assistant Backend")

class UserInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "S1 Assistant backend is running"}

@app.post("/chat")
def chat(data: UserInput):
    user_text = data.text.lower()

    if "hello" in user_text or "hi" in user_text:
        return {"reply": "Hello! I am S1 Assistant."}

    if "time" in user_text:
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return {"reply": f"Current time is {now}"}

    return {"reply": "I heard you. More features coming soon."}
