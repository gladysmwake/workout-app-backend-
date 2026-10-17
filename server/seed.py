#!/usr/bin/env python3
"""Seed file to populate the database with realistic starter workouts and exercises."""
from datetime import date

from app import app
from models import Exercise, Workout, WorkoutExercise, db

EXERCISES = [
    {"name": "Push-ups", "category": "Strength", "equipment_needed": False},
    {"name": "Squats", "category": "Strength", "equipment_needed": False},
    {"name": "Bench Press", "category": "Strength", "equipment_needed": True},
    {"name": "Deadlift", "category": "Strength", "equipment_needed": True},
    {"name": "Running", "category": "Cardio", "equipment_needed": False},
    {"name": "Jump Rope", "category": "Cardio", "equipment_needed": True},
    {"name": "Plank", "category": "Core", "equipment_needed": False},
]

WORKOUTS = [
    {"date": date(2026, 10, 5), "duration_minutes": 45, "notes": "Full body strength session"},
    {"date": date(2026, 10, 7), "duration_minutes": 30, "notes": "Morning cardio intervals"},
    {"date": date(2026, 10, 9), "duration_minutes": 55, "notes": "Upper body and core focus"},
    {"date": date(2026, 10, 12), "duration_minutes": 50, "notes": "Leg day and conditioning"},
]

# (workout_index, exercise_name, reps, sets, duration_seconds)
WORKOUT_LINKS = [
    (0, "Push-ups", 15, 3, None),
    (0, "Squats", 12, 4, None),
    (0, "Plank", None, 3, 60),
    (1, "Running", None, 1, 1200),
    (1, "Jump Rope", None, 5, 180),
    (2, "Bench Press", 8, 4, None),
    (2, "Push-ups", 20, 3, None),
    (2, "Plank", None, 3, 45),
    (3, "Squats", 10, 5, None),
    (3, "Deadlift", 5, 5, None),
]


def seed():
    with app.app_context():
        print("Clearing old data...")
        WorkoutExercise.query.delete()
        Workout.query.delete()
        Exercise.query.delete()
        db.session.commit()

        print("Seeding exercises...")
        exercise_objs = {}
        for ex_data in EXERCISES:
            exercise = Exercise(**ex_data)
            db.session.add(exercise)
            exercise_objs[ex_data["name"]] = exercise
        db.session.commit()

        print("Seeding workouts...")
        workout_objs = []
        for w_data in WORKOUTS:
            workout = Workout(**w_data)
            db.session.add(workout)
            workout_objs.append(workout)
        db.session.commit()

        print("Linking exercises to workouts...")
        for w_idx, ex_name, reps, sets, duration in WORKOUT_LINKS:
            link = WorkoutExercise(
                workout=workout_objs[w_idx],
                exercise=exercise_objs[ex_name],
                reps=reps,
                sets=sets,
                duration_seconds=duration,
            )
            db.session.add(link)
        db.session.commit()

        print(
            f"Successfully seeded {len(exercise_objs)} exercises, "
            f"{len(workout_objs)} workouts, and {len(WORKOUT_LINKS)} workout-exercise links!"
        )


if __name__ == "__main__":
    seed()
