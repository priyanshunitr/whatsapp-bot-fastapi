from fastapi import FastAPI, Response, Request
from twilio.twiml.messaging_response import MessagingResponse
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI()

chat_history = [
    SystemMessage(content = 'You are a helpful assistant')
]

with open (r'D:\old\Dev\whatsapp-bot-fastapi\chat_history.txt') as f:
    chat_history.extend(f.readlines())

template = ChatPromptTemplate([
    ('system', 'You are a helpful AI assistant'),
    MessagesPlaceholder ( variable_name = 'recorded_chats')
])

#app======================================================================================

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/whatsapp")
async def reply_whatsapp(request: Request):
    form_data = await request.form()
    message = form_data.get('Body')
    print(f"Message from user: {message}")

    ## INJECTING BOT ##
    chat_history.append(HumanMessage(content=message))
    prompt = template.invoke({'recorded_chats': chat_history })
    result = model.invoke (prompt)
    chat_history.append(AIMessage(content=(result.content)))

    # Create a new Twilio MessagingResponse
    resp = MessagingResponse()
    resp.message(result.content)

    # Return the TwiML (as XML) response
    return Response(content=str(resp), media_type="application/xml")
