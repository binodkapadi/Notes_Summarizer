## Deployment Link

url = https://binodkapadi-notessummarizer.streamlit.app/

       https://binodkapadi-notessummarizer.streamlit.app/


## NotesSummarizer
The Note Summarizer processes long pasted notes and uploaded files, including PDF, DOCX, PPT, images (JPEG/PNG), and more, converting them into clear and human-friendly notes. It analyzes the entire document thoroughly and produces well-structured, easy-to-read summaries with proper spacing, alignment, and topic-wise clarity. The tool supports multiple formats and ensures that all extracted content is presented in a simple, understandable, and organized manner.


## Problem Statement
Students, professionals, and learners often deal with lengthy notes, PDFs, documents, and presentations that are difficult to read, revise, and organize. Manually summarizing large amounts of information is time-consuming and overwhelming, making it harder to prepare well-structured study material.


## Solution Summary
The Note Summarizer is an AI-powered tool that converts long pasted notes and uploaded files (PDF, DOCX, PPT, JPEG, PNG, etc.) into clean, human-friendly summaries. It analyzes the entire document and generates clear, well-organized, topic-wise notes with proper spacing and alignment to make revision easier, faster, and more effective.

## Tech Stack

    - Backend: Python, Streamlit
    - Frontend: Streamlit Components, Custom CSS
    - AI / LLM Models: Google Gemini 2.0 Flash (google-generativeai SDK)
    - Deployment / Hosting: Streamlit Cloud
    - Version Control: Git and GitHub

## Project Structure
QUIZGENERATOR

    - mainapp.py                               # Main Streamlit application
    - style.css                                # Custom UI styling (Dark Mode)
    - .env                                     # Environment variables (contains GEMINI_API_KEY)
    - requirements.txt                         # Project dependencies
    - README.md                                # Project documentation
    - .gitignore                               # For hiding api key ( or other sensitive
    information)
    -  venv/                                   # Virtual environment directory 



## Setup Instructions (with Python)

1. Create and Activate a Virtual Environment
   
       python -m venv venv
       venv\Scripts\activate

3. Install Dependencies
   
       pip install -r requirements.txt

5. Set Up Environment Variables
   
       GEMINI_API_KEY=your_google_gemini_api_key_here
   
7. Run the Streamlit App
   
       streamlit run mainapp.py

   By default, the app runs on:
   
        http://localhost:8501

  
11. To stop the Streamlit App
    
        ctrl + c

13. Deactivate the Virtual Environment (After Use)
    
        deactivate


## Deployment
   -Activate the virtual environment
   
        venv\Scripts\activate
   
   - Run the Streamlit App
     
         streamlit run mainapp.py

   By default, the app runs on:
   
        http://localhost:8501
        
## Features
- Summarizes long notes, PDFs, DOCX, PPTs, and images into clear, human-friendly study material.
- Automatically organizes content into topic-wise sections with proper spacing and alignment.
- Supports multiple file formats including PDF, DOCX, PPT, JPG, PNG, and pasted text.
- Clean and intuitive UI for fast document uploading and instant summary generation.
- Useful for students, teachers, and professionals who need quick, readable summaries.


## Technical Architecture
The system allows users to upload files (PDF, DOCX, PPT, images) or paste long notes, then processes the content using the Google Gemini API to generate structured, easy-to-read summaries with topic-wise formatting.

     ASCII Architecture Diagram:
     
         Frontend (Streamlit UI)  
                  ↓  User uploads file / pastes notes  
         Backend (Python + Google GenAI)  
                  ↓  
         Google Gemini API  
                  ↓  
         Generates structured summary text  
                  ↓  
         Backend formats into clean readable notes  
                  ↓  
         Frontend displays human-friendly summarized notes



## References

    Streamlit Documentation
    Google Generative AI SDK
    python-dotenv


## Acknowledgements
 - Developed by Binod Kapadi (12201221)
 - Special thanks to Google Gemini for enabling AI-powered document analysis and summarization.