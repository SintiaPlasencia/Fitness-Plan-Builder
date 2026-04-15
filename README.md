## Fitness Plan Builder

# Description

The Fitness Plan Builder is an AI-powered web application that generates personalized fitness plans based on user input. Users can enter their fitness goals, experience level, workout schedule, and preferences, and the system generates a customized workout routine.

This project aims to help users stay consistent, motivated, and achieve their health goals through tailored fitness guidance.



# Features
	•	Personalized fitness plan generation using AI
	•	User-friendly web interface for input
	•	User inputs include:
	•	Fitness goal (weight loss, muscle gain, endurance)
	•	Experience level (beginner, intermediate, advanced)
	•	Workout days per week
	•	Session length
	•	Preferred workout type (gym, home, running, etc.)
	•	Additional notes (optional)
	•	AI-generated output includes:
	•	Summary of plan
	•	Weekly workout schedule
	•	Exercises with sets and repetitions
	•	Tips for improvement



# Tech Stack
	•	Python (Flask backend)
	•	Hugging Face Transformers (LLM integration)
	•	HTML + Tailwind CSS (Frontend UI)
	•	Google Colab (model experimentation)



# Team Members
	•	Sintia Plasencia Diaz (Team Lead)
Responsibilities: Prompt engineering, backend development (app.py), AI integration, testing
	•	Lasiru Lochana Weerasuriya (Frontend Developer)
Responsibilities: UI design, input form, results display, frontend-backend connection


# Current Progress
	•	✅ Project proposal completed
	•	✅ Repository created and organized
	•	✅ Virtual environment set up and dependencies installed
	•	✅ AI fitness plan generator tested in Google Colab
	•	✅ Flask backend (app.py) created
	•	✅ Frontend UI built using HTML + Tailwind CSS
	•	✅ Frontend connected to backend API
	•	✅ Working prototype that generates fitness plans from user input

# Note:
The current model output may be repetitive or not fully structured because we are using a lightweight local model. This will be improved in the next phase by integrating a more advanced LLM (such as Llama) and refining the prompt for better formatting and quality.


# Next Steps
	•	Improve AI output quality through better prompt engineering
	•	Integrate a more advanced LLM (Llama)
	•	Improve UI/UX and formatting of results
	•	Add input validation and error handling
	•	Conduct user testing
	•	Prepare final demo and presentation



# Demo
	•	Colab Notebook:
https://colab.research.google.com/drive/19_Ta7TMxgIITsovs1mTL7TqvEvd3XFJh?usp=sharing
	•	GitHub Repository:
https://github.com/SintiaPlasencia/Fitness-Plan-Builder



# How to Run the App
	1.	Download or clone the project from GitHub
	2.	Open the project folder in your code editor (such as VS Code)
	3.	Make sure Python and required libraries (Flask, transformers, torch) are installed
	4.	Run the app.py file
	5.	Open your browser and go to http://127.0.0.1:5000
	6.	Enter your fitness information in the form
	7.	Click “Generate My Plan” to see your personalized workout plan


# How It Works
	1.	The user enters fitness details in the web interface
	2.	The frontend sends the data to the Flask backend
	3.	The backend sends a prompt to the AI model
	4.	The AI generates a fitness plan
	5.	The result is displayed back on the webpage


# Expected Outcome

A working AI-powered web application that generates structured, personalized fitness plans and demonstrates the use of Generative AI with a full frontend-backend system.
