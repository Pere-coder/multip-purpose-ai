import requests
import json
import fitz  # PyMuPDF
import streamlit as st
import os
import pyttsx3
import time



class ChatAgent:
    def __init__(self, model='deepseek-r1:latest'):
        self.model = model
        self.history = []  # Store conversation history
        self.engine = pyttsx3.init()


    def query(self, prompt):
        url = 'http://localhost:11434/api/generate'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': True
        }

        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            if response.status_code == 100:
                response_text = ''
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            response_text += data['response']
                return response_text
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None

    def extract_text_from_pdf(self, pdf_file):
        """
        Extract text from a PDF file.
        """
        text = ""
        try:
            doc = fitz.open(pdf_file)
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text()
        except Exception as e:
            return f"Error extracting text from PDF: {e}"
        
        return text

    def summarize_pdf(self, pdf_file):
        """
        Handle PDF upload and summarize the content using the AI model.
        """
        # Step 1: Extract text from the PDF
        pdf_text = self.extract_text_from_pdf(pdf_file)
        
        if pdf_text.startswith("Error"):
            return pdf_text
        
        
        max_length = 2000
        if len(pdf_text) > max_length:
            pdf_text = pdf_text[:max_length] 

        prompt = f"Summarize the following text:\n\n{pdf_text}"
        

        # Step 3: Get the AI response
        summary = self.query(prompt)
        
        return summary
    
    def speak_text(self, text):
        """
        Convert text to speech and play it.
        """
        
        self.engine.say(text)
        self.engine.runAndWait()
        # Wait for the speech to finish
   

def main():
    # Initialize the Streamlit app interface
    st.title("PDF Summarization Agent")
    
    agent = ChatAgent()

    # File uploader widget
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    
    if uploaded_file is not None:
        # Show progress or status
        with st.spinner("Processing PDF..."):
            # Save uploaded file temporarily
            with open("temp_uploaded_pdf.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Get the summary of the PDF
            summary = agent.summarize_pdf("temp_uploaded_pdf.pdf")
            
            # Display the summary
            st.subheader("Summarized Content:")
            st.write(summary)
            # Option to read the summary aloud
            if st.button("Read Summary Aloud"):
                agent.speak_text(summary)
                st.success("Reading the summary aloud...")
    
    else:
        st.write("Please upload a PDF file to get started.")

if __name__ == "__main__":
    main()
