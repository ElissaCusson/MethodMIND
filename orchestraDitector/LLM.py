import google.generativeai as genai
import os
from dotenv import load_dotenv

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(model_name="gemini-1.5-flash")
response = model.generate_content("Explain how AI works")
print(response.text)
