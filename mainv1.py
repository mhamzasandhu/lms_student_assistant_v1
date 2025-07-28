from fastapi import FastAPI, Request
import requests
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

# === CONFIG ===
GROQ_API_KEY = "Api key here"  # replace with your key
MODEL_NAME = "llama-3.3-70b-versatile"  # or llama3-70b, etc.
STUDENT_API_BASE = "https://lms.prismaticcrm.com/api/student-profile"
# === LLM Setup ===

llm = ChatGroq(
    temperature=0.7,
    model_name=MODEL_NAME,
    api_key=GROQ_API_KEY
)

# === Prompt Template ===
with open("prompt_template.txt", "r") as f:
    prompt_template = f.read()

prompt = PromptTemplate.from_template(prompt_template)

# === FastAPI App ===
app = FastAPI()

# === Formatter ===
def format_profile(json_data: dict) -> str:
    lines = []

    profile = json_data.get("profile", {})
    if profile:
        lines.append("🧑‍🎓 Basic Profile:")
        lines.extend([
            f"Name: {profile.get('first_name', '')} {profile.get('last_name', '')}",
            f"Email: {profile.get('email', 'N/A')}",
            f"Gender: {profile.get('gender', 'N/A')}",
            f"Date of Birth: {profile.get('date_of_birth', 'N/A')}",
            f"City: {profile.get('city', 'N/A')}",
            f"Course: {profile.get('course_name', 'N/A')}",
            f"Batch: {profile.get('batch_name', 'N/A')}",
            f"Branch: {profile.get('branch_name', 'N/A')}",
        ])

    assignments = json_data.get("lms", {}).get("assignments", {}).get("data", [])
    if assignments:
        lines.append("\n📚 Assignments:")
        for a in assignments:
            lines.append(f"- {a.get('add_title')} (Due: {a.get('submission_date')}, Marks: {a.get('total_marks')})")

    quizzes = json_data.get("lms", {}).get("quizzes", {}).get("data", [])
    if quizzes:
        lines.append("\n📝 Quizzes:")
        for q in quizzes:
            lines.append(f"- {q.get('title')} (Marks: {q.get('marks')}, Due: {q.get('lastDate')})")

    notes = json_data.get("lms", {}).get("lecture_notes", {}).get("data", [])
    if notes:
        lines.append("\n📄 Lecture Notes:")
        for n in notes:
            lines.append(f"- {n.get('lec_title')} (Date: {n.get('lec_date')})")

    videos = json_data.get("lms", {}).get("video_tutorials", {}).get("data", [])
    if videos:
        lines.append("\n🎥 Video Tutorials:")
        for v in videos:
            lines.append(f"- {v.get('video_title')} (Date: {v.get('lec_date')})")

    paid_fees = json_data.get("fee_invoices", {}).get("paid_invoices", {}).get("paid", [])
    if paid_fees:
        lines.append("\n💰 Fee Status:")
        for f in paid_fees:
            lines.append(f"- Paid: {f.get('fee_amount')} on {f.get('receipt_date')} (Receipt: {f.get('receipt_id')})")

    return "\n".join(lines)

# === Fetch Profile & Format ===
def fetch_student_profile(student_id: str) -> str:
    try:
        url = f"{STUDENT_API_BASE}/{student_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return format_profile(data)
    except Exception as e:
        return f"Error fetching student profile: {e}"

# === LangChain Chain Builder ===
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

# === FastAPI Endpoint ===
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
