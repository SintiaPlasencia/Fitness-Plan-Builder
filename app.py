from flask import Flask, request, render_template, jsonify
from transformers import pipeline

app = Flask(__name__)

# Use lightweight model for local demo
generator = pipeline(
    "text-generation",
    model="distilgpt2"
)

def generate_fitness_plan(goal, level, days_per_week, workout_type, session_length, notes=""):
    prompt = f"""
Create a personalized fitness plan.

Goal: {goal}
Experience level: {level}
Workout days per week: {days_per_week}
Preferred workout type: {workout_type}
Session length: {session_length} minutes
Additional notes: {notes}

Include:
1. Summary
2. Weekly Schedule
3. Exercises with sets and reps
4. Tips

Keep it clear, realistic, and organized.
"""

    result = generator(
        prompt,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.7
    )

    return result[0]["generated_text"]

# Route to load the page
@app.route("/")
def home():
    return render_template("index.html")

# API route to handle frontend request
@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json()

    goal = data.get("goal", "")
    level = data.get("level", "")
    days_per_week = data.get("days_per_week", "")
    session_length = data.get("session_length", "")
    workout_type = data.get("workout_type", "")
    notes = data.get("notes", "")

    plan = generate_fitness_plan(
        goal,
        level,
        days_per_week,
        workout_type,
        session_length,
        notes
    )

    return jsonify({"plan": plan})

if __name__ == "__main__":
    app.run(debug=True)