import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
# We only need `torch` installed, no need to import it explicitly
# import torch 

st.title("DesignGPT")
st.write("Your AI design assistant")

# 1. Use st.cache_resource to load the model only once
# This is crucial for performance and preventing the blank screen
@st.cache_resource
def load_model_and_tokenizer():
    # Load a pre-trained model (GPT-2 is a good free start)
    model_name = "gpt2"
    
    # Use a loading message while it's loading the first time
    with st.spinner(f"Loading AI Model: {model_name}... (This might take a minute the first time!)"):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

# Call the function to get the cached model and tokenizer
tokenizer, model = load_model_and_tokenizer()

# Input prompt from user
prompt = st.text_input("Enter your design idea:")

if prompt:
    # 2. Add a loading spinner while the model is generating text
    with st.spinner("AI is generating design idea..."):
        try:
            inputs = tokenizer(prompt, return_tensors="pt")
            
            # Generate the text
            outputs = model.generate(
                **inputs, 
                max_length=150, # Increased length for better results
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id # Important for GPT-2 generation
            )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            st.subheader("Generated Design Idea:")
            st.code(generated_text) # Display as code for better structure
            
        except Exception as e:
            st.error(f"An error occurred during generation: {e}")