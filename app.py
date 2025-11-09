import streamlit as st
import json
import streamlit.components.v1 as components 
import re 
import requests # <--- NEW: For robust API calls
# Imports the function from the generator file we created
from src.generator.layout_generator import generate_html_ui

# --- Global Configuration ---
st.title("🧠 DesignGPT (Ollama + Mistral)")
st.write("Your AI design assistant running the smart Mistral 7B model!")

MODEL_NAME = "designgpt-mistral"
OLLAMA_API_URL = "http://localhost:11434/api/generate" # Default Ollama endpoint

# --- Function 1: Cleanup and Parsing (Robust JSON Extraction) ---
def extract_and_parse_json(generated_text):
    """Safely extracts and cleans a JSON dictionary from a text string."""
    
    if isinstance(generated_text, dict):
        return generated_text

    # 1. Extraction: Find the main JSON block { ... }
    json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
    
    if json_match:
        json_string = json_match.group(0).strip()
        
        # --- CLEANUP STEPS ---
        # 1. Fix Single Quotes (Most Common LLM Error)
        json_string = json_string.replace("'", '"')
        
        # 2. Remove Trailing Commas (Major JSONDecodeError Cause)
        json_string = re.sub(r',\s*([\]\}])', r'\1', json_string)
        
        # 3. Remove JavaScript/C-style Comments (If AI adds them)
        json_string = re.sub(r'//.*?\n|/\*.*?\*/', '', json_string, flags=re.DOTALL)

        # 2. Parsing: Attempt to parse the cleaned string
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            st.error(f"AI output contained a JSON-like structure, but it was invalid even after cleanup. Error: {e}")
            st.code(json_string)
            return None
    
    return None

# --- Function 2: Direct Ollama API Call (Robust Connection) ---
def call_ollama_api(prompt, model_name, api_url):
    """
    Calls the Ollama API directly using requests for better error control.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.5,
            "num_predict": 700,
            "stop": ["\n\n", "User", "USER"]
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        
        # This raises an exception for 4xx or 5xx status codes (model not found, server error)
        response.raise_for_status()
        
        # If successful, return the raw response text
        return response.json().get('response', '')

    except requests.exceptions.ConnectionError:
        # Catches "Connection Refused" cleanly
        raise ConnectionError("Ollama service not found. Make sure it's running.")
    
    except requests.exceptions.RequestException as e:
        # Catches HTTP errors, timeouts, and unexpected response codes
        status_code = response.status_code if 'response' in locals() else 'N/A'
        raise Exception(f"Ollama API request failed (Status: {status_code}). Details: {e}")


# --- Streamlit Execution Flow ---
user_input = st.text_input("Describe the UI you want:")

if st.button("Generate Design Spec"):
    if user_input:
        
        # Define the strict System Role
        system_role = """
        You are an expert UI/UX designer bot named DesignGPT.
        Your ONLY job is to take the user's design request and convert it into a single, valid JSON object.
        START your response with the JSON object and DO NOT include any text after the closing curly brace (}).
        The JSON MUST contain these keys: "style", "page_type", "elements" (list), "color_palette" (list of 3 HEX codes), "fonts", and "rationale".
        """

        user_request = f"Based on this brief, generate the design specification in JSON format: {user_input}"
        final_prompt = f"{system_role}\n\nUSER BRIEF: {user_request}"
        
        with st.spinner("Mistral is thinking and structuring the design spec..."):
            try:
                # 1. Call the robust API function to get raw text
                raw_generated_text = call_ollama_api(final_prompt, MODEL_NAME, OLLAMA_API_URL)
                
                # 2. Cleanup and Parse the raw text
                design_spec = extract_and_parse_json(raw_generated_text)
                
                if design_spec:
                    # SUCCESS: design_spec is a clean dict
                    st.subheader("✅ Clean Design Specification (The Recipe):")
                    st.json(design_spec)

                    # 3. Generate HTML: Pass the clean Python DICTIONARY
                    html_content = generate_html_ui(design_spec)

                    st.subheader("🖥️ UI Preview:")
                    components.html(html_content, height=600, scrolling=True)
                
                else:
                    # FAILURE: No valid JSON was extracted (Error handled inside the function)
                    st.warning("Mistral produced text, but no valid JSON specification could be found or parsed.")
                    st.code(raw_generated_text)

            # 4. Catch exceptions raised by call_ollama_api
            except (ConnectionError, Exception) as e:
                st.error(f"Error communicating with Ollama: {str(e)}")
                st.warning("Make sure the **Ollama service is running** in the background!")