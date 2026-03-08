import os
import google.generativeai as genai
import toml

try:
    with open(".streamlit/secrets.toml", "r") as f:
        secrets = toml.load(f)
        api_key = secrets.get("GRAMVANI_GEMINI_KEY")
except Exception as e:
    api_key = None
    print(f"Error reading secrets: {e}")

if not api_key:
    print("No API key found.")
else:
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print("AVAILABLE MODELS:")
        for m in models:
            print(f"- {m}")
    except Exception as e:
        print(f"API Error: {e}")
