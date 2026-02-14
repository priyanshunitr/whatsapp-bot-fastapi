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
    chat_history.extend([line.strip() for line in f.readlines()])

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
    chat_history.append(HumanMessage(content="User: " + message))
    prompt = template.invoke({'recorded_chats': chat_history })
    result = model.invoke (prompt)
    chat_history.append(AIMessage(content=("Bot: " + result.content)))

    # Create a new Twilio MessagingResponse
    resp = MessagingResponse()
    resp.message(result.content)

    # Save chat history
    with open(r'D:\old\Dev\whatsapp-bot-fastapi\chat_history.txt', 'w') as f:
        # Convert message objects to strings and ensure we get just the content
        history_lines = []
        for msg in chat_history:
            # Skip SystemMessages to prevent duplication on reload
            if isinstance(msg, SystemMessage):
                continue
                
            content = ""
            if hasattr(msg, 'content'):
                content = msg.content
            else:
                content = str(msg).strip()
            
            # Also filter out string versions if they got saved previously
            if "You are a helpful assistant" in content:
                 continue
                 
            history_lines.append(content)
        f.write('\n'.join(history_lines))

    # Return the TwiML (as XML) response
    return Response(content=str(resp), media_type="application/xml")
