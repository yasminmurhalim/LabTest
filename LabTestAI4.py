import streamlit as st
import nltk
from nltk.tokenize import sent_tokenize
from PyPDF2 import PdfReader

# configuration 
st.set_page_config(page_title="PDF Text Chunking (Q4)", layout="wide")

# Ensure the NLTK 'punkt' tokenizer is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

st.title("PDF Semantic Text Chunking")

# file upload
uploaded_file = st.file_uploader("Upload your PDF file ", type="pdf")

if uploaded_file:

    reader = PdfReader(uploaded_file)
    full_text = ""
    
    with st.spinner("Extracting text from PDF..."):
        for page in reader.pages:
       
            text = page.extract_text()
            if text:
                full_text += text + " "
    
    st.success("Text extracted successfully!")
   
    sentences = sent_tokenize(full_text)
    
    # Display 
    st.info(f"Total Sentences Found: {len(sentences)}")

    # 
    st.subheader("Extracted Text Sample ")
 
    start_index = 58
    end_index = 69 
    
    if len(sentences) >= end_index:
        target_chunk = sentences[start_index:end_index]
        
        # Display as a clean list
        for i, sentence in enumerate(target_chunk):
          
            actual_idx = start_index + i
            st.markdown(f"**Sentence {actual_idx}:**")
            st.write(f"> {sentence}")
            st.markdown("---")
            
     
        with st.expander("View Raw List Format"):
            st.code(target_chunk)
    else:
        st.warning(f"The document is too short! It only has {len(sentences)} sentences. Please upload a longer document like the Z-TOPSIS paper.")

else:
    st.info("Please upload the 'Z-TOPSIS' PDF file to see the results.")