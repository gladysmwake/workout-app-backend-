# Workout Application Backend

A Flask REST API for tracking workouts and reusable exercises used by personal trainers. Workouts include sets, reps, or duration for each exercise performed. Built with Flask, Flask-SQLAlchemy, Flask-Migrate, and Marshmallow.

---

## Features

- **Workout Tracking**: Create, view, and delete workouts with date, duration in minutes, and optional notes.
- **Reusable Exercise Catalogue**: Create, view, and delete exercises (name, category, equipment flag). Exercises can be reused across any number of workouts.
- **Many-to-Many Association**: Join entity `WorkoutExercise` links workouts to exercises with tracked sets, reps, or duration in seconds.
- **Multi-Level Validation**:
  - **Table Constraints**: SQL-level CheckConstraints (`name_not_blank`, `duration_positive`, `reps_or_duration_required`) and UniqueConstraints.
  - **Model Validations**: SQLAlchemy `@validates` hooks ensuring clean strings, positive integers, and valid dates.
  - **Schema Validations**: Marshmallow schemas enforcing bounds, non-blank strings, and relationship serialization.
- **Seed Data**: Pre-populated database with 7 common exercises, 4 realistic workouts, and 10 workout-exercise records.

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- [Pipenv](https://pipenv.pypa.io/)
- Git

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd workout-app-backend-
   ```

2. **Install dependencies:**
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Set up the database & seed data:**
   ```bash
   cd server
   flask db upgrade head
   python seed.py
   ```

---

## Running the Application

From the `server/` directory:

```bash
flask run -p 5555
```

The API will be live at `http://127.0.0.1:5555`.

---

## Running the Tests

To run the automated pytest suite:

```bash
cd server
pytest -v
```

All 18 automated tests cover:
- Model instantiation and validation hooks
- Table-level constraints
- Schema validations and serialization
- All 9 CRUD and association endpoints (success, validation, and error states)
- Cascade deletion of join records

---

## API Endpoints

All request and response bodies use JSON. Dates follow the `YYYY-MM-DD` format.

### Workouts

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `GET` | `/workouts` | List all workouts | `200 OK` |
| `GET` | `/workouts/<id>` | Show a single workout with associated exercises, reps, sets, and duration | `200 OK` |
| `POST` | `/workouts` | Create a new workout session | `201 Created` |
| `DELETE` | `/workouts/<id>` | Delete a workout (cascade-deletes associated workout-exercises) | `204 No Content` |

#### `POST /workouts` Request Body:
```json
{
  "date": "2026-10-05",
  "duration_minutes": 45,
  "notes": "Leg day and conditioning"
}
```

---

### Exercises

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `GET` | `/exercises` | List all exercises alphabetically | `200 OK` |
| `GET` | `/exercises/<id>` | Show an exercise and all workouts it appears in | `200 OK` |
| `POST` | `/exercises` | Create a reusable exercise | `201 Created` |
| `DELETE` | `/exercises/<id>` | Delete an exercise (cascade-deletes associated workout-exercises) | `204 No Content` |

#### `POST /exercises` Request Body:
```json
{
  "name": "Squats",
  "category": "Strength",
  "equipment_needed": false
}
```

---

### Workout-Exercise Association

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `POST` | `/workouts/<w_id>/exercises/<e_id>/workout_exercises` | Add an exercise to a workout with reps, sets, or duration | `201 Created` |

#### Request Body (Reps & Sets):
```json
{
  "reps": 12,
  "sets": 4
}
```

#### Request Body (Duration & Sets):
```json
{
  "duration_seconds": 60,
  "sets": 3
}
```

---

## Project Structure

```
workout-app-backend-/
├── Pipfile                 # Project dependencies
├── Pipfile.lock            # Pinned dependency lockfile
├── README.md               # Project documentation and instructions
└── server/
    ├── app.py              # Application entry point, factory & error handlers
    ├── models.py           # Exercise, Workout, WorkoutExercise models & constraints
    ├── schemas.py          # Marshmallow serialization & validation schemas
    ├── routes.py           # Blueprint with all 9 REST endpoints
    ├── seed.py             # Starter database population script
    ├── test_app.py         # 18 automated tests for endpoints and validations
    ├── pytest.ini          # Pytest runner configuration
    └── migrations/         # Alembic database migration versions
```

---

## Git Workflow

Development was tracked across dedicated feature branches, merged into `main` via Pull Requests, with branches cleanly managed:
- `feature/models-and-migrations`: Data models, table constraints, and Alembic migrations.
- `feature/schemas-and-validations`: Marshmallow schemas and validation rules.
- `feature/routes`: REST endpoints for Workouts, Exercises, and WorkoutExercises.
- `feature/seed-and-tests`: Seeder script and automated test suite.
- `feature/docs`: Project documentation and API specifications.
