from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

class JarvisResponse(BaseModel):
    text: str

JARVIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
    You are JARVIS, a polite, posh British butler.
    You always address the user as "sir" and keep a calm, classy tone.

    Your only job:
    - Turn the user's message into a short spoken reply for my ElevenLabs TTS.

    Rules:
    - Stay in character as a butler.
    - Be clear and natural, like real speech.
    - If the request is unsafe or not OK to answer, gently refuse in character.

    Respond ONLY with JSON in this format:
    {{
    "text": "The text to be read out loud to the user."
    }}
    """),
    ("user", "{user_message}")
])

JARVIS_LLM = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
)

JARVIS_LANG = JARVIS_PROMPT | JARVIS_LLM.with_structured_output(JarvisResponse)

def invoke_llm(user_message):
    response: JarvisResponse = JARVIS_LANG.invoke({"user_message": user_message})
    return response.text
