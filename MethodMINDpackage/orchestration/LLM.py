import google.generativeai as genai
from MethodMINDpackage.params import *

def llm_gemini_response_generation(text):
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(text, generation_config=genai.types.GenerationConfig(max_output_tokens=700))
    return response.text


# def llm_gemini_response_generation(text):
#     # Configure the Gemini API with your key
#     genai.configure(api_key=GEMINI_API_KEY)

#     # Create a new generative model
#     model = genai.GenerativeModel(model_name="gemini-1.5-flash")

#     # Prepare the API request with reset set to true to forget previous queries
#     request_data = {
#         "contents": [
#             {
#                 "role": "user",
#                 "parts": [
#                     {
#                         "text": text
#                     }
#                 ]
#             }
#         ],
#         "reset": True
#     }

#     # Send the request and get the response
#     response = model.generate_content(request_data, generation_config=genai.types.GenerationConfig(max_output_tokens=700))

#     # Return the generated response text
#     return response.text
