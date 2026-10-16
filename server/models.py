import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()

MAX_NAME_LEN = 100
MAX_CATEGORY_LEN = 50
MAX_DURATION = 24 * 60


def clean_text(label, value, max_len):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    cleaned = value.strip()
    if len(cleaned) > max_len:
        raise ValueError(f"{label} must be at most {max_len} characters.")
    return cleaned


def positive_int(label, value, maximum=None):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer.")
    if value < 1:
        raise ValueError(f"{label} must be at least 1.")
    if maximum and value > maximum:
        raise ValueError(f"{label} must be at most {maximum}.")
    return value


class Exercise(db.Model):
    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="exercise_name_not_blank"),
        CheckConstraint("length(trim(category)) > 0", name="exercise_category_not_blank"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_NAME_LEN), nullable=False, unique=True)
    category = db.Column(db.String(MAX_CATEGORY_LEN), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    workouts = association_proxy("workout_exercises", "workout")

    @validates("name")
    def validate_name(self, key, value):
        return clean_text("Exercise name", value, MAX_NAME_LEN)

    @validates("category")
    def validate_category(self, key, value):
        return clean_text("Exercise category", value, MAX_CATEGORY_LEN)

    @validates("equipment_needed")
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be true or false.")
        return value

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"


class Workout(db.Model):
    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="workout_duration_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Relationships
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    exercises = association_proxy("workout_exercises", "exercise")

    @validates("date")
    def validate_date(self, key, value):
        if isinstance(value, datetime.datetime) or not isinstance(value, datetime.date):
            raise ValueError("Workout date must be a valid date.")
        return value

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        if value is None:
            raise ValueError("duration_minutes is required.")
        return positive_int("duration_minutes", value, MAX_DURATION)

    def __repr__(self):
        return f"<Workout {self.id}: {self.date} ({self.duration_minutes} min)>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="unique_workout_exercise"),
        CheckConstraint(
            "reps IS NOT NULL OR duration_seconds IS NOT NULL",
            name="reps_or_duration_required",
        ),
        CheckConstraint("reps IS NULL OR reps > 0", name="reps_positive"),
        CheckConstraint("sets IS NULL OR sets > 0", name="sets_positive"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="duration_seconds_positive",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Relationships
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps")
    def validate_reps(self, key, value):
        return positive_int("reps", value, maximum=10_000)

    @validates("sets")
    def validate_sets(self, key, value):
        return positive_int("sets", value, maximum=1_000)

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        return positive_int("duration_seconds", value, maximum=24 * 60 * 60)

    def __repr__(self):
        return f"<WorkoutExercise {self.id}: workout={self.workout_id} exercise={self.exercise_id}>"
