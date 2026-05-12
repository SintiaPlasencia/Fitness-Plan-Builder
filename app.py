from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

def generate_fitness_plan(goal, level, days_per_week, workout_type, session_length, notes=""):
    if not goal:
        goal = "General Health"

    if not level:
        level = "Beginner"

    if not days_per_week:
        days_per_week = "3"

    if not workout_type:
        workout_type = "gym"

    if not session_length:
        session_length = "45"

    if not notes:
        notes = "none"

    plan = f"""
1. Summary
This is a {days_per_week}-day {workout_type} fitness plan for a {level} user whose goal is {goal}. Each workout is designed to last about {session_length} minutes and includes strength training, cardio, and recovery.

2. Weekly Schedule

Day 1: Full Body Strength
- Squats: 3 sets of 10 reps
- Dumbbell Chest Press: 3 sets of 10 reps
- Lat Pulldown: 3 sets of 10 reps
- Plank: 3 sets of 30 seconds
- Light cardio: 10 minutes

Day 2: Cardio + Core
- Treadmill walk or jog: 20 minutes
- Bicycle crunches: 3 sets of 15 reps
- Leg raises: 3 sets of 12 reps
- Russian twists: 3 sets of 15 reps

Day 3: Lower Body + Conditioning
- Lunges: 3 sets of 10 reps each leg
- Leg Press: 3 sets of 10 reps
- Glute Bridges: 3 sets of 12 reps
- Stair climber or bike: 15 minutes

3. Tips
- Start with a 5-minute warm-up before each workout.
- Rest 60–90 seconds between sets.
- Drink water and focus on good form.
- Increase weight slowly as you get stronger.
- Stay consistent and adjust the plan as needed.

Additional Notes: {notes}
"""
    return plan


@app.route("/")
def home():
    return render_template("index.html")


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