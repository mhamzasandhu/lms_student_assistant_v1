from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fetch_student_data import fetch_student_profile
from langchain_community.agent_toolkits import JsonToolkit, create_json_agent
from langchain_community.tools.json.tool import JsonSpec
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
load_dotenv() 
# Initialize FastAPI
app = FastAPI()

# Request schema
class QuestionRequest(BaseModel):
    student_id: str
    question: str

# Groq setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # set this in your environment
llm = ChatGroq(
    temperature=0.7,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY
)

@app.post("/ask")
def ask_student_question(req: QuestionRequest):
    student_data = fetch_student_profile(req.student_id)

    if "error" in student_data:
        raise HTTPException(status_code=400, detail=student_data["error"])

    # Wrap data with LangChain JSON agent
    json_spec = JsonSpec(dict_=student_data, max_value_length=4000)
    toolkit = JsonToolkit(spec=json_spec)
    agent = create_json_agent(llm=llm, toolkit=toolkit, verbose=True)

    try:
        result = agent.run(req.question)
        return {"answer": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
