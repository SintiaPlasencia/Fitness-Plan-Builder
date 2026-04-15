from flask import Flask, request, render_template
from transformers import pipeline

app = Flask(__name__)

generator = pipeline(
    "text-generation",
    model="meta-llama/Llama-3.2-3B-Instruct",
    device_map="auto"
)

def generate_fitness_plan(goal, level, days, workout, length):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful fitness coach. Create clear, realistic, structured fitness plans."
        },
        {
            "role": "user",
            "content": f"""
Create a personalized fitness plan.

Goal: {goal}
Experience level: {level}
Workout days per week: {days}
Preferred workout type: {workout}
Session length: {length}

Format:
1. Summary
2. Weekly Schedule
3. Exercises with sets and reps
4. Tips

Keep it concise and organized.
"""
        }
    ]

    result = generator(
        messages,
        max_new_tokens=300,
        do_sample=True,
        temperature=0.7,
    )

    return result[0]["generated_text"][-1]["content"]

@app.route("/", methods=["GET", "POST"])
def home():
    plan = ""
    if request.method == "POST":
        goal = request.form["goal"]
        level = request.form["level"]
        days = request.form["days"]
        workout = request.form["workout"]
        length = request.form["length"]
        plan = generate_fitness_plan(goal, level, days, workout, length)

    return render_template("index.html", plan=plan)

if __name__ == "__main__":
    app.run(debug=True)