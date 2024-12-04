import google.generativeai as genai
from MethodMINDpackage.params import *

def llm_gemini_response_generation(text):
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    model.max_output_tokens = 400
    response = model.generate_content(text)
    return response.text
