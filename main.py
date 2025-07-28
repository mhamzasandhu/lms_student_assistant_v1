import requests
from langchain_groq import ChatGroq
from fastapi import FastAPI, Request
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# ============ CONFIGURATION ============
GROQ_API_KEY = "your key"  # replace with your key
MODEL_NAME = "llama-3.3-70b-versatile"  # or llama3-70b, etc.
STUDENT_API_BASE = "https://lms.prismaticcrm.com/api/student-profile"
# ========================================

# === Initialize LLM ===
llm = ChatGroq(
    temperature=0.6,
    model_name=MODEL_NAME,
    api_key=GROQ_API_KEY,
)

# === Load Prompt Template ===
with open("prompt_template1.txt", "r") as f:
    prompt_template = f.read()

prompt = PromptTemplate.from_template(prompt_template)

# === FastAPI App ===
app = FastAPI()

# === Utility: Fetch Student Profile ===
def fetch_student_profile(student_id: str) -> str:
    try:
        url = f"{STUDENT_API_BASE}/{student_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        profile_text = "\n".join([f"{k}: {v}" for k, v in data.items()])
        return profile_text
    except Exception as e:
        return f"Unable to fetch profile. Error: {e}"

# === Build LangChain Chain ===
def build_chain(student_profile: str):
    chain = (
        {
            "student_profile": RunnablePassthrough(),
            "input": RunnablePassthrough()
        }
        | prompt
        | llm
    )
    return chain

# === API Endpoint ===
@app.post("/chat/{student_id}")
async def chat_with_student(student_id: str, request: Request):
    body = await request.json()
    user_question = body.get("message")

    if not user_question:
        return {"error": "Missing 'message' in request body"}

    profile_text = fetch_student_profile(student_id)
    chain = build_chain(profile_text)
    response = chain.invoke(user_question)

    return {"reply": response.content}
