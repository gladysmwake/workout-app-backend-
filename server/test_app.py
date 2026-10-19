from datetime import date
import pytest

from app import create_app
from models import Exercise, Workout, WorkoutExercise, db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# --- Model and Constraint Tests ---

def test_exercise_model_creation(app):
    with app.app_context():
        ex = Exercise(name="Push-ups", category="Strength", equipment_needed=False)
        db.session.add(ex)
        db.session.commit()
        assert ex.id is not None
        assert ex.name == "Push-ups"


def test_exercise_name_validation(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Exercise(name="", category="Strength")


def test_workout_duration_validation(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Workout(date=date(2026, 10, 5), duration_minutes=-10)


def test_workout_exercise_requires_reps_or_duration(app):
    with app.app_context():
        ex = Exercise(name="Plank", category="Core")
        w = Workout(date=date(2026, 10, 5), duration_minutes=30)
        db.session.add_all([ex, w])
        db.session.commit()

        # Both reps and duration are None -> schema validation should reject
        with pytest.raises(Exception):
            link = WorkoutExercise(workout_id=w.id, exercise_id=ex.id, reps=None, duration_seconds=None)
            db.session.add(link)
            db.session.commit()


# --- Workout Endpoint Tests ---

def test_get_workouts_empty(client):
    res = client.get("/workouts")
    assert res.status_code == 200
    assert res.get_json() == []


def test_create_workout(client):
    res = client.post(
        "/workouts",
        json={"date": "2026-10-05", "duration_minutes": 45, "notes": "Leg day"},
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["duration_minutes"] == 45
    assert data["notes"] == "Leg day"
    assert data["id"] is not None


def test_create_workout_validation_error(client):
    res = client.post(
        "/workouts",
        json={"date": "invalid-date", "duration_minutes": -5},
    )
    assert res.status_code == 422
    assert "errors" in res.get_json()


def test_get_workout_with_exercises(client):
    # Create workout
    w_res = client.post(
        "/workouts",
        json={"date": "2026-10-05", "duration_minutes": 60, "notes": "Upper body"},
    )
    w_id = w_res.get_json()["id"]

    # Create exercise
    ex_res = client.post(
        "/exercises",
        json={"name": "Bench Press", "category": "Strength", "equipment_needed": True},
    )
    ex_id = ex_res.get_json()["id"]

    # Link exercise to workout
    client.post(
        f"/workouts/{w_id}/exercises/{ex_id}/workout_exercises",
        json={"reps": 10, "sets": 3},
    )

    # Fetch single workout (stretch goal: includes exercises and reps/sets)
    res = client.get(f"/workouts/{w_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == w_id
    assert len(data["workout_exercises"]) == 1
    assert data["workout_exercises"][0]["reps"] == 10
    assert data["workout_exercises"][0]["exercise"]["name"] == "Bench Press"


def test_get_workout_not_found(client):
    res = client.get("/workouts/9999")
    assert res.status_code == 404


def test_delete_workout_cascades(client):
    w_res = client.post("/workouts", json={"date": "2026-10-05", "duration_minutes": 30})
    w_id = w_res.get_json()["id"]

    ex_res = client.post("/exercises", json={"name": "Squats", "category": "Strength"})
    ex_id = ex_res.get_json()["id"]

    client.post(
        f"/workouts/{w_id}/exercises/{ex_id}/workout_exercises",
        json={"reps": 12, "sets": 4},
    )

    # Delete workout
    del_res = client.delete(f"/workouts/{w_id}")
    assert del_res.status_code == 204

    # Workout is gone
    assert client.get(f"/workouts/{w_id}").status_code == 404

    # Exercise itself remains
    assert client.get(f"/exercises/{ex_id}").status_code == 200


# --- Exercise Endpoint Tests ---

def test_get_exercises_list(client):
    client.post("/exercises", json={"name": "Running", "category": "Cardio"})
    client.post("/exercises", json={"name": "Pull-ups", "category": "Strength"})

    res = client.get("/exercises")
    assert res.status_code == 200
    names = [e["name"] for e in res.get_json()]
    assert "Pull-ups" in names
    assert "Running" in names


def test_create_exercise_duplicate_conflict(client):
    client.post("/exercises", json={"name": "Deadlift", "category": "Strength"})
    res = client.post("/exercises", json={"name": "Deadlift", "category": "Strength"})
    assert res.status_code == 409


def test_create_exercise_blank_name_fails(client):
    res = client.post("/exercises", json={"name": "   ", "category": "Strength"})
    assert res.status_code == 422


def test_get_exercise_detail_with_workouts(client):
    ex_res = client.post("/exercises", json={"name": "Plank", "category": "Core"})
    ex_id = ex_res.get_json()["id"]

    w_res = client.post("/workouts", json={"date": "2026-10-08", "duration_minutes": 20})
    w_id = w_res.get_json()["id"]

    client.post(
        f"/workouts/{w_id}/exercises/{ex_id}/workout_exercises",
        json={"duration_seconds": 60, "sets": 3},
    )

    res = client.get(f"/exercises/{ex_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "Plank"
    assert len(data["workouts"]) == 1
    assert data["workouts"][0]["id"] == w_id


def test_delete_exercise_cascades(client):
    ex_res = client.post("/exercises", json={"name": "Lunges", "category": "Strength"})
    ex_id = ex_res.get_json()["id"]

    del_res = client.delete(f"/exercises/{ex_id}")
    assert del_res.status_code == 204
    assert client.get(f"/exercises/{ex_id}").status_code == 404


# --- WorkoutExercise Join Endpoint Tests ---

def test_add_exercise_to_workout(client):
    w_res = client.post("/workouts", json={"date": "2026-10-10", "duration_minutes": 40})
    w_id = w_res.get_json()["id"]

    ex_res = client.post("/exercises", json={"name": "Dips", "category": "Strength"})
    ex_id = ex_res.get_json()["id"]

    res = client.post(
        f"/workouts/{w_id}/exercises/{ex_id}/workout_exercises",
        json={"reps": 15, "sets": 3},
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["reps"] == 15
    assert data["sets"] == 3
    assert data["exercise"]["name"] == "Dips"


def test_add_exercise_to_workout_missing_reps_and_duration(client):
    w_res = client.post("/workouts", json={"date": "2026-10-10", "duration_minutes": 40})
    w_id = w_res.get_json()["id"]

    ex_res = client.post("/exercises", json={"name": "Burpees", "category": "Cardio"})
    ex_id = ex_res.get_json()["id"]

    res = client.post(
        f"/workouts/{w_id}/exercises/{ex_id}/workout_exercises",
        json={"sets": 3},  # missing both reps and duration_seconds
    )
    assert res.status_code == 422


def test_add_duplicate_exercise_to_workout_conflict(client):
    w_res = client.post("/workouts", json={"date": "2026-10-10", "duration_minutes": 40})
    w_id = w_res.get_json()["id"]

    ex_res = client.post("/exercises", json={"name": "Crunches", "category": "Core"})
    ex_id = ex_res.get_json()["id"]

    client.post(
        f"/workouts/{w_id}/exercises/{ex_id}/workout_exercises",
        json={"reps": 20, "sets": 3},
    )
    # Adding same exercise to same workout again
    res = client.post(
        f"/workouts/{w_id}/exercises/{ex_id}/workout_exercises",
        json={"reps": 15, "sets": 2},
    )
    assert res.status_code == 409
