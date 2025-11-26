## Deployment Link

url = https://kapadibinod-quizgenerator077.streamlit.app/

         https://kapadibinod-quizgenerator077.streamlit.app/


## notes-to-quiz-generator-binod-kapadi-12201221
Quiz Generator automatically converts any set of notes or prompt into interactive quiz questions (MCQs) using AI.


## Project Overview
Convert your class notes or text into interactive quizzes using AI.


## Problem Statement
Students often take detailed notes but struggle to revise them effectively.
Manually creating quizzes from notes is time-consuming, making it hard to practice and retain knowledge efficiently.


## Solution Summary
The Notes-to-Quiz Generator is an AI-driven web application that transforms written notes into interactive quizzes for effective self-assessment.
Users can paste their notes, choose a quiz difficulty level, and instantly generate AI-created questions with correct answers.


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
    - .gitignore                               # For hiding api key ( or other sensitive information)
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
   
9. Generate a Quiz
    
       - Paste any text or notes into the textarea
       - Select quiz difficulty level (Easy / Medium / Hard)
       - Click “🚀 Generate Quiz”
       - Attempt questions and click “Submit” to view your score
  
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
- Converts text notes into interactive quizzes automatically.
- Generates multiple-choice, True/False, and short-answer questions.
- Clean, intuitive UI with real-time quiz generation.
- Real-world applicability for students, educators, and self-learners.


## Technical Architecture
The system allows users to paste notes or text, sends the content to the Google Gemini API, and automatically generates multiple-choice quiz questions (MCQs) that are displayed interactively in the Streamlit interface.

   - ASCII Architecture Diagram:
     
         Frontend (Streamlit UI)   ->    User pastes notes or text   ->    Backend (Python + Google GenAI)    ->    Google Gemini API    ->     Generates MCQs in JSON format     ->     Backend processes questions       ->      Frontend displays interactive quiz


## References

    Streamlit Documentation
    Google Generative AI SDK
    python-dotenv


## License
This project is licensed under the MIT License.


## Acknowledgements
 - Developed by Binod Kapadi (12201221)
 - Special thanks to Google Gemini for powering AI question generation.
