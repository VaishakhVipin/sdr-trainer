import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash')

def generate_response(user_input, history, persona, offer):
    system_prompt = f"""
You are simulating a skeptical prospect in a mock sales call.

Persona:
{persona}

Offer being pitched:
{offer}

Behavior:
- You are skeptical, cautious, and realistic.
- You ask tough questions.
- You challenge vague claims.
- You act like a busy professional who doesn’t want to waste time.

Keep responses short, real, and natural — like a real conversation.
    """

    conversation = f"{history}\nUser: {user_input}\nYou:"

    res = model.generate_content(system_prompt + "\n" + conversation)
    return res.text.strip()


def score_call(history, persona, offer):
    prompt = f"""
You are an expert sales coach. Analyze the following mock sales call.

Persona:
{persona}

Offer:
{offer}

Conversation:
{history}

Return a score out of 100 for the call. (specific integral numeric value in decimal number system)

Return ONLY actionable feedback as a list of bullet points. Do NOT include any summary, filler, or overall impressions. Be concise and specific. Example:
- Ask more open-ended questions about the prospect's needs.
- Quantify the value proposition with numbers.
- Address objections about pricing directly.
"""
    response = model.generate_content(prompt)
    import json
    try:
        result = json.loads(response.text.strip())
    except Exception:
        result = {"score": None, "feedback": response.text.strip()}
    return result


def generate_session_title(history, persona, offer):
    prompt = f"""
Given the following mock sales call, persona, and offer, generate a short, catchy, and relevant title for the session. The title should be 3-8 words, descriptive, and suitable for displaying in a dashboard. Do NOT include any filler or explanation, just the title.

Persona:
{persona}

Offer:
{offer}

Conversation:
{history}
"""
    response = model.generate_content(prompt)
    return response.text.strip()
