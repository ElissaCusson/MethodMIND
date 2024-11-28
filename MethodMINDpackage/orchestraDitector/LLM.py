import google.generativeai as genai
import os
# from dotenv import load_dotenv

def llm_test():
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content("Explain how AI works")
    return response.text

print(llm_test())
