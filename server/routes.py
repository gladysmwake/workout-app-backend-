from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db
from schemas import (
    exercise_detail_schema,
    exercise_schema,
    exercises_schema,
    workout_detail_schema,
    workout_exercise_detail_schema,
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

api = Blueprint("api", __name__)


def get_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")
    return data


# --- Workouts Endpoints ---

@api.get("/workouts")
def get_workouts():
    workouts = db.session.scalars(
        db.select(Workout).order_by(Workout.date.desc(), Workout.id.desc())
    ).all()
    return jsonify(workouts_schema.dump(workouts)), 200


@api.get("/workouts/<int:id>")
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return jsonify({"error": f"Workout {id} not found."}), 404
    return jsonify(workout_detail_schema.dump(workout)), 200


@api.post("/workouts")
def create_workout():
    data = workout_schema.load(get_json())
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@api.delete("/workouts/<int:id>")
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return jsonify({"error": f"Workout {id} not found."}), 404
    db.session.delete(workout)
    db.session.commit()
    return "", 204


# --- Exercises Endpoints ---

@api.get("/exercises")
def get_exercises():
    exercises = db.session.scalars(
        db.select(Exercise).order_by(Exercise.name)
    ).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@api.get("/exercises/<int:id>")
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return jsonify({"error": f"Exercise {id} not found."}), 404
    return jsonify(exercise_detail_schema.dump(exercise)), 200


@api.post("/exercises")
def create_exercise():
    data = exercise_schema.load(get_json())
    exercise = Exercise(**data)
    db.session.add(exercise)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Exercise with name '{data['name']}' already exists."}), 409
    return jsonify(exercise_schema.dump(exercise)), 201


@api.delete("/exercises/<int:id>")
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return jsonify({"error": f"Exercise {id} not found."}), 404
    db.session.delete(exercise)
    db.session.commit()
    return "", 204


# --- WorkoutExercise Join Endpoint ---

@api.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return jsonify({"error": f"Workout {workout_id} not found."}), 404

    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return jsonify({"error": f"Exercise {exercise_id} not found."}), 404

    data = workout_exercise_schema.load(get_json())
    link = WorkoutExercise(
        workout_id=workout.id,
        exercise_id=exercise.id,
        **data,
    )
    db.session.add(link)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "This exercise is already added to this workout."}), 409

    return jsonify(workout_exercise_detail_schema.dump(link)), 201
