import google.generativeai as genai
from MethodMINDpackage.params import *
# from dotenv import load_dotenv

def llm_test(text):
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    response = model.generate_content(text)
    return response.text
