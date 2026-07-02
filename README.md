# NotesSummarizer

The Note Summarizer processes long pasted notes,any prompt and uploaded files, including text-based PDF, DOCX, PPT and images (JPEG/PNG) converting them into clear and human-friendly notes. It analyzes the entire document thoroughly and produces well-structured, easy-to-read summaries with proper spacing, alignment, and topic-wise clarity. Supports both printed and handwritten documents. For the best results, use clear, high-quality scans or images. Accuracy may vary for unclear or difficult-to-read handwriting. All extracted information is presented in a simple, understandable, and organized format for easy revision.

# Deployment Link

Deployment (Streamlit) = https://binodkapadi-notessummarizer.streamlit.app/

# PROJECT SETUP

pip = Python Package Installer

venv = Python Virtual Environment

### Step 1: Install Required Software

#### A) Install Python

Download and install Python:

Official Website: https://www.python.org/downloads/

During installation:

    Check the option "Add Python to PATH"
    Click Install Now

Verify installation [Open Command Prompt in Windows]:

     python --version

#### B) Install Visual Studio Code (Recommended)

Download and install Visual Studio Code:

Official Website: https://code.visualstudio.com

Recommended Extensions:

     Python
     Pylance
     Streamlit

### Step 2: Setup Folder Structure

Open VS Code Terminal and create a new folder:

     mkdir NotesSummarizer
     cd NotesSummarizer
     python -m venv venv
     venv\Scripts\activate

First of all, inside the folder create:

* .env
* requirements.txt

#### Install Dependencies

First put all required dependencies inside requirements.txt file and then run:

    pip install -r requirements.txt

#### Configure Environment Variables (.env)

    GEMINI_API_KEY=your_gemini_api_key

Get Gemini API Key from: https://aistudio.google.com/app/apikey


### Step 3: Run the Streamlit Application

#### Run the application:

     streamlit run mainapp.py

By default, the app runs on:

     http://localhost:8501

#### STOP APPLICATION

To stop the Streamlit server:

     CTRL + C

#### DEACTIVATE VIRTUAL ENVIRONMENT

After completing your work:

     deactivate

## Problem Statement

Students, professionals, and learners often deal with lengthy notes, PDFs, documents, and presentations that are difficult to read, revise, and organize. Manually summarizing large amounts of information is time-consuming and overwhelming, making it harder to prepare well-structured study material.

## Solution Summary

The Note Summarizer is an AI-powered tool that converts long pasted notes and uploaded files (PDF, DOCX, PPT, JPEG, PNG, etc.) into clean, human-friendly summaries. It analyzes the entire document and generates clear, well-organized, topic-wise notes with proper spacing and alignment to make revision easier, faster, and more effective.

## Tech Stack

    - Backend: Python, Streamlit
    - Frontend: Streamlit Components, Custom CSS
    - AI / LLM Models: Google Gemini 2.0 Flash (google-genai SDK)
    - Deployment / Hosting: Streamlit Cloud
    - Version Control: Git and GitHub

## Project Structure

NOTESSUMMARIZER

    - mainapp.py                               # Main Streamlit application
    - style.css                                # Custom UI styling (Dark Mode)
    - .env                                     # Environment variables (contains GEMINI_API_KEY)
    - requirements.txt                         # Project dependencies
    - README.md                                # Project documentation
    - .gitignore                               # For hiding api key ( or other sensitive information)
    - venv/                                    # Virtual environment directory 

## Features

* Summarizes long notes, PDFs, DOCX, PPTs, and images into clear, human-friendly study material.
* Automatically organizes content into topic-wise sections with proper spacing and alignment.
* Supports multiple file formats including PDF, DOCX, PPT, JPG, PNG, and pasted text.
* Clean and intuitive UI for fast document uploading and instant summary generation.
* Generates readable and structured summaries for easy revision and understanding.
* Useful for students, teachers, researchers, and professionals.
* Human-friendly formatting with clean spacing and organized output.
* AI-powered summarization using Google Gemini API.

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
       PyPDF2 Documentation
       python-docx Documentation
       python-pptx Documentation

## Acknowledgements

* Developed by Binod Kapadi
* Special thanks to Google Gemini for enabling AI-powered document analysis and summarization.