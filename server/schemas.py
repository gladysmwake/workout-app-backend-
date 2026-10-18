from marshmallow import Schema, ValidationError, fields, validate, validates_schema


def not_blank(value):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Field cannot be blank.")


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=100), not_blank],
    )
    category = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=50), not_blank],
    )
    equipment_needed = fields.Bool(load_default=False)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(
        strict=True,
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=10_000),
    )
    sets = fields.Int(
        strict=True,
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=1_000),
    )
    duration_seconds = fields.Int(
        strict=True,
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=24 * 60 * 60),
    )

    @validates_schema
    def validate_reps_or_duration(self, data, **kwargs):
        if data.get("reps") is None and data.get("duration_seconds") is None:
            raise ValidationError("Provide at least one of 'reps' or 'duration_seconds'.")


class WorkoutExerciseDetailSchema(WorkoutExerciseSchema):
    exercise = fields.Nested(ExerciseSchema, dump_only=True)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1, max=24 * 60),
    )
    notes = fields.Str(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=2000),
    )


class WorkoutDetailSchema(WorkoutSchema):
    workout_exercises = fields.Nested(
        WorkoutExerciseDetailSchema,
        many=True,
        dump_only=True,
        exclude=("workout_id",),
    )


class ExerciseDetailSchema(ExerciseSchema):
    workouts = fields.Nested(WorkoutSchema, many=True, dump_only=True)


# Schema instances for convenient import
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()

workout_exercise_schema = WorkoutExerciseSchema()
workout_exercise_detail_schema = WorkoutExerciseDetailSchema()
